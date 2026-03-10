# Graphics Engine Quick Start Guide

## 30-Second Overview

The Graphics Engine applies YouTube Shorts overlays (text with positioning, timing, and styling) to videos using FFmpeg.

**Main Function:**
```python
from src.content.graphics_engine import apply_overlays

output = apply_overlays(
    input_video="video.mp4",
    output_video="video_overlaid.mp4",
    channel_id="money_blueprints",
    script={
        "hook_text": "Your hook text here",
        "key_benefit": "Your benefit text here",
        "duration_s": 45,  # Video duration
    }
)
# Returns: path to overlaid video
```

## Key Files

| File | Purpose |
|------|---------|
| `src/content/graphics_engine.py` | Main implementation |
| `src/content/overlay_templates.py` | Python fallback configs |
| `config/overlays/*.yaml` | Channel-specific overlay configs |
| `docs/GRAPHICS_ENGINE_GUIDE.md` | Full documentation |

## Installation

1. **Ensure FFmpeg is installed:**
   ```bash
   ffmpeg -version
   ```
   If not found, install from https://ffmpeg.org/download.html

2. **Verify PyYAML is installed:**
   ```bash
   pip list | grep pyyaml
   ```
   (Already in requirements.txt)

3. **Done!** The module is ready to use.

## Quick Test

Run the test suite to verify everything works:

```bash
python test_graphics_engine.py
```

Expected output: `Total: 6/6 passed`

## Usage Examples

### Example 1: Basic Overlay Application

```python
from src.content.graphics_engine import apply_overlays

# Apply overlays to a video
result = apply_overlays(
    input_video="input.mp4",
    output_video="output_overlaid.mp4",
    channel_id="money_blueprints",
    script={
        "hook_text": "Wall Street doesn't want you to know...",
        "key_benefit": "Earn $500-$10K/month with AI",
        "duration_s": 45,
    }
)

print(f"Output: {result}")
```

### Example 2: In the Pipeline

The graphics engine is already integrated into the pipeline:

```bash
python run_full_pipeline_demo.py
```

This runs Step 4b automatically:
1. Creates video
2. **Applies overlays** ← Graphics Engine
3. Uploads to YouTube with #Shorts tags

### Example 3: Using Python Fallback Templates

If YAML config is missing, Python templates are used automatically:

```python
from src.content.overlay_templates import get_overlays_for_channel

# Get default overlays for a channel
config = get_overlays_for_channel("money_blueprints")
print(f"Overlays: {len(config['overlays'])}")
```

### Example 4: With Uploader

Upload a video with overlays applied:

```python
from src.youtube.uploader import YouTubeUploader

uploader = YouTubeUploader()

result = uploader.upload_video(
    video_file="video.mp4",
    title="My Video Title #Shorts",
    description="Description here",
    tags=["#Shorts", "AI", "money"],
    apply_shorts_overlays=True,         # NEW: Enable overlays
    channel_id="money_blueprints",      # NEW: Channel for overlay config
    hook_text="Hook text from script",  # NEW: For {{ hook_text }}
    key_benefit="Main benefit here",    # NEW: For {{ key_benefit }}
)
```

## Configuration

### Create a Custom Overlay YAML

Create `config/overlays/your_channel_overlays.yaml`:

```yaml
overlays:
  - id: hook
    type: text
    text: "{{ hook_text }}"
    timing_start_s: 0
    timing_end_s: 3
    fontsize: 72
    fontcolor: "white"
    x: "w/2"              # Center horizontally
    y: "h/4"              # 1/4 down from top
    boxcolor: "0x00000080"  # Semi-transparent black background
    boxborderw: 2

  - id: benefit
    type: text
    text: "{{ key_benefit }}"
    timing_start_s: 2
    timing_end_s: -2      # 2 seconds before end
    fontsize: 60
    fontcolor: "0xFFD700FF"  # Gold (RGBA hex)
    x: "w/2"
    y: "h*3/4"
    boxcolor: "0x00000080"
    boxborderw: 1
```

### Template Variables Available

- `{{ hook_text }}` - Video hook/opening line
- `{{ key_benefit }}` - Main value proposition
- `{{ duration_s }}` - Video duration in seconds
- `{{ accent_color }}` - Channel accent color (if provided)
- `{{ channel_name }}` - Channel name (if provided)

### Position Expressions

Use FFmpeg expressions for positioning:

- `w/2` - Center horizontally (w = video width)
- `h/2` - Center vertically (h = video height)
- `h/4` - 1/4 down from top
- `h*3/4` - 3/4 down from top
- `10` - 10 pixels from left/top
- `w-100` - 100 pixels from right edge

### Colors

