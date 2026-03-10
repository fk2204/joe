# Error Handling Module - Joe System

## Overview

The error handling module (`src/utils/error_handler.py`) provides:

1. **Structured error classes** with user-friendly messages
2. **Retry decorator** with exponential backoff for resilient operations
3. **Pre-flight system checks** before pipeline execution
4. **Error context tracking** for better debugging
5. **Domain-specific error handlers** for different failures

## Quick Start

### Running Pre-flight Checks

```bash
# Check system before running pipeline
python -c "from src.utils.error_handler import check_system; check_system()"
```

Output:
```
======================================================================
PRE-FLIGHT SYSTEM CHECKS
======================================================================

Checking FFmpeg...
  [OK] FFmpeg found: ffmpeg version 8.0...

Checking Python Packages...
  [OK] Package installed: edge_tts...
  [OK] Package installed: PIL...
  [OK] Package installed: google.auth...

... (all checks shown)

======================================================================
RESULTS: 12 passed, 0 failed
======================================================================

All checks passed! Ready to start pipeline.
```

### Test Error Handling

```bash
python test_error_handling.py
```

## Error Classes

### JoeError (Base Class)

All errors inherit from `JoeError` with these properties:

```python
from src.utils.error_handler import JoeError

error = JoeError(
    code="OPERATION_FAILED",           # Machine-readable error code
    user_msg="User-friendly message",  # What to show the user
    tech_details="Debug info...",      # Technical details for logs
    suggestion="Try this fix..."       # Recommended action
)

# Show user message
error.show_user_message()

# Log technical details
error.log_details()
```

### Domain-Specific Errors

#### FFmpegError
```python
from src.utils.error_handler import FFmpegError

raise FFmpegError(
    code="FFMPEG_NOT_FOUND",
    user_msg="FFmpeg not installed. Video generation requires FFmpeg.",
    tech_details="find_ffmpeg() returned None",
    suggestion="Install from https://ffmpeg.org/download.html"
)
```

#### TTSError
```python
from src.utils.error_handler import TTSError

raise TTSError(
    code="TTS_RATE_LIMIT",
    user_msg="Too many TTS requests. Rate limit exceeded.",
    tech_details="Edge-TTS API returned 429",
    suggestion="Wait 5-10 minutes and try again"
)
```

#### OAuthError
```python
from src.utils.error_handler import OAuthError

raise OAuthError(
    code="OAUTH_CREDENTIALS_INVALID",
    user_msg="YouTube credentials are invalid or expired.",
    tech_details="Credentials file corrupted",
    suggestion="Run: python authenticate_youtube.py"
)
```

#### UploadError
```python
from src.utils.error_handler import UploadError

raise UploadError(
    code="UPLOAD_QUOTA_EXCEEDED",
    user_msg="YouTube upload quota exceeded. Too many uploads today.",
    tech_details="YouTube API returned quotaExceeded",
    suggestion="Wait and try again tomorrow"
)
```

#### ConfigError
```python
from src.utils.error_handler import ConfigError

raise ConfigError(
    code="CONFIG_FILE_MISSING",
    user_msg="Configuration file not found.",
    tech_details="Expected at config/config.yaml",
    suggestion="Create config/config.yaml or check path"
)
```

## Retry Decorator

### Basic Usage

```python
from src.utils.error_handler import retry

# Retry with defaults (3 attempts, 1s backoff)
@retry()
def my_function():
    # Will retry on any exception
    pass

# Custom retry parameters
@retry(max_attempts=5, backoff_seconds=2)
def flaky_api_call():
    pass

# Retry only on specific exceptions
@retry(
    max_attempts=3,
    backoff_seconds=1,
    exceptions=(ConnectionError, TimeoutError)
)
async def network_operation():
    pass
```

### How It Works

1. **First attempt**: Runs immediately
2. **Failed**: Logs warning, waits for backoff time
3. **Second attempt**: Tries again after backoff
4. **Exponential backoff**: Wait time doubles each attempt
   - Attempt 1: immediate
   - Attempt 2: 1 second
   - Attempt 3: 2 seconds
   - Attempt 4: 4 seconds
   - ...

### Example: TTS with Retry

```python
from src.content.tts import TextToSpeech

tts = TextToSpeech()

# Decorated with @retry internally
# Automatically retries on network errors
audio = await tts.generate("Hello world", "output.mp3")
```

### Example: Upload with Retry

