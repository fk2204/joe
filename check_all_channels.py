#!/usr/bin/env python3
"""
Check ALL YouTube channels including brand accounts
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
    print("CHECKING ALL YOUTUBE CHANNELS (including brand accounts)")
    print("="*70)

    try:
        from src.youtube.auth_oob import YouTubeAuthOOB

        auth = YouTubeAuthOOB()
        youtube = auth.get_authenticated_service()

        all_channels = []

        # 1. Get primary channel (mine=True)
        print("\n[1] Fetching PRIMARY channel...")
        request = youtube.channels().list(
            part='snippet,statistics',
            mine=True,
            maxResults=50
        )
        response = request.execute()
        primary = response.get('items', [])
        all_channels.extend(primary)
        print(f"    Found: {len(primary)} primary channel(s)")

        # 2. Get brand accounts (secondary channels)
        print("\n[2] Fetching BRAND ACCOUNTS (secondary channels)...")
        try:
            request = youtube.channels().list(
                part='snippet,statistics',
                managedByMe=True,
                maxResults=50
            )
            response = request.execute()
            secondary = response.get('items', [])
            all_channels.extend(secondary)
            print(f"    Found: {len(secondary)} secondary channel(s)")
        except Exception as e:
            print(f"    Note: {e}")

        # Remove duplicates
        seen = set()
        unique_channels = []
        for ch in all_channels:
            ch_id = ch['id']
            if ch_id not in seen:
                seen.add(ch_id)
                unique_channels.append(ch)

        if not unique_channels:
            print("\n[ERROR] No channels found")
            return False

        print(f"\n[OK] TOTAL: {len(unique_channels)} channel(s):\n")

        for i, ch in enumerate(unique_channels, 1):
            channel_id = ch['id']
            title = ch['snippet']['title']
            subs = ch['statistics'].get('subscriberCount', '0')
            views = ch['statistics'].get('viewCount', '0')

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
        print("These are ALL your YouTube channels")
    else:
        print("Could not fetch channels")
    print("="*70)

    sys.exit(0 if success else 1)
