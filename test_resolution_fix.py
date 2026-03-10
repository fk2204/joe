#!/usr/bin/env python3
"""
Test script to verify YouTube Shorts resolution fix (1080x1920).

This script:
1. Generates a test video with the new resolution
2. Validates the output resolution using ffprobe
3. Reports the results
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.content.video_fast import FastVideoGenerator
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | {message}", level="DEBUG")


def check_ffprobe_installed():
    """Check if ffprobe is available."""
    try:
        result = subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def main():
    """Run the resolution validation test."""
    print("\n" + "=" * 70)
    print("YouTube Shorts Resolution Fix Test (1080x1920)")
    print("=" * 70)

    # Check prerequisites
    print("\n1. Checking prerequisites...")
    if not check_ffprobe_installed():
        print("   [FAIL] ffprobe not found. Install FFmpeg to continue.")
        print("   Download from: https://ffmpeg.org/download.html")
        return False

    print("   [OK] ffprobe available")

    # Check for test audio
    audio_file = "output/narration.mp3"
    if not os.path.exists(audio_file):
        print(f"   [FAIL] Test audio not found: {audio_file}")
        return False

    print(f"   [OK] Test audio available: {audio_file}")

    # Create output directory
    os.makedirs("output", exist_ok=True)

    # Generate test video
    print("\n2. Generating test video with 1080x1920 resolution...")
    generator = FastVideoGenerator()
    print(f"   Generator resolution: {generator.resolution}")
    print(f"   Generator width: {generator.width}")
    print(f"   Generator height: {generator.height}")
    print(f"   Content type: {generator.content_type}")

    output_file = "output/test_shorts_video.mp4"
    print(f"\n   Creating video: {output_file}")

    video_file = generator.create_video(
        audio_file=audio_file,
        output_file=output_file,
        title="YouTube Shorts Test",
        subtitle="1080x1920 Vertical Format",
    )

    if not video_file:
        print("   [FAIL] Video creation failed")
        return False

    print(f"   [OK] Video created: {video_file}")

    # Validate resolution
    print("\n3. Validating output resolution...")
    validation = generator.validate_output_resolution(video_file)

    print(f"\n   Resolution Details:")
    print(f"   - Width:              {validation['width']} px")
    print(f"   - Height:             {validation['height']} px")
    print(f"   - Actual aspect ratio: {validation['aspect_ratio']:.4f}")
    print(f"   - Expected (9:16):    {validation['expected_aspect_ratio']:.4f}")
    print(f"   - Matches expected:   {validation['matches_expected']}")

    print(f"\n   Validation Status:")
    if validation["is_valid"]:
        print("   [OK] PASS - Video is correctly formatted for YouTube Shorts!")
    else:
        print("   [FAIL] FAIL - Video does not match YouTube Shorts format")
        if validation["warning"]:
            print(f"   Warning: {validation['warning']}")

    # File info
    print(f"\n4. File Information:")
    file_size = os.path.getsize(video_file)
    file_size_mb = file_size / (1024 * 1024)
    print(f"   - File size: {file_size_mb:.2f} MB")
    print(f"   - Location: {os.path.abspath(video_file)}")

    # Summary
    print("\n" + "=" * 70)
    if validation["is_valid"]:
        print("[OK] TEST PASSED - All resolution checks successful!")
        print("=" * 70)
        return True
    else:
        print("[FAIL] TEST FAILED - Resolution validation failed")
        if validation["warning"]:
            print(f"Error: {validation['warning']}")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
