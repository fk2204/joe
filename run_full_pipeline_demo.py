#!/usr/bin/env python3
"""
Joe Full Pipeline DEMO: Generate > Create > Upload (No AI Keys Needed)

Uses template-based script generation for testing.
"""

import sys
import os

# Change to project directory
project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
import asyncio
from pathlib import Path

load_dotenv('.env')

def main():
    print("\n" + "="*70)
    print("JOE FULL PIPELINE DEMO: GENERATE > CREATE > UPLOAD")
    print("="*70)

    # Step 1: Check YouTube setup
    print("\n[STEP 1] Checking YouTube setup...")
    yt_secret = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'config/client_secret.json')

    if not os.path.exists(yt_secret or ''):
        print(f"[ERROR] YouTube client secret not found at {yt_secret}")
        return

    print(f"[OK] YouTube secret exists: {yt_secret}")

    # Step 2: Generate Script (Template-Based, No AI)
    print("\n[STEP 2] Generating video script (template-based)...")

    script = {
        'title': '5 Ways to Make Passive Income with AI in 2026',
        'hook': 'Wall Street doesnt want you to know these tricks...',
        'duration': 120,
        'description': 'Learn 5 proven ways to generate passive income using AI.',
        'narration': '''
Welcome to Money Blueprints. Today, I'm showing you 5 ways to make passive income with AI.

Number 1: Content Automation. Use AI to write scripts for YouTube videos. Earn $500 to $2,000 per month.

Number 2: Freelance AI Services. Sell AI services on Fiverr. Earn $1,000 to $5,000 per month.

Number 3: Affiliate Income. Recommend AI tools and earn commissions. Earn $200 to $1,000 per month.

Number 4: Digital Products. Create AI-powered tools and sell them online. Earn $100 to $10,000 per month.

Number 5: Consulting. Help businesses implement AI. Earn $2,000 to $10,000 per month.

The best part? You can start with zero investment.

If this video helped you, hit that subscribe button and turn on notifications.

Your financial future starts now.
        '''.strip()
    }

    print(f"[OK] Title: {script['title']}")
    print(f"[OK] Duration: {script['duration']} seconds")
    print(f"[OK] Hook: {script['hook'][:50]}...")

    # Step 3: Generate TTS Audio
    print("\n[STEP 3] Generating audio (TTS - Edge)...")
    try:
        from src.content.tts import TextToSpeech

        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        tts = TextToSpeech(default_voice="en-US-GuyNeural")
        audio_file = str(output_dir / "narration.mp3")

        print(f"   Generating TTS for {len(script['narration'])} characters...")
        asyncio.run(tts.generate(script['narration'], audio_file))

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

        print(f"   Creating {script['duration']}s video at 1920x1080...")
        generator.create_video(
            audio_file=audio_file,
            output_file=video_file,
            title=script['title'],
            subtitle='AI Money Making Guide',
            normalize_audio=True
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

    # Step 4b: Apply Shorts Overlays
    print("\n[STEP 4b] Applying Shorts overlays...")
    try:
        from src.content.graphics_engine import apply_overlays

        overlaid_video_file = str(output_dir / "video_overlaid.mp4")
        apply_overlays(
            input_video=video_file,
            output_video=overlaid_video_file,
            channel_id="money_blueprints",
            script={
                "hook_text": script["hook"],
                "key_benefit": "Earn $500-$10K/month with AI",
                "duration_s": script.get("duration", 45),
            }
        )
        video_file = overlaid_video_file
        size_mb = os.path.getsize(video_file) / 1024 / 1024
        print(f"[OK] Overlaid video: {video_file} ({size_mb:.1f} MB)")

    except Exception as e:
        print(f"[WARN] Overlay failed, uploading without overlays: {e}")
        # Non-fatal: continue with raw video

    # Step 5: Upload to YouTube
    print("\n[STEP 5] Uploading to YouTube...")
    print("   Channel: money_blueprints (Finance)")
    print("   Privacy: unlisted (safe first upload)")
    print("   Note: Browser will open for OAuth consent")

    try:
        from src.youtube.uploader import YouTubeUploader

        uploader = YouTubeUploader()

        result = uploader.upload_video(
            video_file=video_file,
            title=f"{script['title']} #Shorts",
            description=f"{script['description']}\n\nGenerated with Joe - AI Content Automation",
            tags=["#Shorts", "passive income", "AI", "money", "finance", "side hustle"],
            category="education",
            privacy="unlisted"
        )

        if result.get('success'):
            print(f"\n[OK] Upload successful!")
            print(f"  Video URL: {result['video_url']}")
            print(f"  Video ID: {result['video_id']}")
            print(f"\n  NEXT STEPS:")
            print(f"  1. Browser opened for OAuth (may be in background)")
            print(f"  2. Click ALLOW to authorize YouTube access")
            print(f"  3. Go to https://youtube.com/studio to verify upload")
            print(f"  4. Change privacy to PUBLIC when ready")
        else:
            print(f"[ERROR] Upload failed: {result.get('error', 'Unknown error')}")
            if result.get('error_details'):
                print(f"  Details: {result['error_details']}")

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print("\nFiles generated:")
    print(f"  - Audio:  {audio_file}")
    print(f"  - Video:  {video_file}")
    print("\nNext steps:")
    print("  1. Verify video uploaded to YouTube Studio")
    print("  2. Test with real Groq API for AI script generation")
    print("  3. Generate videos for other channels (mind_unlocked, untold_stories)")
    print("  4. Add social media API keys for cross-posting (Twitter, Reddit)")

if __name__ == "__main__":
    main()
