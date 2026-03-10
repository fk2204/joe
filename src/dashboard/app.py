"""
Joe Analytics Dashboard - Streamlit MVP

Simple, fast analytics dashboard for YouTube Shorts performance.
Run: streamlit run src/dashboard/app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.analytics.analytics_db import AnalyticsDB

st.set_page_config(page_title="Joe Analytics", layout="wide")

# Initialize database
db = AnalyticsDB()

st.title("📊 Joe Analytics Dashboard")
st.markdown("Track your YouTube Shorts performance across all 4 channels")

# Sidebar: Channel selector
st.sidebar.header("Settings")
channels = ["money_blueprints", "mind_unlocked", "neural_forge", "prof8ssor_ai"]
selected_channel = st.sidebar.selectbox("Select Channel", channels)

# Get channel summary
summary = db.get_channel_summary(selected_channel)

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Videos", summary["video_count"])

with col2:
    st.metric("Total Views", f"{summary['total_views']:,.0f}")

with col3:
    st.metric("Avg CTR", f"{summary['avg_ctr']:.2%}")

with col4:
    st.metric("Estimated Revenue", f"${summary['total_revenue']:.2f}")

st.divider()

# Display message if no data
if summary["video_count"] == 0:
    st.info(f"No analytics data yet for {selected_channel}")
    st.markdown("""
    ### Getting Started
    1. Run: `python batch_upload_all_channels.py`
    2. Wait 24 hours for YouTube Analytics to populate
    3. Refresh this dashboard to see your metrics
    """)
else:
    st.success(f"✓ Tracking {summary['video_count']} videos on {selected_channel}")

st.markdown("""
---
## Next Steps

**Week 1**: Analytics Dashboard ✓ (You are here)
**Week 2**: Add A/B Testing System
**Week 3**: Add Performance Monitoring & Alerts
**Week 4**: Add Trending Topics Research
**Week 5**: Add Revenue Projection
""")
