#!/usr/bin/env python3
"""
Simple YouTube Upload - Uses existing video + OOB OAuth
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
    print("UPLOAD TO YOUTUBE (Using OOB OAuth)")
    print("="*70)

    # Check if video exists
    print("\n[CHECK] Looking for video file...")
    video_file = 'output/video.mp4'

    if not os.path.exists(video_file):
        print(f"[ERROR] Video not found: {video_file}")
        print(f"        Run: python3 run_full_pipeline_demo.py")
        return False

    size_mb = os.path.getsize(video_file) / 1024 / 1024
    print(f"[OK] Found: {video_file} ({size_mb:.1f} MB)")

    # Get YouTube service with OOB auth
    print("\n[STEP 1] Authenticating with YouTube (OOB flow)...")
    print("          Browser will open - you authorize manually")

    try:
        from src.youtube.auth_oob import YouTubeAuthOOB

        auth = YouTubeAuthOOB()
        youtube = auth.get_authenticated_service()

        print(f"[OK] Authenticated!")

    except KeyboardInterrupt:
        print(f"[CANCELLED] User cancelled")
        return False
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Upload to YouTube
    print("\n[STEP 2] Uploading video to YouTube...")
    print(f"          File: {video_file}")
    print(f"          Title: 5 Ways to Make Passive Income with AI in 2026")

    try:
        request_body = {
            'snippet': {
                'title': '5 Ways to Make Passive Income with AI in 2026',
                'description': 'Learn 5 proven ways to make passive income with AI. Setup cost: $0. Time to first $100: 2-4 weeks.',
                'tags': ['passive income', 'AI', 'money', 'finance', 'tutorial'],
                'categoryId': '22'  # 22 = education
            },
            'status': {
                'privacyStatus': 'unlisted'  # unlisted = not public, but viewable
            }
        }

        # Upload
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
        print(f"     Video ID: {video_id}")
        print(f"     URL: {video_url}")
        print(f"\n     Next steps:")
        print(f"     1. Go to https://youtube.com/studio")
        print(f"     2. Check your 'Uploads' tab")
        print(f"     3. When ready, change privacy to PUBLIC")
        print(f"     4. Share the link: {video_url}")

        return True

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()

    print("\n" + "="*70)
    if success:
        print("RESULT: Video uploaded successfully!")
    else:
        print("RESULT: Upload failed or cancelled")
    print("="*70)

    sys.exit(0 if success else 1)
