#!/usr/bin/env python3
"""
Reauthorize YouTube (keep existing credentials)
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
    print("REAUTHORIZING YOUTUBE (Keeping existing credentials)")
    print("="*70)

    try:
        from src.youtube.auth_oob import YouTubeAuthOOB

        auth = YouTubeAuthOOB()

        print("\n[STEP 1] Getting authorization URL...")
        print("          This will ask for ALL channel permissions\n")

        # Create flow
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_secrets_file(
            'config/client_secret.json',
            [
                'https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube',
                'https://www.googleapis.com/auth/youtube.force-ssl',
            ]
        )

        # Get authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')

        print("[AUTHORIZE NOW]")
        print("="*70)
        print("\nOpen this link in your browser:")
        print(f"\n  {auth_url}\n")
        print("="*70)

        print("\nSteps:")
        print("  1. Open the link above")
        print("  2. Sign in with fkozina92@gmail.com")
        print("  3. Click ALLOW to authorize")
        print("  4. You'll see an authorization code")
        print("  5. Copy the code and paste it below\n")

        try:
            auth_code = input("Paste your authorization code here: ").strip()
        except KeyboardInterrupt:
            print("\nCancelled")
            return False

        if not auth_code:
            print("No code provided")
            return False

        print(f"\nExchanging code for credentials...")
        credentials = flow.fetch_token(code=auth_code)

        # Save credentials
        import pickle
        with open('config/youtube_credentials.pickle', 'wb') as f:
            pickle.dump(credentials, f)

        print("[OK] Credentials updated!")

        # Now check channels
        print("\n[CHECKING] Your YouTube channels...")
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', credentials=credentials)

        request = youtube.channels().list(part='snippet,statistics', mine=True, maxResults=50)
        response = request.execute()

        channels = response.get('items', [])

        if not channels:
            print("[INFO] No channels found")
            return False

        print(f"\n[OK] Found {len(channels)} channel(s):\n")

        for i, ch in enumerate(channels, 1):
            title = ch['snippet']['title']
            channel_id = ch['id']
            subs = ch['statistics'].get('subscriberCount', '0')
            views = ch['statistics'].get('viewCount', '0')

            print(f"  {i}. {title}")
            print(f"     ID: {channel_id}")
            print(f"     Subscribers: {subs}")
            print(f"     Views: {views}\n")

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
        print("DONE! Your channels are now accessible")
        print("\nNow you can:")
        print("  python3 run_full_pipeline_demo.py")
    else:
        print("Authorization failed")
    print("="*70)

    sys.exit(0 if success else 1)
