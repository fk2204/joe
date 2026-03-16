#!/usr/bin/env python3
"""
YouTube OAuth Authentication Setup (Better Version)

This uses the auth.py module which:
1. Tries automatic local server first (no config needed)
2. Falls back to manual OOB if needed

Run this ONCE to set up credentials, then you can upload videos.

Usage:
    python authenticate_youtube.py
"""

import sys
import os

project_dir = '/root/fk2204-repos/youtube-automation'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

from pathlib import Path
from src.youtube.auth import YouTubeAuth
from src.utils.error_handler import OAuthError, ConfigError


def main():
    print("\n" + "="*70)
    print("YOUTUBE OAUTH AUTHENTICATION")
    print("="*70)

    # Check if credentials already exist
    creds_file = "config/youtube_credentials.pickle"
    if os.path.exists(creds_file):
        print(f"\n[OK] Credentials already exist: {creds_file}")
        print("     You can now run: python batch_upload_all_channels.py")
        return True

    print("\n[STEP 1] Starting authentication process...")
    print("         This is a ONE-TIME setup for all 4 channels")

    try:
        auth = YouTubeAuth()

        print("\n[STEP 2] Authenticating with YouTube...")
        print("         (Browser may open automatically, or you'll see a link to open)")

        service = auth.get_authenticated_service()

        print("\n" + "="*70)
        print("SUCCESS! Credentials saved.")
        print("="*70)
        print("\nYou can now run:")
        print("  python batch_upload_all_channels.py")
        print("\nThis will upload your video to all 4 channels as PUBLIC.")

        return True

    except (OAuthError, ConfigError) as e:
        # Show user-friendly message
        e.show_user_message()
        e.log_details()
        return False
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have client_secret.json in config/")
        print("2. Make sure your Google Cloud project has YouTube Data API v3 enabled")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
