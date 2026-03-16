#!/usr/bin/env python3
"""
Headless YouTube OAuth Helper

Starts a temporary HTTP server on port 8080 to receive the OAuth callback.
Open the printed URL in your browser, authorize, and the credentials are saved automatically.
"""
import os, sys, json, pickle, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

os.chdir('/root/fk2204-repos/youtube-automation')
sys.path.insert(0, '.')

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

PORT = 8080
REDIRECT_URI = f"http://187.77.7.117:{PORT}"

class CallbackHandler(BaseHTTPRequestHandler):
    code = None
    
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if 'code' in query:
            CallbackHandler.code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Authorization successful!</h1><p>You can close this tab. Go back to the terminal.</p>')
        else:
            self.send_response(400)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            error = query.get('error', ['unknown'])[0]
            self.wfile.write(f'<h1>Error: {error}</h1>'.encode())
        
    def log_message(self, format, *args):
        pass  # Silence logs

# Create flow with our redirect URI
flow = Flow.from_client_secrets_file('config/client_secret.json', scopes=SCOPES)
flow.redirect_uri = REDIRECT_URI

auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')

print("\n" + "="*70)
print("YOUTUBE OAUTH SETUP")
print("="*70)
print(f"\nOpen this URL in your browser:\n")
print(auth_url)
print(f"\nWaiting for authorization on port {PORT}...")
print("="*70)

# Start server
server = HTTPServer(('0.0.0.0', PORT), CallbackHandler)
server.timeout = 300  # 5 min timeout

while CallbackHandler.code is None:
    server.handle_request()

server.server_close()

# Exchange code for credentials
print("\nGot authorization code! Exchanging for credentials...")
flow.fetch_token(code=CallbackHandler.code)
credentials = flow.credentials

# Save as pickle (compatible with existing code)
with open('config/youtube_credentials.pickle', 'wb') as f:
    pickle.dump(credentials, f)

print("\n✅ Credentials saved to config/youtube_credentials.pickle")
print("You can now run: python batch_upload_all_channels.py")
