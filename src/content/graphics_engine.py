"""
Graphics Engine Module - Apply YouTube Shorts overlays to videos using FFmpeg.

Applies text overlays (hooks, key benefits, etc.) to short-form videos.
Uses FFmpeg filter_complex for single-pass overlay application with audio passthrough.

Usage:
    from src.content.graphics_engine import apply_overlays

    output = apply_overlays(
        input_video="video.mp4",
        output_video="video_overlaid.mp4",
        channel_id="money_blueprints",
        script={
            "hook_text": "Wall Street doesn't want you to know...",
            "key_benefit": "Earn $500-$10K/month",
            "duration_s": 45,
        }
    )
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger

from src.content.video_utils import find_ffmpeg


class GraphicsEngineError(Exception):
    """Raised when graphics engine operations fail."""

    pass


def _load_channels_config() -> Dict[str, Dict[str, Any]]:
    """
    Load channels configuration from channels_config.json.

    Returns:
        Dict mapping channel_id to channel config dict.

    Raises:
        GraphicsEngineError: If config file not found or invalid.
    """
    config_path = Path("config/channels_config.json")

    if not config_path.exists():
        raise GraphicsEngineError(f"channels_config.json not found at {config_path}")

    try:
        with open(config_path) as f:
            data = json.load(f)

        # Build dict keyed by channel ID
        channels_by_id = {}
        for channel in data.get("channels", []):
            channel_id = channel.get("name")  # Use 'name' as key (e.g., "money_blueprints")
            if channel_id:
                channels_by_id[channel_id] = channel

        logger.debug(f"Loaded {len(channels_by_id)} channels from config")
        return channels_by_id

    except (json.JSONDecodeError, KeyError) as e:
        raise GraphicsEngineError(f"Failed to parse channels_config.json: {e}")


def _load_overlay_config(
    channel_id: str, overlays_config_dir: str = "config/overlays"
) -> Optional[Dict[str, Any]]:
    """
    Load overlay configuration from YAML file for a channel.

    Args:
        channel_id: Channel identifier (e.g., "money_blueprints")
        overlays_config_dir: Directory containing overlay YAML files

    Returns:
        Dict with overlay configuration, or None if file not found.

    Raises:
        GraphicsEngineError: If YAML file exists but is invalid.
    """
    config_file = Path(overlays_config_dir) / f"{channel_id}_overlays.yaml"

    # Non-fatal: missing YAML file returns None
    if not config_file.exists():
        logger.warning(f"Overlay config not found: {config_file} (will skip overlays)")
        return None

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        logger.debug(f"Loaded overlay config from {config_file}")
        return config

    except yaml.YAMLError as e:
        raise GraphicsEngineError(f"Invalid YAML in {config_file}: {e}")


def _resolve_template_variables(text: str, script: Dict[str, Any]) -> str:
    """
    Substitute template variables in text.

    Supports:
    - {{ hook_text }}
    - {{ key_benefit }}
    - {{ accent_color }}
    - {{ duration_s }}
    - {{ channel_name }}

    Args:
        text: Text with template variables
        script: Dict with template values

    Returns:
        Text with substitutions applied. Unknown variables left unchanged.
    """
    result = text

    variables = {
        "hook_text": script.get("hook_text", ""),
        "key_benefit": script.get("key_benefit", ""),
        "accent_color": script.get("accent_color", "#FF0000"),
        "duration_s": str(script.get("duration_s", 0)),
        "channel_name": script.get("channel_name", ""),
    }

    for key, value in variables.items():
        if not value:
            # Skip empty variables, leave template as-is
            continue

        result = result.replace(f"{{{{ {key} }}}}", str(value))

    return result


def _resolve_timing(timing: float, total_duration: float) -> float:
    """
    Resolve negative timing values.

    Negative timing is relative to end. E.g., -4 means 4 seconds before end.

    Args:
        timing: Timing value in seconds (can be negative)
        total_duration: Total video duration in seconds

    Returns:
        Absolute timing in seconds from start.
    """
    if timing < 0:
        return max(0, total_duration + timing)  # Clamp to 0
    return timing


def _build_drawtext_filter(
    text: str,
    x: str = "w/2",
    y: str = "h/2",
    fontsize: int = 60,
    fontcolor: str = "white",
    fontfile: Optional[str] = None,
    fontweight: int = 700,
    boxcolor: Optional[str] = None,
    boxborderw: int = 0,
    start_time: float = 0,
    end_time: Optional[float] = None,
) -> str:
    """
    Build a FFmpeg drawtext filter fragment.

    Args:
        text: Text to draw (escaped for FFmpeg)
        x: X position (default: center)
        y: Y position (default: center)
        fontsize: Font size in pixels
        fontcolor: Font color name or hex (e.g., "white", "0xFF0000FF")
        fontfile: Path to font file (optional)
        fontweight: Font weight (100-900)
        boxcolor: Background box color (optional)
        boxborderw: Box border width
        start_time: Start time in seconds
        end_time: End time in seconds (optional)

    Returns:
        FFmpeg drawtext filter string.
    """
    # Escape single quotes and special chars for FFmpeg
    escaped_text = text.replace("\\", "\\\\").replace("'", "\\'")

    parts = [
        f"text='{escaped_text}'",
        f"x={x}",
        f"y={y}",
        f"fontsize={fontsize}",
        f"fontcolor={fontcolor}",
        f"line_spacing={int(fontsize * 0.2)}",
    ]

    if fontfile:
        # Escape backslashes for FFmpeg on Windows
        escaped_fontfile = fontfile.replace("\\", "\\\\")
        parts.append(f"fontfile='{escaped_fontfile}'")

    if boxcolor:
        parts.append(f"box=1")
        parts.append(f"boxcolor={boxcolor}")
        parts.append(f"boxborderw={boxborderw}")

    if start_time > 0 or end_time is not None:
        # Use enable expression for timing
        if end_time is not None:
            enable_expr = f"between(t,{start_time},{end_time})"
        else:
            enable_expr = f"gte(t,{start_time})"

        parts.append(f"enable='{enable_expr}'")

    return ":".join(parts)


def _build_filter_complex(
    overlays: List[Dict[str, Any]],
    script: Dict[str, Any],
    video_duration: float,
    accent_color: str = "0xFF0000FF",
) -> str:
    """
    Build complete FFmpeg filter_complex string from overlays config.

    Args:
        overlays: List of overlay dicts from config
        script: Script dict with template variables
        video_duration: Total video duration in seconds
        accent_color: Default accent color in 0xRRGGBBAA format

    Returns:
        FFmpeg filter_complex string ready for -filter_complex argument.
    """
    filter_parts = []

    for overlay in overlays:
        overlay_type = overlay.get("type", "text")

        if overlay_type != "text":
            logger.warning(f"Unsupported overlay type: {overlay_type}, skipping")
            continue

        # Resolve timing
        timing_start = overlay.get("timing_start_s", 0)
        timing_end = overlay.get("timing_end_s")

        start_abs = _resolve_timing(timing_start, video_duration)

        end_abs = None
        if timing_end is not None:
            # Special case: timing_end_s: 0 means "until video end"
            if timing_end == 0:
                end_abs = video_duration
            else:
                end_abs = _resolve_timing(timing_end, video_duration)

        # Resolve template variables
        text = overlay.get("text", "")
        text = _resolve_template_variables(text, script)

        # Get styling
        fontsize = overlay.get("fontsize", 60)
        fontcolor = overlay.get("fontcolor", "white")
        x = overlay.get("x", "w/2")
        y = overlay.get("y", "h/2")
        boxcolor = overlay.get("boxcolor")
        boxborderw = overlay.get("boxborderw", 0)

        # Build filter
        filter_str = _build_drawtext_filter(
            text=text,
            x=x,
            y=y,
            fontsize=fontsize,
            fontcolor=fontcolor,
            boxcolor=boxcolor,
            boxborderw=boxborderw,
            start_time=start_abs,
            end_time=end_abs,
        )

        filter_parts.append(filter_str)

    # Chain filters with comma
    if not filter_parts:
        # No overlays, return identity filter
        return "[0:v]format=yuv420p[v_out]"

    # Build chain: [0:v]filter1[tmp0]; [tmp0]filter2[tmp1]; ...; [tmpN]format=yuv420p[v_out]
    if len(filter_parts) == 1:
        # Single filter: [0:v]filter[v_out_temp]; [v_out_temp]format=yuv420p[v_out]
        filter_chain = f"[0:v]{filter_parts[0]}[v_out_temp]; [v_out_temp]format=yuv420p[v_out]"
    else:
        # Multiple filters: chain them with intermediate labels
        filter_chain = f"[0:v]{filter_parts[0]}[tmp0]"

        for i, part in enumerate(filter_parts[1:], start=1):
            if i == len(filter_parts) - 1:
                # Last filter outputs to v_out_temp
                filter_chain += f"; [tmp{i-1}]{part}[v_out_temp]"
            else:
                # Intermediate filter outputs to tmp label
                filter_chain += f"; [tmp{i-1}]{part}[tmp{i}]"

        filter_chain += "; [v_out_temp]format=yuv420p[v_out]"

    return filter_chain


def apply_overlays(
    input_video: str,
    output_video: str,
    channel_id: str,
    script: dict,
    overlays_config_dir: str = "config/overlays",
) -> str:
    """
    Apply Shorts overlays to a video using FFmpeg.

    Applies text overlays (hooks, key benefits, etc.) from YAML config.
    Uses single-pass FFmpeg encoding with audio passthrough (-c:a copy).

    Args:
        input_video: Path to input MP4
        output_video: Path to output MP4 (will be created/overwritten)
        channel_id: Channel identifier (e.g., "money_blueprints")
        script: Dict with template variables:
            - hook_text: Hook text for overlay
            - key_benefit: Key benefit text
            - duration_s: Video duration in seconds
            - accent_color: (optional) Color in 0xRRGGBBAA format
            - channel_name: (optional) Channel name for substitution
        overlays_config_dir: Directory containing overlay YAML files

    Returns:
        Path to output_video (same as input output_video param)

    Raises:
        GraphicsEngineError: If config missing, FFmpeg fails, or invalid config.
        FileNotFoundError: If input video not found.
    """
    # Validate input
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Input video not found: {input_video}")

    # Try to load overlay config (non-fatal if missing)
    overlay_config = _load_overlay_config(channel_id, overlays_config_dir)

    if overlay_config is None:
        # Non-fatal fallback: return input unchanged
        logger.warning(f"No overlays found for {channel_id}, returning input video unchanged")
        return input_video

    overlays = overlay_config.get("overlays", [])

    if not overlays:
        logger.warning("No overlays defined in config, returning input video unchanged")
        return input_video

    # Build filter_complex
    try:
        video_duration = script.get("duration_s", 45)
        accent_color = script.get("accent_color", "0xFF0000FF")

        filter_complex = _build_filter_complex(overlays, script, video_duration, accent_color)

        logger.debug(f"Filter complex: {filter_complex[:100]}...")

    except Exception as e:
        raise GraphicsEngineError(f"Failed to build filter_complex: {e}")

    # Find FFmpeg
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        raise GraphicsEngineError(
            "FFmpeg not found. Install from https://ffmpeg.org/download.html"
        )

    # Build FFmpeg command
    cmd = [
        ffmpeg_path,
        "-i",
        input_video,
        "-filter_complex",
        filter_complex,
        "-map",
        "[v_out]",  # Use filtered video output
        "-map",
        "0:a",  # Copy audio from input
        "-c:v",
        "libx264",
        "-preset",
        "medium",  # Balance speed/quality
        "-crf",
        "23",  # Quality (0-51, lower=better)
        "-c:a",
        "copy",  # Copy audio without re-encoding
        "-y",  # Overwrite output file
        output_video,
    ]

    logger.info(f"Applying overlays to {input_video}...")
    logger.debug(f"FFmpeg command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            error_msg = result.stderr[-500:] if result.stderr else "Unknown error"
            raise GraphicsEngineError(f"FFmpeg failed: {error_msg}")

        if not os.path.exists(output_video):
            raise GraphicsEngineError("Output video file was not created")

        size_mb = os.path.getsize(output_video) / 1024 / 1024
        logger.success(f"Overlays applied: {output_video} ({size_mb:.1f} MB)")

        return output_video

    except subprocess.TimeoutExpired:
        raise GraphicsEngineError("FFmpeg timeout (video processing took too long)")
    except Exception as e:
        raise GraphicsEngineError(f"FFmpeg execution failed: {e}")