```python
from src.youtube.uploader import YouTubeUploader

uploader = YouTubeUploader()

# Decorated with @retry internally
# Automatically retries on temporary failures
result = uploader.upload_video(
    video_file="video.mp4",
    title="My Video",
    description="...",
    category="education"
)
```

## Error Context Manager

Track the context of operations for better debugging:

```python
from src.utils.error_handler import ErrorContext

# Successful operation
with ErrorContext("TTS Generation", f"voice={voice}, chars={len(text)}"):
    result = await tts.generate(text, output_file)

# Failed operation (context logged automatically)
with ErrorContext("Video Upload", f"file={video_file}"):
    uploader.upload_video(video_file, title, description)
```

Logs like:
```
2026-03-10 02:33:26 | INFO    | Starting: TTS Generation, details=voice=en-US-GuyNeural, chars=450
2026-03-10 02:33:26 | INFO    | Completed: TTS Generation (0.5s)
2026-03-10 02:33:27 | ERROR   | Failed: Video Upload (2.3s), error=Network timeout
```

## System Pre-Flight Checks

### What Gets Checked

1. **FFmpeg** - Is it installed and working?
2. **Python Packages** - Are all required libraries available?
3. **Config Files** - Do config.yaml, channels.yaml, .env exist?
4. **YouTube Auth** - Is client_secret.json present?
5. **Output Directory** - Can we write to output/?

### Usage

```python
from src.utils.error_handler import check_system

# Run all checks
success = check_system()

if not success:
    print("Fix the above issues and try again")
    sys.exit(1)
```

### Example Output (All Passing)

```
======================================================================
PRE-FLIGHT SYSTEM CHECKS
======================================================================

Checking FFmpeg...
  [OK] FFmpeg found: ffmpeg version 8.0.1-full_build

Checking Python Packages...
  [OK] Package installed: edge_tts (Edge TTS (text-to-speech))
  [OK] Package installed: PIL (Pillow (image processing))
  [OK] Package installed: google.auth (Google Auth (YouTube API))
  [OK] Package installed: googleapiclient (Google API Client (YouTube upload))
  [OK] Package installed: loguru (Loguru (logging))

Checking Config Files...
  [OK] Config found: config/config.yaml (Main configuration)
  [OK] Config found: config/channels.yaml (Channel configuration)
  [OK] Config found: .env (Environment variables)

Checking YouTube Auth...
  [OK] YouTube credentials file: config/client_secret.json
  [OK] YouTube OAuth cache: config/youtube_credentials.pickle

Checking Output Directory...
  [OK] Output directory writable: output

======================================================================
RESULTS: 12 passed, 0 failed
======================================================================

All checks passed! Ready to start pipeline.
```

## Integration in Main Scripts

### run_full_pipeline_demo.py

```python
# Pre-flight checks
try:
    from src.utils.error_handler import check_system

    if not check_system():
        print("\nFix the above issues and try again.")
        return
except Exception as e:
    print(f"[WARN] System checks failed: {e}")
    # Continue anyway - not critical

# TTS with error handling
try:
    asyncio.run(tts.generate(script['narration'], audio_file))
except TTSError as e:
    e.show_user_message()
    e.log_details()
    return

# Video creation with error handling
try:
    result = generator.create_video(audio_file, output_file, ...)
except FFmpegError as e:
    e.show_user_message()
    e.log_details()
    return

# Upload with error handling
try:
    result = uploader.upload_video(video_file, title, ...)
except (UploadError, OAuthError) as e:
    e.show_user_message()
    e.log_details()
    return
```

### batch_upload_all_channels.py

```python
# Upload to each channel, continue on error
for channel in channels:
    try:
        success = upload_to_channel(channel, video_file)
        results[channel] = success
    except UploadError as e:
        print(f"[ERROR] {e.code}: {e.user_msg}")
        results[channel] = False
        # Continue to next channel

# Show summary
for channel, success in results.items():
    status = "[OK]" if success else "[FAILED]"
    print(f"{status} {channel}")
```

### authenticate_youtube.py

```python
try:
    auth = YouTubeAuth()
    service = auth.get_authenticated_service()
    # Success
except (OAuthError, ConfigError) as e:
    e.show_user_message()
    e.log_details()
    return False
```

## Error Handling Patterns

### Pattern 1: Validate Before Operations

