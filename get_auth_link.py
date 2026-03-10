#!/usr/bin/env python3
import sys
import os

project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env')

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
]

flow = InstalledAppFlow.from_client_secrets_file('config/client_secret.json', SCOPES)
auth_url, _ = flow.authorization_url(prompt='consent')

print("\n" + "="*70)
print("AUTHORIZATION LINK")
print("="*70)
print(f"\n{auth_url}\n")
print("="*70)
print("\nSteps:")
print("1. Click the link above (or copy/paste in browser)")
print("2. Sign in with: fkozina92@gmail.com")
print("3. Click ALLOW")
print("4. Copy the authorization code")
print("5. Paste it in the next step")
print("="*70 + "\n")
