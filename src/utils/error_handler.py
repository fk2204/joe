"""
Structured Error Handling for Joe

Provides error classes, retry logic, and user-friendly error messages.
"""

import logging
from typing import Any, Callable, Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)


class JoeError(Exception):
    """Base error class for all Joe errors."""

    def __init__(
        self,
        code: str,
        user_msg: str,
        tech_details: str = "",
        suggestion: str = "",
    ):
        self.code = code
        self.user_msg = user_msg
        self.tech_details = tech_details
        self.suggestion = suggestion
        super().__init__(user_msg)

    def show_user_message(self):
        """Display user-friendly error message."""
        print(f"\n[ERROR] {self.code}")
        print(f"        {self.user_msg}")
        if self.suggestion:
            print(f"        Suggestion: {self.suggestion}")

    def log_details(self):
        """Log technical details for debugging."""
        logger.error(
            f"{self.code}: {self.user_msg} | Details: {self.tech_details}"
        )


class ConfigError(JoeError):
    """Configuration file or environment issue."""
    pass


class OAuthError(JoeError):
    """YouTube OAuth authentication error."""
    pass


class UploadError(JoeError):
    """YouTube upload error."""
    pass


class FFmpegError(JoeError):
    """FFmpeg video processing error."""
    pass


class TTSError(JoeError):
    """Text-to-speech generation error."""
    pass


class RetryError(JoeError):
    """All retry attempts failed."""
    pass


def retry(
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: tuple = None,
    exceptions: tuple = None,
):
    """Decorator: Retry function with exponential backoff."""
    # Handle both parameter names for compatibility
    exc_tuple = exceptions or retryable_exceptions or (Exception,)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_backoff = backoff_seconds
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exc_tuple as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    else:
                        logger.warning(f"{func.__name__} attempt {attempt} failed, retrying in {current_backoff}s")
                        time.sleep(current_backoff)
                        current_backoff *= backoff_multiplier
        return wrapper
    return decorator


def check_file_exists(path: str, error_code: str = "ERR_FILE_NOT_FOUND") -> bool:
    """Check if file exists, raise ConfigError if not."""
    import os
    if not os.path.exists(path):
        raise ConfigError(
            code=error_code,
            user_msg=f"Required file not found: {path}",
            suggestion=f"Make sure {path} exists",
        )
    return True


from contextlib import contextmanager


@contextmanager
def ErrorContext(operation: str, details: str = ""):
    """Context manager for operation tracking with error logging."""
    import time
    start = time.time()
    try:
        yield
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"[{operation}] Failed after {elapsed:.2f}s. Details: {details}. Error: {e}")
        raise
    else:
        elapsed = time.time() - start
        logger.debug(f"[{operation}] Completed in {elapsed:.2f}s")


def handle_tts_error(error: Exception, voice: str = "", text_length: int = 0) -> None:
    """Handle TTS-specific errors with helpful messages."""
    error_msg = str(error).lower()

    if "api" in error_msg or "connection" in error_msg:
        raise TTSError(
            code="ERR_TTS_API",
            user_msg="Text-to-speech API connection failed",
            tech_details=str(error),
            suggestion="Check internet connection and API status",
        )
    elif "auth" in error_msg:
        raise TTSError(
            code="ERR_TTS_AUTH",
            user_msg="Text-to-speech authentication failed",
            tech_details=str(error),
            suggestion="Check API credentials in .env file",
        )
    elif "limit" in error_msg or "rate" in error_msg:
        raise TTSError(
            code="ERR_TTS_RATE_LIMIT",
            user_msg="Text-to-speech rate limit exceeded",
            tech_details=str(error),
            suggestion="Wait a few minutes before retrying",
        )
    else:
        raise TTSError(
            code="ERR_TTS_UNKNOWN",
            user_msg=f"Text-to-speech generation failed for voice '{voice}' ({text_length} chars)",
            tech_details=str(error),
            suggestion="Try with a different voice or shorter text",
        )


def handle_ffmpeg_error(error: Exception, operation: str = "encoding") -> None:
    """Handle FFmpeg-specific errors."""
    error_msg = str(error).lower()

    if "not found" in error_msg or "command not found" in error_msg:
        raise FFmpegError(
            code="ERR_FFMPEG_NOT_FOUND",
            user_msg="FFmpeg is not installed",
            tech_details=str(error),
            suggestion="Install FFmpeg from https://ffmpeg.org/download.html",
        )
    elif "invalid" in error_msg or "format" in error_msg:
        raise FFmpegError(
            code="ERR_FFMPEG_FORMAT",
            user_msg=f"Invalid video format for {operation}",
            tech_details=str(error),
            suggestion="Use H.264 codec with MP4 container",
        )
    else:
        raise FFmpegError(
            code="ERR_FFMPEG_UNKNOWN",
            user_msg=f"FFmpeg {operation} failed",
            tech_details=str(error),
            suggestion="Check video file integrity and format",
        )


def handle_upload_error(error: Exception, video_id: str = "") -> None:
    """Handle YouTube upload-specific errors."""
    error_msg = str(error).lower()

    if "auth" in error_msg or "401" in error_msg or "403" in error_msg:
        raise UploadError(
            code="ERR_UPLOAD_AUTH",
            user_msg="YouTube authentication failed - credentials may have expired",
            tech_details=str(error),
            suggestion="Run: python authenticate_youtube.py",
        )
    elif "quota" in error_msg or "limit" in error_msg:
        raise UploadError(
            code="ERR_UPLOAD_QUOTA",
            user_msg="YouTube upload quota exceeded",
            tech_details=str(error),
            suggestion="Wait 24 hours or request higher quota",
        )
    elif "not found" in error_msg or "404" in error_msg:
        raise UploadError(
            code="ERR_UPLOAD_FILE_NOT_FOUND",
            user_msg="Video file not found for upload",
            tech_details=str(error),
            suggestion="Check file path exists and is accessible",
        )
    else:
        raise UploadError(
            code="ERR_UPLOAD_UNKNOWN",
            user_msg="YouTube upload failed",
            tech_details=str(error),
            suggestion="Check internet connection and try again",
        )
