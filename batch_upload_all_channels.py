#!/usr/bin/env python3
"""
Batch upload Shorts to all 4 channels (public)
"""

import sys
import os
import json
import subprocess

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

def upload_to_channel(channel_name, video_file):
    """Upload video to a specific channel"""
    print(f"\n{'='*70}")
    print(f"UPLOADING TO: {channel_name}")
    print(f"{'='*70}")

    try:
        from src.youtube.auth import YouTubeAuth

        # Load channels config
        with open('config/channels_config.json', 'r') as f:
            config = json.load(f)

        # Find the channel
        selected = None
        for ch in config['channels']:
            if ch['name'] == channel_name:
                selected = ch
                break

        if not selected:
            print(f"[ERROR] Channel {channel_name} not found")
            return False

        print(f"[OK] Selected: {selected['name']}")

        # Check video exists
        if not os.path.exists(video_file):
            print(f"[ERROR] Video not found: {video_file}")
            return False

        size_mb = os.path.getsize(video_file) / 1024 / 1024
        print(f"[OK] Found: {video_file} ({size_mb:.1f} MB)")

        # Authenticate
        print(f"\n[AUTHENTICATING] YouTube...")
        auth = YouTubeAuth()
        youtube = auth.get_authenticated_service()
        print(f"[OK] Authenticated!")

        # Upload
        print(f"\n[UPLOADING] to {selected['name']} (PUBLIC)...")

        request_body = {
            'snippet': {
                'title': f"AI Money Secrets - {selected['niche'].replace('_', ' ').title()} #Shorts",
                'description': f"{selected['description']}\n\nGenerated with Joe - AI Content Automation",
                'tags': ['#Shorts', 'AI', 'money', 'tutorial', selected['niche']],
                'categoryId': '22'  # Education
            },
            'status': {
                'privacyStatus': 'public'  # PUBLIC - NOT UNLISTED
            }
        }

        request = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=video_file
        )

        print(f"[UPLOADING...] This may take 1-2 minutes...")
        response = request.execute()

        video_id = response['id']
        video_url = f'https://youtu.be/{video_id}'

        print(f"\n[OK] UPLOAD SUCCESSFUL!")
        print(f"     Channel: {selected['name']}")
        print(f"     Video URL: {video_url}")
        print(f"     Status: PUBLIC (live now)")

        return True

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("BATCH UPLOAD TO ALL 4 CHANNELS")
    print("="*70)

    # Video file - use overlaid if available, otherwise use raw video
    video_file = 'output/video_overlaid.mp4'
    if not os.path.exists(video_file):
        video_file = 'output/video.mp4'

    if not os.path.exists(video_file):
        print(f"[ERROR] Video not found: output/video.mp4 or output/video_overlaid.mp4")
        print(f"        Run: python3 run_full_pipeline_demo.py")
        return False

    # Upload to each channel
    channels = ['money_blueprints', 'mind_unlocked', 'neural_forge', 'prof8ssor_ai']
    results = {}

    for i, channel in enumerate(channels, 1):
        print(f"\n[{i}/{len(channels)}] Processing {channel}...")
        success = upload_to_channel(channel, video_file)
        results[channel] = success

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)

    for channel, success in results.items():
        status = "[OK]" if success else "[FAILED]"
        print(f"{status} {channel}")

    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{len(channels)} uploaded successfully")

    return all(results.values())


if __name__ == "__main__":
    success = main()

    print("\n" + "="*70)
    if success:
        print("All channels uploaded!")
        print("Check YouTube Studio to verify videos are public and live")
    else:
        print("Some uploads failed. Check logs above.")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