```python
from src.utils.error_handler import FFmpegError, ConfigError

# Check files exist before processing
if not os.path.exists(audio_file):
    raise FFmpegError(
        code="AUDIO_FILE_NOT_FOUND",
        user_msg=f"Audio file not found: {audio_file}",
        tech_details=f"Expected file at {audio_file}",
        suggestion="Check that the audio file exists"
    )
```

### Pattern 2: Graceful Degradation

```python
from src.utils.error_handler import ErrorContext

# Try feature, fallback if it fails
with ErrorContext("Shorts Overlays", f"channel={channel_id}"):
    try:
        apply_overlays(input_video, output_video, channel_id, script)
        video_file = output_video
    except Exception as e:
        logger.warning(f"Overlays failed, continuing without: {e}")
        # Use video without overlays
```

### Pattern 3: Retry Network Operations

```python
from src.utils.error_handler import retry

@retry(max_attempts=3, backoff_seconds=2, exceptions=(TimeoutError, ConnectionError))
async def fetch_data_from_api():
    response = await api.get("/data")
    return response.json()
```

### Pattern 4: Context-Specific Error Handling

```python
from src.utils.error_handler import ErrorContext, TTSError

with ErrorContext("Audio Generation", f"text_length={len(text)}"):
    try:
        await tts.generate(text, output_file)
    except TTSError as e:
        if "rate_limit" in e.code.lower():
            logger.info("Rate limited, waiting and retrying...")
            await asyncio.sleep(60)
            await tts.generate(text, output_file)
        else:
            raise
```

## Testing

Run the test suite:

```bash
python test_error_handling.py
```

This tests:
- Pre-flight system checks
- All error message types
- Retry decorator with backoff
- Error context tracking
- Integration with main modules

## Files Modified

### New Files
- `src/utils/error_handler.py` - Error handling module
- `test_error_handling.py` - Test suite

### Modified Files
- `src/content/tts.py` - Added error handling and retry
- `src/content/video_fast.py` - Added error handling and validation
- `src/youtube/uploader.py` - Added error handling and retry
- `src/youtube/auth.py` - Improved error messages
- `run_full_pipeline_demo.py` - Pre-flight checks and error handling
- `batch_upload_all_channels.py` - Continue-on-error for batch uploads
- `authenticate_youtube.py` - Better error messages

## Error Recovery Examples

### FFmpeg Not Found
**Before:**
```
ERROR: FFmpeg not available
(operator has no idea what to do)
```

**After:**
```
======================================================================
ERROR: FFMPEG_NOT_FOUND
======================================================================

FFmpeg not installed. Video generation requires FFmpeg.

Try this: Install from https://ffmpeg.org/download.html
         or: choco install ffmpeg
```

### TTS Rate Limit
**Before:**
```
ConnectionError: [Errno 429] ...
(operator confused about what happened)
```

**After:**
```
======================================================================
ERROR: TTS_RATE_LIMIT
======================================================================

Too many TTS requests. Rate limit exceeded.

Try this: Wait 5-10 minutes and try again
```

### YouTube Auth Failed
**Before:**
```
Exception: invalid_grant
(no idea what credentials are needed)
```

**After:**
```
======================================================================
ERROR: OAUTH_CREDENTIALS_INVALID
======================================================================

YouTube credentials are invalid or expired.

Try this: Run: python authenticate_youtube.py
```

### Missing YouTube Secret
**Before:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config/client_secret.json'
(operator doesn't know how to get the file)
```

**After:**
```
======================================================================
ERROR: YOUTUBE_CLIENT_SECRET_MISSING
======================================================================

YouTube client_secret.json not found.

Try this: 1. Go to https://console.cloud.google.com
         2. Create a new project
         3. Enable YouTube Data API v3
         4. Create OAuth 2.0 Desktop credentials
         5. Download and save to config/client_secret.json
```

## Best Practices

### DO:
- Use specific error codes (e.g., `FFMPEG_NOT_FOUND`, not `ERROR`)
- Include actionable suggestions
- Log technical details for debugging
- Use retry decorator for network operations
- Check preconditions before operations

### DON'T:
- Silently fail - always raise or log
- Generic error messages - be specific
- Mix error handling with business logic
- Retry non-idempotent operations
- Log sensitive information (passwords, tokens)

## Future Enhancements

Potential additions:
- Error telemetry/analytics
- Automatic issue reporting
- Recovery action execution
- Error recovery strategies
- Circuit breaker pattern for external APIs
- Custom error handlers per module
