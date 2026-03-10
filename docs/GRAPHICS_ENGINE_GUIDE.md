# Graphics Engine Guide - YouTube Shorts Overlays

## Overview

The Graphics Engine module (`src/content/graphics_engine.py`) applies YouTube Shorts overlays to videos using FFmpeg. It reads overlay configurations from YAML files and applies text overlays with timing, positioning, and styling.

## Module Structure

### Core Files

| File | Purpose |
|------|---------|
| `src/content/graphics_engine.py` | Main graphics engine with FFmpeg integration |
| `src/content/overlay_templates.py` | Pure data module with Python-based overlay configs (fallback) |
| `config/overlays/<channel_id>_overlays.yaml` | YAML overlay configs per channel |

## Key Features

### 1. Template Variable Substitution
Overlays can use template variables that get replaced at runtime:

- `{{ hook_text }}` - Video hook/opening line
- `{{ key_benefit }}` - Main value proposition
- `{{ accent_color }}` - Channel accent color
- `{{ duration_s }}` - Video duration in seconds
- `{{ channel_name }}` - Channel name for branding

### 2. Negative Timing (Relative to End)
Overlays can use negative timing values to position relative to video end:

```yaml
timing_start_s: -5  # 5 seconds before end
timing_end_s: 0     # Until the very end
```

This makes overlay placement independent of video duration.

### 3. FFmpeg Integration
- Single-pass encoding with audio passthrough (`-c:a copy`)
- No re-encoding of audio (preserves quality, saves time)
- Filter-complex chain for applying multiple overlays
- Uses libx264 H.264 codec with medium preset

## Quick Start

### Basic Usage

```python
from src.content.graphics_engine import apply_overlays

output = apply_overlays(
    input_video="video.mp4",
    output_video="video_overlaid.mp4",
    channel_id="money_blueprints",
    script={
        "hook_text": "Wall Street doesn't want you to know...",
        "key_benefit": "Earn $500-$10K/month with AI",
        "duration_s": 45,
    }
)
```

### In Pipeline

The overlays are applied in `run_full_pipeline_demo.py` after video creation:

```python
# Step 4b: Apply Shorts Overlays
overlaid_video = apply_overlays(
    input_video=video_file,
    output_video=overlaid_video_file,
    channel_id="money_blueprints",
    script={
        "hook_text": script["hook"],
        "key_benefit": "Earn $500-$10K/month with AI",
        "duration_s": script.get("duration", 45),
    }
)
```

If overlay YAML is missing, this returns the input file unchanged (non-fatal).

## Configuration Format

### YAML Overlay Config

Create `config/overlays/<channel_id>_overlays.yaml`:

```yaml
overlays:
  - id: hook_text
    type: text
    text: "{{ hook_text }}"
    timing_start_s: 0
    timing_end_s: 3
    fontsize: 72
    fontcolor: "white"
    x: "w/2"           # Center horizontally
    y: "h/4"           # 1/4 down from top
    boxcolor: "0x00000080"  # Semi-transparent black
    boxborderw: 2

  - id: key_benefit
    type: text
    text: "{{ key_benefit }}"
    timing_start_s: 2
    timing_end_s: -2   # 2 seconds before end
    fontsize: 60
    fontcolor: "0xFFD700FF"  # Gold (RGBA hex)
    x: "w/2"
    y: "h*3/4"
    boxcolor: "0x00000080"
    boxborderw: 1
```

### Overlay Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique overlay ID |
| type | string | Yes | "text" (only type supported currently) |
| text | string | Yes | Text content (supports {{ variables }}) |
| timing_start_s | float | Yes | Start time (positive or negative) |
| timing_end_s | float | No | End time (optional, if omitted overlay stays to end) |
| fontsize | int | Yes | Font size in pixels |
| fontcolor | string | Yes | Color name or hex (0xRRGGBBAA format) |
| x | string | Yes | X position (FFmpeg expression, e.g., "w/2" for center) |
| y | string | Yes | Y position (FFmpeg expression, e.g., "h/2" for center) |
| boxcolor | string | No | Background box color (if omitted, no background) |
| boxborderw | int | No | Box border width (default: 0) |

### Position Expressions

Use FFmpeg expressions for positioning:

- `w/2` - Center horizontally (w = width)
- `h/2` - Center vertically (h = height)
- `h/4` - 1/4 down from top
- `h*3/4` - 3/4 down from top
- `10` - 10 pixels from left/top
- `w-100` - 100 pixels from right edge

### Color Format

Colors can be:
- Named colors: "white", "red", "blue", etc.
- Hex RGBA: "0xRRGGBBAA" (e.g., "0xFF0000FF" = red, "0x00000080" = semi-transparent black)

## Fallback Overlay Templates

If YAML file is missing, Python fallback templates are used from `src/content/overlay_templates.py`:

```python
from src.content.overlay_templates import get_overlays_for_channel

overlays = get_overlays_for_channel("money_blueprints")
# Returns: {"overlays": [...]}
```

The templates provide sensible defaults for each channel's niche:
- **money_blueprints**: Gold accent (finance theme)
- **mind_unlocked**: Purple-pink accent (psychology theme)
- **untold_stories**: Dark red accent (storytelling/mystery)
- **neural_forge**: Green accent (tech/hacker theme)
- **prof8ssor_ai**: Blue accent (educational)

## Error Handling

### Non-Fatal (Graceful Degradation)
- Missing YAML file: logs warning, returns input file unchanged
- No overlays defined in YAML: returns input file unchanged
- FFmpeg errors during filter building: raises GraphicsEngineError

### Fatal (Exceptions)
- FFmpeg not found: raises GraphicsEngineError
- Input video file not found: raises FileNotFoundError
- Invalid YAML syntax: raises GraphicsEngineError
- FFmpeg subprocess failure: raises GraphicsEngineError with stderr output

