#!/usr/bin/env python3
"""
Manual YouTube OAuth Authentication

This is a workaround for Google Cloud Console redirect_uri issues.
It manually exchanges an authorization code for credentials.
"""

import os
import sys
import json
import pickle
from urllib.parse import urlencode

os.chdir(r'C:\Users\fkozi\joe')
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')


def manual_auth():
    """Manual OAuth flow without needing redirect_uri."""

    print("\n" + "="*70)
    print("MANUAL YOUTUBE AUTHENTICATION")
    print("="*70)

    # Read client credentials
    with open('config/client_secret.json') as f:
        creds = json.load(f)['installed']

    client_id = creds['client_id']
    client_secret = creds['client_secret']

    # Build authorization URL
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl",
    ]

    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': ' '.join(scopes),
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'access_type': 'offline',
        'prompt': 'consent',
    }

    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(auth_params)}"

    print("\n[STEP 1] Open this link in your browser:")
    print(f"\n{auth_url}\n")

    print("[STEP 2] Sign in with: fkozina92@gmail.com")
    print("[STEP 3] Click 'Allow'")
    print("[STEP 4] Copy the authorization code shown")
    print("[STEP 5] Paste it below:\n")

    auth_code = input("Authorization code: ").strip()

    if not auth_code:
        print("[ERROR] No code provided")
        return False

    # Exchange code for token
    print("\n[Exchanging authorization code for credentials...]")

    import requests

    token_params = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code',
    }

    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_params,
            timeout=10
        )
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Token exchange failed: {e}")
        return False

    token_data = response.json()

    if 'error' in token_data:
        print(f"[ERROR] {token_data.get('error_description', token_data['error'])}")
        return False

    print("[OK] Token received!")

    # Save credentials
    creds_file = 'config/youtube_credentials.pickle'
    os.makedirs(os.path.dirname(creds_file), exist_ok=True)

    with open(creds_file, 'wb') as f:
        pickle.dump(token_data, f)

    print(f"[OK] Credentials saved to {creds_file}")
    print("\n" + "="*70)
    print("SUCCESS! You can now upload videos.")
    print("="*70)
    print("\nRun: python upload_to_all_channels.py")

    return True


if __name__ == "__main__":
    success = manual_auth()
    sys.exit(0 if success else 1)