Specify colors as:
- **Named**: "white", "red", "blue", "black", etc.
- **Hex RGBA**: "0xRRGGBBAA"
  - Example: "0xFF0000FF" = red (opaque)
  - Example: "0x00000080" = black (semi-transparent)

## Error Handling

The module handles errors gracefully:

### Non-Fatal Errors (Continues)
- YAML file missing → Uses Python templates
- No overlays defined → Returns input unchanged
- FFmpeg errors during filter building → Logs warning, skips overlays

### Fatal Errors (Exceptions)
- FFmpeg not found → Install from ffmpeg.org
- Input video missing → Check file path
- Invalid YAML → Check syntax (indentation, quotes)

## Timing Guide

### Positive Timing (From Start)
```yaml
timing_start_s: 0    # Start at beginning
timing_end_s: 3      # End at 3 seconds
```
Shows overlay from 0s to 3s

### Negative Timing (From End)
```yaml
timing_start_s: 2
timing_end_s: -2     # 2 seconds before end
```
For 45s video: shows from 2s to 43s

### Relative to Duration
Negative timing is resolved as: `abs_time = duration + negative_time`

Examples for 45s video:
- `-5` → 40s (5 seconds before end)
- `-2` → 43s (2 seconds before end)
- `0` → 45s (at the very end)

## Performance Tips

1. **Faster encoding**: Use fewer overlays
2. **Better quality**: Stick with default CRF=23
3. **Optimize text**: Keep text simple and short
4. **Test locally**: Test overlays before uploading

## Troubleshooting

### "FFmpeg not found"
```
GraphicsEngineError: FFmpeg not found. Install from https://ffmpeg.org/download.html
```
**Solution**: Install FFmpeg from https://ffmpeg.org/download.html

### "Invalid YAML in config/overlays/..."
```
GraphicsEngineError: Invalid YAML in config/overlays/money_blueprints_overlays.yaml: ...
```
**Solution**: Check YAML syntax:
- Use spaces (not tabs) for indentation
- Quote strings with special characters
- Use proper YAML list/dict syntax

### Overlays not showing in output
**Check**:
1. YAML file exists at `config/overlays/<channel_id>_overlays.yaml`
2. Template variables have values (not empty)
3. Timing is correct (0-based, not 1-based)
4. Coordinates are within video bounds

### FFmpeg encoding slow
**Optimize**:
- Use fewer overlays
- Reduce text size
- Simplify colors
- Use faster preset (trades quality for speed)

## Channel Presets

Default configurations are available for:

| Channel | File | Accent Color |
|---------|------|--------------|
| money_blueprints | `config/overlays/money_blueprints_overlays.yaml` | Gold |
| mind_unlocked | `config/overlays/mind_unlocked_overlays.yaml` | Purple-pink |
| neural_forge | `config/overlays/neural_forge_overlays.yaml` | Green |
| prof8ssor_ai | `config/overlays/prof8ssor_ai_overlays.yaml` | Blue |

## Next Steps

1. **Understand the basics** - Read this file
2. **Learn more** - Read `docs/GRAPHICS_ENGINE_GUIDE.md`
3. **Customize** - Edit YAML files in `config/overlays/`
4. **Test** - Run `python test_graphics_engine.py`
5. **Deploy** - Run `python run_full_pipeline_demo.py`

## API Reference

### apply_overlays()

```python
def apply_overlays(
    input_video: str,                    # Path to input video
    output_video: str,                   # Path to output video
    channel_id: str,                     # Channel ID (e.g., "money_blueprints")
    script: dict,                        # Template variables
    overlays_config_dir: str = "config/overlays"
) -> str:
    """Apply Shorts overlays to a video using FFmpeg.

    Returns: Path to output_video on success or input_video if skipped
    Raises: FileNotFoundError, GraphicsEngineError
    """
```

### get_overlays_for_channel()

```python
def get_overlays_for_channel(channel_id: str) -> dict:
    """Get overlay config for a channel.

    Returns: {"overlays": [...]} from Python templates
    """
```

## Related Files

- Full documentation: `/docs/GRAPHICS_ENGINE_GUIDE.md`
- Implementation details: `/GRAPHICS_ENGINE_IMPLEMENTATION.md`
- Complete summary: `/GRAPHICS_ENGINE_SUMMARY.txt`
- Source code: `src/content/graphics_engine.py`
- Templates: `src/content/overlay_templates.py`

## Support

For detailed help:
1. Check `docs/GRAPHICS_ENGINE_GUIDE.md` (complete reference)
2. Review examples in `test_graphics_engine.py`
3. Check logs for specific error messages
4. Verify YAML syntax with Python: `python -c "import yaml; yaml.safe_load(open('config/overlays/your_channel_overlays.yaml'))"`

---

**Ready to create Shorts with overlays?** Start with `python run_full_pipeline_demo.py`