## Integration Points

### 1. Pipeline Integration
- **File**: `run_full_pipeline_demo.py` (Step 4b)
- **Timing**: After video creation, before upload
- **Behavior**: Non-fatal (fails gracefully if overlays missing)

### 2. Uploader Integration
- **File**: `src/youtube/uploader.py` method `upload_video()`
- **New Parameters**:
  - `channel_id`: Channel for loading overlay config
  - `apply_shorts_overlays`: Whether to apply overlays before uploading
  - `hook_text`: Hook text for overlay
  - `key_benefit`: Key benefit text for overlay
- **Behavior**: Applies overlays before uploading (optional)

## Examples

### Example 1: Money Blueprint Channel

**YAML Config** (`config/overlays/money_blueprints_overlays.yaml`):
```yaml
overlays:
  - id: hook
    type: text
    text: "{{ hook_text }}"
    timing_start_s: 0
    timing_end_s: 3
    fontsize: 72
    fontcolor: "white"
    x: "w/2"
    y: "h/4"
    boxcolor: "0x1E3A8A80"  # Dark blue
    boxborderw: 2

  - id: benefit
    type: text
    text: "{{ key_benefit }}"
    timing_start_s: 2
    timing_end_s: -2
    fontsize: 60
    fontcolor: "0xFFD700FF"  # Gold
    x: "w/2"
    y: "h*3/4"
    boxcolor: "0x00000080"
    boxborderw: 1
```

**Usage**:
```python
apply_overlays(
    input_video="video.mp4",
    output_video="video_overlaid.mp4",
    channel_id="money_blueprints",
    script={
        "hook_text": "Passive income secrets Wall Street doesn't want you to know...",
        "key_benefit": "Earn $500-$10K/month with just AI",
        "duration_s": 45,
    }
)
```

**Result**:
- First 3 seconds: White hook text on dark blue background
- 2-43 seconds: Gold benefit text on semi-transparent black
- Both centered, repositioned to fit aspect ratio

### Example 2: Missing YAML (Graceful Fallback)

If `config/overlays/untold_stories_overlays.yaml` doesn't exist:

```python
apply_overlays(
    input_video="story.mp4",
    output_video="story_overlaid.mp4",
    channel_id="untold_stories",
    script={...}
)
```

**Result**:
- Logs: "Overlay config not found: config/overlays/untold_stories_overlays.yaml (will skip overlays)"
- Returns: `"story.mp4"` (input file unchanged)
- Video uploads without overlays (non-fatal)

## Performance

### Encoding Speed
- **Preset**: "medium" (balanced speed/quality)
- **Resolution**: 1920x1080 (YouTube Shorts)
- **Typical time**: 30-60 seconds for 45-second video

### Quality
- **Codec**: H.264/libx264
- **CRF**: 23 (quality 0-51, lower=better)
- **Audio**: Copied without re-encoding (fast)
- **Bitrate**: Default ~5-8 Mbps

### Optimization Tips
- Use simpler text (fewer overlays = faster)
- Avoid complex filter expressions
- Pre-calculate timing if possible
- Consider encoding preset trade-offs

## Troubleshooting

### FFmpeg Not Found
```
GraphicsEngineError: FFmpeg not found. Install from https://ffmpeg.org/download.html
```

**Solution**: Install FFmpeg from https://ffmpeg.org/download.html or use:
```bash
choco install ffmpeg  # Windows with Chocolatey
brew install ffmpeg   # macOS
apt-get install ffmpeg # Linux
```

### Invalid YAML Syntax
```
GraphicsEngineError: Invalid YAML in config/overlays/money_blueprints_overlays.yaml: ...
```

**Solution**: Validate YAML syntax. Common issues:
- Indentation (must use spaces, not tabs)
- Quote strings with special characters
- Use proper YAML list/dict syntax

### Output File Not Created
```
GraphicsEngineError: Output video file was not created
```

**Likely cause**:
- Insufficient disk space
- FFmpeg crash (check stderr for details)
- Invalid filter expression

**Solution**: Check FFmpeg output in logs for error details.

## Future Enhancements

Potential improvements (not yet implemented):

- [ ] Image overlays (not just text)
- [ ] Dynamic positioning based on video content
- [ ] Animation effects (fade in/out, slide)
- [ ] Multiple font support with per-overlay fonts
- [ ] Real-time preview of overlays
- [ ] Overlay templates with design presets
- [ ] A/B testing different overlay styles

## Testing

Run the test suite:

```bash
python test_graphics_engine.py
```

Tests cover:
- Loading channels configuration
- Loading overlay YAML files
- Template variable substitution
- Timing resolution (negative timing)
- FFmpeg filter building

All tests should pass (6/6).

## Limitations

Current implementation notes:

- Only text overlays supported (no images, shapes, etc.)
- Single video track only (no split screens)
- Limited to FFmpeg's drawtext filter capabilities
- No built-in animation/transitions
- Colors must be specified as FFmpeg-compatible hex or names
- No watermark burn-in (use overlays instead)

## Related Files

- `src/content/video_utils.py` - Shared FFmpeg utilities (find_ffmpeg, two_pass_encode)
- `src/content/video_fast.py` - Fast video generator
- `src/youtube/uploader.py` - YouTube upload with optional overlay support
- `run_full_pipeline_demo.py` - Full pipeline with Step 4b overlays

## See Also

- [FFmpeg drawtext Documentation](https://ffmpeg.org/ffmpeg-filters.html#drawtext-1)
- [FFmpeg Filter Documentation](https://ffmpeg.org/ffmpeg-filters.html)
- [YouTube Shorts Best Practices](https://support.google.com/youtube/answer/10059382)
