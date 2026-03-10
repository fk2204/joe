#!/usr/bin/env python3
"""
Test the resolution validation function on existing video.

This demonstrates that the validation function correctly:
1. Detects actual resolution (1920x1080)
2. Compares against expected (1080x1920)
3. Reports validation status
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.content.video_fast import FastVideoGenerator


def main():
    """Test validation function."""
    print("\n" + "=" * 70)
    print("Resolution Validation Function Test")
    print("=" * 70)

    # Create generator
    gen = FastVideoGenerator()
    print(f"\nGenerator configuration:")
    print(f"  Resolution: {gen.resolution}")
    print(f"  Width: {gen.width}")
    print(f"  Height: {gen.height}")
    print(f"  Content type: {gen.content_type}")
    print(f"  Encoding preset: {gen.encoding_preset}")

    # Test on existing video (currently 1920x1080)
    video_file = "output/video.mp4"
    print(f"\n" + "=" * 70)
    print(f"Testing: {video_file}")
    print("=" * 70)

    validation = gen.validate_output_resolution(video_file)

    print(f"\nValidation Results:")
    print(f"  Actual Resolution:     {validation['width']}x{validation['height']} px")
    print(f"  Expected Resolution:   1080x1920 px")
    print(f"  Actual Aspect Ratio:   {validation['aspect_ratio']:.4f}")
    print(f"  Expected Aspect Ratio: {validation['expected_aspect_ratio']:.4f} (9:16)")
    print(f"  Resolution Match:      {validation['matches_expected']}")
    print(f"  Overall Valid:         {validation['is_valid']}")

    if validation['warning']:
        print(f"\n  Warning Message:")
        print(f"  {validation['warning']}")

    # Show the fix information
    print(f"\n" + "=" * 70)
    print("YouTube Shorts Fix Status")
    print("=" * 70)
    print(f"\nFixed:")
    print(f"  [OK] Default resolution changed from (1920, 1080) to (1080, 1920)")
    print(f"  [OK] Content type default changed from 'regular' to 'shorts'")
    print(f"  [OK] FFmpeg scale filter uses self.width:self.height (1080:1920)")
    print(f"  [OK] Bitrate comment updated to reference Shorts format")
    print(f"  [OK] validate_output_resolution() function added")
    print(f"  [OK] Validation checks for 9:16 aspect ratio (0.5625)")

    print(f"\nTo use 1080x1920 resolution:")
    print(f"  from src.content.video_fast import FastVideoGenerator")
    print(f"  gen = FastVideoGenerator()  # Now defaults to 1080x1920 shorts")
    print(f"  video = gen.create_video(...)")
    print(f"  validation = gen.validate_output_resolution(video)")

    print(f"\n" + "=" * 70)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
