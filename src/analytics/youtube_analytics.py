"""
YouTube Analytics API Integration

Fetches watch time, CTR, views, and other metrics for videos.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError("Install: pip install google-api-python-client")


class YouTubeAnalyticsAPI:
    """Fetch YouTube Analytics data for owned channels."""

    API_SERVICE_NAME = "youtubeAnalytics"
    API_VERSION = "v2"

    def __init__(self, credentials):
        """
        Initialize with OAuth credentials.
        
        Args:
            credentials: Google OAuth credentials from YouTubeAuth
        """
        self.service = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
        self.metrics = [
            "views",
            "redisLikes",
            "redisUnlikes", 
            "estimatedRevenue",
            "adImpressionsPercent",
            "averageViewDuration",
            "watchTimeMinutes",
        ]

    def get_channel_analytics(
        self, channel_id: str, days_back: int = 28
    ) -> Dict:
        """
        Get analytics for a channel over the last N days.
        
        Args:
            channel_id: YouTube channel ID
            days_back: Number of days of history to fetch
            
        Returns:
            Dict with daily metrics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            request = self.service.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date.strftime("%Y-%m-%d"),
                endDate=end_date.strftime("%Y-%m-%d"),
                metrics=",".join(self.metrics),
                dimensions="day",
                maxResults=500,
            )
            response = request.execute()

            return self._parse_response(response)

        except HttpError as e:
            logger.error(f"YouTube Analytics API error: {e}")
            return {}

    def get_video_analytics(
        self, channel_id: str, video_id: str, days_back: int = 28
    ) -> Dict:
        """
        Get analytics for a specific video.
        
        Args:
            channel_id: YouTube channel ID
            video_id: Video ID
            days_back: Days of history
            
        Returns:
            Dict with video metrics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            request = self.service.reports().query(
                ids=f"channel=={channel_id}",
                filters=f"video=={video_id}",
                startDate=start_date.strftime("%Y-%m-%d"),
                endDate=end_date.strftime("%Y-%m-%d"),
                metrics=",".join(self.metrics),
                maxResults=500,
            )
            response = request.execute()

            data = self._parse_response(response)
            
            # Aggregate to single row
            if "rows" in data and data["rows"]:
                agg = {col: 0 for col in data["columnHeaders"]}
                for row in data["rows"]:
                    for i, col in enumerate(data["columnHeaders"]):
                        try:
                            agg[col] += float(row[i]) if isinstance(row[i], (int, float)) else 0
                        except (ValueError, TypeError):
                            pass
                return agg
            
            return {}

        except HttpError as e:
            logger.error(f"YouTube Analytics API error: {e}")
            return {}

    def _parse_response(self, response: Dict) -> Dict:
        """Parse YouTube Analytics API response."""
        if "rows" not in response:
            return {}

        result = {
            "columnHeaders": [col["name"] for col in response["columnHeaders"]],
            "rows": response["rows"],
        }
        return result

    def get_ctr(self, analytics: Dict) -> Optional[float]:
        """Calculate CTR (impressions → clicks) from analytics."""
        if not analytics or "adImpressionsPercent" not in analytics:
            return None
        return float(analytics.get("adImpressionsPercent", 0)) / 100

    def get_avg_watch_duration(self, analytics: Dict) -> Optional[float]:
        """Get average view duration in seconds."""
        if not analytics or "averageViewDuration" not in analytics:
            return None
        return float(analytics.get("averageViewDuration", 0))

    def get_revenue(self, analytics: Dict) -> Optional[float]:
        """Get estimated revenue in USD."""
        if not analytics or "estimatedRevenue" not in analytics:
            return None
        return float(analytics.get("estimatedRevenue", 0))
