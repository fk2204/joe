#!/usr/bin/env python3
"""
Verify YouTube OAuth Setup
Checks if everything is configured correctly in Google Cloud Console
"""

import sys
import os
import json

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

def check_oauth_setup():
    print("\n" + "="*70)
    print("YOUTUBE OAUTH SETUP VERIFICATION")
    print("="*70)

    all_good = True

    # Check 1: Client Secret File
    print("\n[CHECK 1] Client secret file...")
    if os.path.exists('config/client_secret.json'):
        print("  [OK] File exists: config/client_secret.json")

        with open('config/client_secret.json', 'r') as f:
            secret = json.load(f)

        if 'web' in secret:
            print("  [OK] Type: Web application")
            web = secret['web']
            print(f"  [OK] Client ID: {web['client_id'][:20]}...")
            print(f"  [OK] Project: {web.get('project_id', 'unknown')}")
        elif 'installed' in secret:
            print("  [OK] Type: Desktop application (installed)")
        else:
            print("  [WARNING] Unknown OAuth type")

    else:
        print("  [ERROR] File not found: config/client_secret.json")
        print("  ACTION: Download from Google Cloud Console")
        all_good = False

    # Check 2: Credentials Storage
    print("\n[CHECK 2] Credentials storage...")
    if not os.path.exists('config/credentials'):
        print("  [INFO] Directory doesn't exist (will be created)")
    else:
        files = os.listdir('config/credentials')
        if files:
            print(f"  [OK] Found cached credentials: {files}")
        else:
            print("  [INFO] No cached credentials (first login needed)")

    # Check 3: Environment Variables
    print("\n[CHECK 3] Environment variables...")
    from dotenv import load_dotenv
    load_dotenv('.env')

    yt_secret = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE')
    yt_id = os.getenv('YOUTUBE_CLIENT_ID')

    if yt_secret:
        print(f"  [OK] YOUTUBE_CLIENT_SECRETS_FILE={yt_secret}")
    else:
        print("  [WARNING] YOUTUBE_CLIENT_SECRETS_FILE not set in .env")

    if yt_id:
        print(f"  [OK] YOUTUBE_CLIENT_ID={yt_id[:20]}...")
    else:
        print("  [WARNING] YOUTUBE_CLIENT_ID not set in .env")

    # Check 4: Google Auth Libraries
    print("\n[CHECK 4] Google auth libraries...")
    try:
        import google.auth
        print("  [OK] google.auth installed")
    except ImportError:
        print("  [ERROR] google.auth not installed")
        print("  FIX: pip install google-auth-oauthlib google-api-python-client")
        all_good = False

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        print("  [OK] google_auth_oauthlib installed")
    except ImportError:
        print("  [ERROR] google_auth_oauthlib not installed")
        all_good = False

    try:
        from googleapiclient.discovery import build
        print("  [OK] google-api-python-client installed")
    except ImportError:
        print("  [ERROR] google-api-python-client not installed")
        all_good = False

    # Check 5: Network Connectivity
    print("\n[CHECK 5] Network connectivity...")
    try:
        import socket
        socket.create_connection(("accounts.google.com", 443), timeout=5)
        print("  [OK] Can reach Google OAuth servers")
    except Exception as e:
        print(f"  [ERROR] Cannot reach Google: {e}")
        all_good = False

    # Check 6: Port Availability
    print("\n[CHECK 6] Port availability...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 8080))
        sock.close()
        print("  [OK] Port 8080 is available")
    except OSError:
        print("  [WARNING] Port 8080 is in use")
        print("  Note: Will try auto-selecting another port")

    # Summary
    print("\n" + "="*70)
    if all_good:
        print("RESULT: Setup looks good!")
        print("="*70)
        print("\nNow run:")
        print("  python3 test_youtube_oauth.py")
        print("\nIf you get redirect_uri_mismatch error:")
        print("  Read: docs/YOUTUBE_OAUTH_FIX.md")
    else:
        print("RESULT: Some issues need fixing")
        print("="*70)
        print("\nSee [ERROR] and [FIX] messages above")

if __name__ == "__main__":
    check_oauth_setup()
