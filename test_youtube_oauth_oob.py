#!/usr/bin/env python3
"""
Test YouTube OAuth with Out-of-Band (OOB) Flow
No redirect URI needed - manual authorization
"""

import sys
import os

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

def test_oauth_oob():
    print("\n" + "="*70)
    print("YOUTUBE OAUTH - OUT-OF-BAND FLOW (No Redirect URI Needed)")
    print("="*70)

    # Step 1: Check credentials file
    print("\n[STEP 1] Checking credential files...")

    yt_secret = 'config/client_secret.json'
    print(f"  Looking for: {yt_secret}")

    if not os.path.exists(yt_secret):
        print(f"  [ERROR] Not found!")
        return False

    print(f"  [OK] Found")

    # Step 2: Create credentials directory
    print("\n[STEP 2] Preparing storage...")
    cred_dir = 'config/credentials'
    if not os.path.exists(cred_dir):
        os.makedirs(cred_dir)
        print(f"  [OK] Created: {cred_dir}")
    else:
        print(f"  [OK] Exists: {cred_dir}")

    # Step 3: Test OOB auth
    print("\n[STEP 3] Starting Out-of-Band authentication...")

    try:
        from src.youtube.auth_oob import YouTubeAuthOOB

        print(f"  [OK] Imported YouTubeAuthOOB")

        auth = YouTubeAuthOOB(
            client_secrets_file='config/client_secret.json'
        )
        print(f"  [OK] Created auth instance")

    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Get credentials (this will prompt for authorization)
    print("\n[STEP 4] Getting credentials...")

    try:
        credentials = auth.get_credentials()

        if credentials:
            print(f"  [OK] Credentials obtained!")

            # Step 5: Get YouTube service
            print("\n[STEP 5] Getting YouTube API service...")
            youtube = auth.get_authenticated_service()

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
                            cid = ch['id']
                            print(f"       - {name} (ID: {cid})")
                    else:
                        print(f"  [INFO] No channels found")

                except Exception as e:
                    print(f"  [ERROR] Failed to list channels: {e}")

            return True

        else:
            print(f"  [ERROR] No credentials returned")
            return False

    except KeyboardInterrupt:
        print(f"\n  [CANCELLED] Authorization cancelled by user")
        return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oauth_oob()

    print("\n" + "="*70)
    if success:
        print("RESULT: YouTube OAuth is working!")
        print("="*70)
        print("\nYou can now run the full pipeline:")
        print("  python3 run_full_pipeline_demo.py")
    else:
        print("RESULT: Authorization incomplete or failed")
        print("="*70)

    sys.exit(0 if success else 1)
