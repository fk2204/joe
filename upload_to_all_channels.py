#!/usr/bin/env python3
"""
Complete Upload Workflow - Authentication + Generation + Distribution

Handles the full workflow in one command:
1. Authenticates with YouTube (if not already authenticated)
2. Generates a new video with graphics overlays
3. Uploads to all 4 channels as PUBLIC

Usage:
    python upload_to_all_channels.py
"""

import sys
import os
import subprocess

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

from pathlib import Path


def run_step(step_num, step_name, command):
    """Run a step and report results."""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {step_name}")
    print(f"{'='*70}")

    try:
        result = subprocess.run([sys.executable, command], check=True)
        print(f"\n[OK] Step {step_num} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Step {step_num} failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Step {step_num} error: {e}")
        return False


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("\n" + "="*70)
    print("PREREQUISITE CHECK")
    print("="*70)

    issues = []

    # Check client_secret.json
    if not os.path.exists('config/client_secret.json'):
        issues.append(
            "client_secret.json not found. See UPLOAD_GUIDE.md for setup instructions."
        )

    # Check channels config
    if not os.path.exists('config/channels_config.json'):
        issues.append("channels_config.json not found")

    if issues:
        print("\n[ERROR] Prerequisites not met:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print("\n[OK] All prerequisites met")
    return True


def main():
    print("\n" + "="*70)
    print("COMPLETE UPLOAD WORKFLOW")
    print("="*70)
    print("""
This script will:
1. Authenticate with YouTube (one-time setup)
2. Generate a new AI video with graphics overlays
3. Upload to all 4 channels as PUBLIC

Estimated time: 5-10 minutes
(First run may take longer due to authentication)
""")

    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n[STOPPING] Fix the issues above and try again")
        return False

    # Step 2: Authenticate
    print("\nChecking YouTube authentication...")
    if not os.path.exists('config/youtube_credentials.pickle'):
        print("[NEEDED] YouTube credentials not found")
        if not run_step(1, "YouTube Authentication", "authenticate_youtube.py"):
            return False
    else:
        print("[OK] YouTube credentials already cached")

    # Step 3: Generate video
    if not run_step(2, "Generate Video with Graphics", "run_full_pipeline_demo.py"):
        print("\n[ERROR] Video generation failed. Stopping before upload.")
        return False

    # Step 4: Batch upload
    if not run_step(3, "Upload to All 4 Channels", "batch_upload_all_channels.py"):
        print("\n[ERROR] Upload failed")
        return False

    # Success!
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE!")
    print("="*70)
    print("""
Your video has been:
✓ Generated with AI script
✓ Rendered with professional graphics overlays
✓ Uploaded to all 4 channels as PUBLIC

Channels uploaded to:
  1. money_blueprints (Finance niche)
  2. mind_unlocked (Psychology niche)
  3. neural_forge (AI/Tech niche)
  4. prof8ssor_ai (AI Tutorials niche)

Next:
- Go to https://studio.youtube.com
- Check that videos appear in all 4 channels
- Videos should be live in Shorts feed immediately

For more information, see: UPLOAD_GUIDE.md
""")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
