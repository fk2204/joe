"""
Analytics Data Storage

MVP: SQLite (will migrate to PostgreSQL for scale)
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger


class AnalyticsDB:
    """SQLite analytics database for MVP."""

    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                youtube_video_id TEXT UNIQUE NOT NULL,
                channel_id TEXT NOT NULL,
                title TEXT,
                uploaded_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Analytics snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_analytics (
                id INTEGER PRIMARY KEY,
                video_id INTEGER NOT NULL,
                views INTEGER,
                watch_time_minutes INTEGER,
                avg_view_duration_seconds REAL,
                ctr REAL,
                likes INTEGER,
                comments INTEGER,
                estimated_revenue REAL,
                snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(video_id) REFERENCES videos(id)
            )
        """)

        # Channels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                youtube_channel_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Analytics DB initialized: {self.db_path}")

    def add_video(
        self, youtube_video_id: str, channel_id: str, title: str, uploaded_at: str
    ) -> int:
        """Add a video to tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO videos (youtube_video_id, channel_id, title, uploaded_at)
            VALUES (?, ?, ?, ?)
            """,
            (youtube_video_id, channel_id, title, uploaded_at),
        )
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        return video_id

    def record_analytics(self, video_id: int, metrics: Dict):
        """Record analytics snapshot for a video."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO video_analytics 
            (video_id, views, watch_time_minutes, avg_view_duration_seconds, ctr, likes, comments, estimated_revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                metrics.get("views", 0),
                metrics.get("watch_time_minutes", 0),
                metrics.get("avg_view_duration_seconds", 0),
                metrics.get("ctr", 0),
                metrics.get("likes", 0),
                metrics.get("comments", 0),
                metrics.get("estimated_revenue", 0),
            ),
        )
        conn.commit()
        conn.close()

    def get_video_analytics(self, video_id: int, days: int = 28) -> List[Dict]:
        """Get recent analytics for a video."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT views, watch_time_minutes, avg_view_duration_seconds, ctr, likes, 
                   comments, estimated_revenue, snapshot_at
            FROM video_analytics
            WHERE video_id = ?
            ORDER BY snapshot_at DESC
            LIMIT ?
            """,
            (video_id, days),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "views": row[0],
                "watch_time_minutes": row[1],
                "avg_view_duration_seconds": row[2],
                "ctr": row[3],
                "likes": row[4],
                "comments": row[5],
                "estimated_revenue": row[6],
                "snapshot_at": row[7],
            }
            for row in rows
        ]

    def get_channel_summary(self, channel_id: str) -> Dict:
        """Get summary stats for a channel."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) as video_count,
                   SUM(views) as total_views,
                   SUM(watch_time_minutes) as total_watch_time,
                   AVG(ctr) as avg_ctr,
                   SUM(estimated_revenue) as total_revenue
            FROM video_analytics va
            JOIN videos v ON va.video_id = v.id
            WHERE v.channel_id = ?
            """,
            (channel_id,),
        )

        row = cursor.fetchone()
        conn.close()

        return {
            "video_count": row[0] or 0,
            "total_views": row[1] or 0,
            "total_watch_time": row[2] or 0,
            "avg_ctr": row[3] or 0,
            "total_revenue": row[4] or 0,
        }
