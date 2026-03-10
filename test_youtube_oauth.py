#!/usr/bin/env python3
"""
Test YouTube OAuth Connection
"""

import sys
import os

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

def test_oauth():
    print("\n" + "="*70)
    print("YOUTUBE OAUTH CONNECTION TEST")
    print("="*70)

    # Step 1: Check credentials file
    print("\n[STEP 1] Checking credential files...")

    yt_secret = 'config/client_secret.json'
    print(f"  Looking for: {yt_secret}")

    if os.path.exists(yt_secret):
        print(f"  [OK] Found: {os.path.abspath(yt_secret)}")
        with open(yt_secret, 'r') as f:
            content = f.read()
            print(f"  [OK] File size: {len(content)} bytes")
    else:
        print(f"  [ERROR] Not found!")
        return False

    # Step 2: Check credential token directory
    print("\n[STEP 2] Checking credentials storage...")
    cred_dir = 'config/credentials'
    if not os.path.exists(cred_dir):
        os.makedirs(cred_dir)
        print(f"  [OK] Created: {cred_dir}")
    else:
        print(f"  [OK] Exists: {os.path.abspath(cred_dir)}")
        files = os.listdir(cred_dir)
        if files:
            print(f"  [OK] Found {len(files)} credential files:")
            for f in files:
                print(f"       - {f}")
        else:
            print(f"  [INFO] No credential files yet (will be created on first auth)")

    # Step 3: Try to import and test YouTube auth
    print("\n[STEP 3] Testing YouTube auth module...")
    try:
        from src.youtube.auth import YouTubeAuth
        print(f"  [OK] Imported YouTubeAuth")

        # Create auth instance
        auth = YouTubeAuth(
            client_secrets_file='config/client_secret.json'
        )
        print(f"  [OK] Created YouTubeAuth instance")

    except Exception as e:
        print(f"  [ERROR] Failed to import: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Attempt authentication
    print("\n[STEP 4] Attempting OAuth authentication...")
    print("  NOTE: A browser window should open. If it doesn't:")
    print("    - Check if browser is blocked or hidden")
    print("    - Authorization URL will be displayed below")

    try:
        credentials = auth.get_authenticated_service()

        if credentials:
            print(f"  [OK] Authentication successful!")
            print(f"  [OK] Credentials obtained")

            # Get YouTube service
            print("\n[STEP 5] Getting YouTube API service...")
            youtube = auth.get_youtube_service()
            if youtube:
                print(f"  [OK] YouTube service ready!")

                # List channels
                print("\n[STEP 6] Listing authorized channels...")
                try:
                    request = youtube.channels().list(
                        part='snippet',
                        mine=True
                    )
                    response = request.execute()

                    if response.get('items'):
                        print(f"  [OK] Found {len(response['items'])} channel(s):")
                        for ch in response['items']:
                            name = ch['snippet']['title']
                            print(f"       - {name}")
                    else:
                        print(f"  [INFO] No channels found")

                except Exception as e:
                    print(f"  [ERROR] Failed to list channels: {e}")

            return True
        else:
            print(f"  [ERROR] No credentials returned")
            return False

    except Exception as e:
        print(f"  [ERROR] Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oauth()

    print("\n" + "="*70)
    if success:
        print("RESULT: YouTube OAuth is working!")
        print("="*70)
        print("\nYou can now upload videos to YouTube.")
    else:
        print("RESULT: YouTube OAuth needs attention")
        print("="*70)
        print("\nPossible issues:")
        print("  1. Browser didn't open - check if it's blocked")
        print("  2. Client secret file is invalid")
        print("  3. Need to re-download client_secret.json from Google Console")

    sys.exit(0 if success else 1)
