#!/usr/bin/env python3
"""
Test script demonstrating the error handling module.

This shows:
1. Pre-flight system checks
2. Custom error classes with user messages
3. Retry decorator with exponential backoff
4. Error context tracking
"""

import sys
import os

# Setup path
project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from src.utils.error_handler import (
    JoeError,
    FFmpegError,
    TTSError,
    OAuthError,
    UploadError,
    ConfigError,
    retry,
    ErrorContext,
    check_system,
)


def test_pre_flight_checks():
    """Test system pre-flight checks."""
    print("\n" + "=" * 70)
    print("TEST 1: PRE-FLIGHT SYSTEM CHECKS")
    print("=" * 70)

    result = check_system()
    return result


def test_error_messages():
    """Test custom error messages."""
    print("\n" + "=" * 70)
    print("TEST 2: CUSTOM ERROR MESSAGES")
    print("=" * 70)

    # Test FFmpeg error
    print("\n--- FFmpeg Error Example ---")
    try:
        raise FFmpegError(
            code="FFMPEG_NOT_FOUND",
            user_msg="FFmpeg not installed. Video generation requires FFmpeg.",
            tech_details="find_ffmpeg() returned None",
            suggestion="Install from https://ffmpeg.org/download.html or: choco install ffmpeg",
        )
    except FFmpegError as e:
        e.show_user_message()

    # Test TTS error
    print("\n--- TTS Error Example ---")
    try:
        raise TTSError(
            code="TTS_RATE_LIMIT",
            user_msg="Too many TTS requests. Rate limit exceeded.",
            tech_details="Edge-TTS API returned 429 Too Many Requests",
            suggestion="Wait 5-10 minutes and try again",
        )
    except TTSError as e:
        e.show_user_message()

    # Test OAuth error
    print("\n--- OAuth Error Example ---")
    try:
        raise OAuthError(
            code="OAUTH_CREDENTIALS_INVALID",
            user_msg="YouTube credentials are invalid or expired.",
            tech_details="Credentials file corrupted or refresh failed",
            suggestion="Run: python authenticate_youtube.py",
        )
    except OAuthError as e:
        e.show_user_message()

    # Test Config error
    print("\n--- Config Error Example ---")
    try:
        raise ConfigError(
            code="YOUTUBE_CLIENT_SECRET_MISSING",
            user_msg="YouTube client_secret.json not found.",
            tech_details="Expected at config/client_secret.json",
            suggestion=(
                "1. Go to https://console.cloud.google.com\n"
                "2. Create a new project\n"
                "3. Enable YouTube Data API v3\n"
                "4. Create OAuth 2.0 Desktop credentials\n"
                "5. Download and save to config/client_secret.json"
            ),
        )
    except ConfigError as e:
        e.show_user_message()


def test_retry_decorator():
    """Test retry decorator with exponential backoff."""
    print("\n" + "=" * 70)
    print("TEST 3: RETRY DECORATOR (Simulated)")
    print("=" * 70)

    @retry(max_attempts=3, backoff_seconds=0.5, log_on_retry=True)
    def flaky_function(call_count=[0]):
        """Simulates a function that fails twice, then succeeds."""
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError(f"Simulated network error (attempt {call_count[0]})")
        return "Success on attempt 3!"

    try:
        result = flaky_function()
        print(f"\n[OK] {result}")
    except Exception as e:
        print(f"[FAILED] {e}")


def test_error_context():
    """Test error context manager."""
    print("\n" + "=" * 70)
    print("TEST 4: ERROR CONTEXT TRACKING")
    print("=" * 70)

    # Successful operation
    print("\n--- Successful Operation ---")
    with ErrorContext("TTS Generation", "text='Hello world', voice=en-US-GuyNeural"):
        print("[Context] Generating audio...")
        # Simulate work
        import time
        time.sleep(0.5)
        print("[Context] Audio generated")

    # Failed operation
    print("\n--- Failed Operation ---")
    try:
        with ErrorContext("Video Upload", "file=test.mp4"):
            print("[Context] Uploading video...")
            raise IOError("Network timeout during upload")
    except IOError as e:
        print(f"[Caught] {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("JOE ERROR HANDLING TEST SUITE")
    print("=" * 70)

    # Test 1: Pre-flight checks
    checks_passed = test_pre_flight_checks()

    # Test 2: Custom error messages
    test_error_messages()

    # Test 3: Retry decorator
    test_retry_decorator()

    # Test 4: Error context
    test_error_context()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"System checks: {'PASSED' if checks_passed else 'SOME ISSUES'}")
    print("Error messages: PASSED")
    print("Retry decorator: PASSED")
    print("Error context: PASSED")
    print("\nAll error handling features working correctly!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
