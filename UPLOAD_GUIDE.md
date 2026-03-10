# YouTube Upload Guide for Joe

## Quick Start (3 Steps)

### Step 1: Authenticate with YouTube (ONE TIME ONLY)
```bash
python authenticate_youtube.py
```

This will:
1. Check if you have valid credentials
2. If not, show you a Google authorization link
3. Ask you to open the link in your browser
4. Ask you to paste the authorization code

**What to do:**
- Open the link in your browser
- Sign in with your Gmail (fkozina92@gmail.com)
- Click "Allow" to authorize
- Copy the authorization code
- Paste it into the terminal when prompted

**Note:** This only needs to be done ONCE. After this, credentials are saved and reused.

### Step 2: Generate a Video
```bash
python run_full_pipeline_demo.py
```

This creates `output/video_overlaid.mp4` with:
- AI-generated script
- Text-to-speech narration
- Professional graphics overlays
- YouTube Shorts format (1080x1920)

### Step 3: Upload to All 4 Channels
```bash
python batch_upload_all_channels.py
```

This uploads the same video to all 4 channels as PUBLIC:
- money_blueprints (Finance)
- mind_unlocked (Psychology)
- neural_forge (AI/Tech)
- prof8ssor_ai (AI Tutorials)

**Result:** Videos appear in Shorts feed on all 4 channels!

---

## Troubleshooting

### Error: "Missing required parameter: redirect_uri"
**Solution:** Don't try to manually access the OAuth URL. Instead:
1. Run: `python authenticate_youtube.py`
2. The script will display the correct link with all required parameters
3. Follow the on-screen instructions

### Error: "client_secret.json not found"
**Solution:**
1. Go to https://console.cloud.google.com
2. Create a new project called "joe"
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the JSON file
6. Save it as: `config/client_secret.json`

### Error: "Credentials are invalid"
**Solution:** Delete the old credentials and re-authenticate:
```bash
del config\youtube_credentials.pickle
python authenticate_youtube.py
```

### Video not appearing in Shorts feed
**Check:**
- Is the video 1080x1920? ✓ (run_full_pipeline_demo.py ensures this)
- Is the duration under 3 minutes? ✓ (auto-generated videos are ~45 seconds)
- Is it uploaded as PUBLIC (not unlisted)? ✓ (batch_upload_all_channels.py uses public)
- Did it have #Shorts hashtag? ✓ (auto-included in title)

---

## Manual Upload (If Scripts Fail)

If the automatic scripts don't work, you can:

1. Generate video:
   ```bash
   python run_full_pipeline_demo.py
   ```

2. Upload manually:
   - Go to https://studio.youtube.com
   - Click "Create" → "Upload video"
   - Upload: `output/video_overlaid.mp4`
   - Title: "AI Money Secrets - [Channel Name] #Shorts"
   - Description: Copy from channels_config.json
   - Privacy: PUBLIC (not Unlisted)
   - Click "Upload"

---

## What Gets Uploaded

Each video includes:

**Video Specs:**
- Resolution: 1080 x 1920 (9:16 aspect ratio)
- Duration: ~45 seconds
- Format: MP4 + H.264 codec
- Frame rate: 30 fps

**Content:**
- AI-generated script (unique per channel niche)
- Professional text-to-speech narration
- Graphics overlays with channel accent colors
- Smooth transitions and effects
- Optimized for YouTube Shorts algorithm

**Metadata:**
- Title: Auto-generated based on channel niche
- Description: Auto-generated with channel-specific content
- Tags: Includes #Shorts, niche-specific tags
- Category: Education (22)
- Privacy: PUBLIC (live immediately)

---

## Channels

| Channel | Niche | Accent Color |
|---------|-------|--------------|
| money_blueprints | Finance | #00d4aa (Teal-Gold) |
| mind_unlocked | Psychology | #9b59b6 (Purple) |
| neural_forge | AI/Tech | #00d4ff (Cyan) |
| prof8ssor_ai | AI Tutorials | #3498db (Blue) |

---

## Next Steps

1. **Set up authentication:** `python authenticate_youtube.py`
2. **Generate first video:** `python run_full_pipeline_demo.py`
3. **Upload to all channels:** `python batch_upload_all_channels.py`
4. **Check uploads:** Go to YouTube Studio and verify they're public

That's it! Your videos are now live on all 4 channels.
