#!/usr/bin/env python3
"""
Joe Full Pipeline: Generate > Create > Upload

Generates a video script, creates a video, and uploads to YouTube.
"""

import sys
import os
sys.path.insert(0, '/c/Users/fkozi/joe')

from dotenv import load_dotenv
import asyncio
from pathlib import Path

# Load environment variables
load_dotenv('/c/Users/fkozi/joe/.env')

def main():
    print("\n" + "="*70)
    print("JOE FULL PIPELINE: GENERATE > CREATE > UPLOAD")
    print("="*70)

    # Step 1: Check environment
    print("\n[STEP 1] Checking environment...")
    groq_key = os.getenv('GROQ_API_KEY', '').replace('gsk_', 'gsk_***')
    yt_secret = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE')

    if not os.getenv('GROQ_API_KEY'):
        print("[ERROR] GROQ_API_KEY not configured")
        print("   Set in .env: GROQ_API_KEY=gsk_...")
        return

    if not os.path.exists(yt_secret or ''):
        print(f"[ERROR] YouTube client secret not found at {yt_secret}")
        return

    print(f"[OK] GROQ API configured: {groq_key}")
    print(f"[OK] YouTube secret exists: {yt_secret}")

    # Step 2: Generate Script
    print("\n[STEP 2] Generating video script...")
    try:
        from src.content.script_writer import ScriptWriter

        writer = ScriptWriter(provider="groq")
        script = writer.generate_script(
            topic="5 Ways to Make Passive Income with AI",
            duration_minutes=2,
            niche="finance"
        )

        print(f"[OK] Title: {script.title}")
        print(f"[OK] Duration: {script.duration} seconds")
        print(f"[OK] Hook: {script.hook[:60]}...")

    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Generate TTS Audio
    print("\n[STEP 3] Generating audio (TTS)...")
    try:
        from src.content.tts import TextToSpeech

        output_dir = Path('/c/Users/fkozi/joe/output')
        output_dir.mkdir(exist_ok=True)

        tts = TextToSpeech(default_voice="en-US-GuyNeural")
        narration = writer.get_full_narration(script)
        audio_file = str(output_dir / "narration.mp3")

        # Run async TTS
        asyncio.run(tts.generate(narration, audio_file))

        if os.path.exists(audio_file):
            size_mb = os.path.getsize(audio_file) / 1024 / 1024
            print(f"[OK] Audio generated: {audio_file} ({size_mb:.1f} MB)")
        else:
            print(f"[ERROR] Audio file not created")
            return

    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Create Video
    print("\n[STEP 4] Creating video...")
    try:
        from src.content.video_fast import FastVideoGenerator

        generator = FastVideoGenerator()
        video_file = str(output_dir / "video.mp4")

        generator.create_video(
            audio_file=audio_file,
            output_file=video_file,
            title=script.title,
            duration=script.duration
        )

        if os.path.exists(video_file):
            size_mb = os.path.getsize(video_file) / 1024 / 1024
            print(f"[OK] Video created: {video_file} ({size_mb:.1f} MB)")
        else:
            print(f"[ERROR] Video file not created")
            return

    except Exception as e:
        print(f"[ERROR] Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 5: Upload to YouTube
    print("\n[STEP 5] Uploading to YouTube...")
    print("   Channel: money_blueprints (Finance)")
    print("   Privacy: unlisted (safe first upload)")
    print("   Browser will open for OAuth consent on first upload")

    try:
        from src.youtube.uploader import YouTubeUploader

        uploader = YouTubeUploader(channel_id="money_blueprints")

        result = uploader.upload_video(
            video_file=video_file,
            title=script.title,
            description=f"{script.description}\n\nGenerated with Joe - AI Content Automation",
            tags=["passive income", "AI", "money", "finance", "side hustle"],
            category="education",
            privacy="unlisted"  # Safe for first test
        )

        if result.get('success'):
            print(f"\n[OK] Upload successful!")
            print(f"  Video URL: {result['video_url']}")
            print(f"  Video ID: {result['video_id']}")
            print(f"\n  Browser should have opened for OAuth consent.")
            print(f"  If not, manually visit: https://youtu.be/{result['video_id']}")
        else:
            print(f"[ERROR] Upload failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Check https://youtube.com/studio (go to Uploads)")
    print("2. Change privacy to PUBLIC when ready")
    print("3. Run again to post to additional channels")
    print("4. Add Twitter/Reddit API keys for cross-posting")

if __name__ == "__main__":
    main()
