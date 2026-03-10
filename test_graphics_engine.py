"""
Simple test for graphics engine module.

Tests:
1. Load channels config
2. Load overlay YAML config
3. Test template variable substitution
4. Test timing resolution
5. Test filter building (without FFmpeg)
"""

import json
import os
from pathlib import Path

# Add project to path
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.content.graphics_engine import (
    _load_channels_config,
    _load_overlay_config,
    _resolve_template_variables,
    _resolve_timing,
    _build_drawtext_filter,
)
from src.content.overlay_templates import get_overlays_for_channel


def test_load_channels_config():
    """Test loading channels configuration."""
    print("\n[TEST] Loading channels config...")
    try:
        channels = _load_channels_config()
        print(f"  [OK] Loaded {len(channels)} channels")
        assert "money_blueprints" in channels, "money_blueprints not in config"
        assert "mind_unlocked" in channels, "mind_unlocked not in config"
        print("  [OK] All expected channels present")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed: {e}")
        return False


def test_load_overlay_yaml():
    """Test loading overlay YAML (non-fatal if missing)."""
    print("\n[TEST] Loading overlay YAML...")
    try:
        # YAML file may not exist yet - that's OK
        config = _load_overlay_config("money_blueprints")
        if config is None:
            print("  [INFO] Overlay YAML not found (expected for first run)")
        else:
            print(f"  [OK] Loaded overlay config with {len(config.get('overlays', []))} overlays")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed: {e}")
        return False


def test_overlay_templates():
    """Test getting overlay templates from Python."""
    print("\n[TEST] Loading overlay templates...")
    try:
        config = get_overlays_for_channel("money_blueprints")
        assert "overlays" in config, "Missing overlays key"
        overlays = config.get("overlays", [])
        print(f"  [OK] Loaded {len(overlays)} overlays for money_blueprints")

        # Check overlay structure
        for overlay in overlays:
            assert "id" in overlay, f"Overlay missing 'id': {overlay}"
            assert "type" in overlay, f"Overlay missing 'type': {overlay}"
            assert "text" in overlay, f"Overlay missing 'text': {overlay}"

        print("  [OK] All overlays have required fields")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed: {e}")
        return False


def test_template_substitution():
    """Test template variable substitution."""
    print("\n[TEST] Template variable substitution...")
    try:
        script = {
            "hook_text": "Wall Street doesn't want you to know...",
            "key_benefit": "Earn $500-$10K/month",
            "channel_name": "Money Blueprints",
            "duration_s": 45,
        }

        # Test hook_text substitution
        result = _resolve_template_variables("{{ hook_text }} is amazing!", script)
        expected = "Wall Street doesn't want you to know... is amazing!"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print(f"  [OK] hook_text: {result}")

        # Test key_benefit substitution
        result = _resolve_template_variables("Try: {{ key_benefit }}", script)
        expected = "Try: Earn $500-$10K/month"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print(f"  [OK] key_benefit: {result}")

        # Test empty variable (should leave as-is)
        script_empty = {"hook_text": ""}
        result = _resolve_template_variables("{{ hook_text }}", script_empty)
        assert result == "{{ hook_text }}", "Empty variable should not be replaced"
        print(f"  [OK] Empty variable handling")

        return True
    except Exception as e:
        print(f"  [FAIL] Failed: {e}")
        return False


def test_timing_resolution():
    """Test negative timing resolution (relative to end)."""
    print("\n[TEST] Timing resolution...")
    try:
        # Test positive timing
        result = _resolve_timing(5.0, 45.0)
        assert result == 5.0, f"Expected 5.0, got {result}"
        print(f"  [OK] Positive timing: 5.0s")

        # Test negative timing (relative to end)
        result = _resolve_timing(-3.0, 45.0)
        expected = 42.0  # 45 - 3 = 42
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"  [OK] Negative timing: -3.0s -> {result}s (2 sec before end)")

        # Test negative timing beyond duration (clamp to 0)
        result = _resolve_timing(-50.0, 45.0)
        assert result == 0, f"Expected 0, got {result}"
        print(f"  [OK] Over-negative timing clamped to 0")

        return True
    except Exception as e:
        print(f"  [FAIL] Failed: {e}")
        return False


def test_drawtext_filter():
    """Test FFmpeg drawtext filter building."""
    print("\n[TEST] FFmpeg drawtext filter building...")
    try:
        # Basic filter
        result = _build_drawtext_filter("Hello World", fontsize=60)
        assert "text='Hello World'" in result, f"Text not in filter: {result}"
        print(f"  [OK] Basic filter: {result[:80]}...")

        # Filter with timing
        result = _build_drawtext_filter("Hook", start_time=0, end_time=3)
        assert "enable=" in result, "enable expression missing"
        assert "between(t,0,3)" in result, f"Timing expression incorrect: {result}"
        print(f"  [OK] Filter with timing: {result[:80]}...")

        # Filter with box
        result = _build_drawtext_filter("Text", boxcolor="0x00000080")
        assert "box=1" in result, "Box enable missing"
        assert "boxcolor=" in result, "Box color missing"
        print(f"  [OK] Filter with box: {result[:80]}...")

        return True
    except Exception as e:
        print(f"  [FAIL] Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("GRAPHICS ENGINE TEST SUITE")
    print("="*70)

    tests = [
        ("Channels Config", test_load_channels_config),
        ("Overlay YAML", test_load_overlay_yaml),
        ("Overlay Templates", test_overlay_templates),
        ("Template Substitution", test_template_substitution),
        ("Timing Resolution", test_timing_resolution),
        ("FFmpeg Filter Building", test_drawtext_filter),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\nTotal: {passed}/{total} passed")
    print("="*70)

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
