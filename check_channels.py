#!/usr/bin/env python3
"""
Check what YouTube channels your account has access to
"""

import sys
import os

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

def main():
    print("\n" + "="*70)
    print("CHECKING YOUTUBE CHANNELS ACCESS")
    print("="*70)

    try:
        from src.youtube.auth_oob import YouTubeAuthOOB

        auth = YouTubeAuthOOB()
        youtube = auth.get_authenticated_service()

        print("\n[FETCHING] Your YouTube channels...\n")

        # List all channels
        request = youtube.channels().list(
            part='snippet,statistics',
            mine=True,
            maxResults=50
        )
        response = request.execute()

        channels = response.get('items', [])

        if not channels:
            print("[INFO] No channels found")
            return False

        print(f"[OK] Found {len(channels)} channel(s):\n")

        for i, ch in enumerate(channels, 1):
            channel_id = ch['id']
            title = ch['snippet']['title']
            subs = ch['statistics'].get('subscriberCount', 'N/A')
            views = ch['statistics'].get('viewCount', 'N/A')

            print(f"  {i}. {title}")
            print(f"     ID: {channel_id}")
            print(f"     Subscribers: {subs}")
            print(f"     Total Views: {views}")
            print()

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()

    print("="*70)
    if success:
        print("These are all the channels your account can access")
    else:
        print("Could not fetch channels")
    print("="*70)

    sys.exit(0 if success else 1)
