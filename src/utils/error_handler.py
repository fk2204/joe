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
    retryable_exceptions: tuple = (Exception,),
):
    """Decorator: Retry function with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_backoff = backoff_seconds
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
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
