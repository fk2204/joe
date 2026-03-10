# FFmpeg Overlay Examples - Working Syntax

This document shows real, working FFmpeg drawtext filter examples.

## Basic Overlay (Hook Text)

**Python code:**
```python
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
```

**Generated FFmpeg filter:**
```
drawtext=text='Wall Street doesn'\''t want you to know...':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',format=yuv420p
```

**FFmpeg command:**
```bash
ffmpeg -i video.mp4 \
  -vf "drawtext=text='Wall Street doesn'\''t want you to know...':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',format=yuv420p" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a copy \
  -y video_overlaid.mp4
```

## Multiple Overlays (Hook + Benefit + CTA)

**Configuration (money_blueprints_overlays.yaml):**
```yaml
overlays:
  # Hook: First 3 seconds
  - type: text
    timing_start_s: 0.0
    timing_end_s: 3.0
    text: "{{ hook_text }}"
    fontsize: 54
    fontcolor: "white"
    x: "w/2"
    y: "h/4"
    boxcolor: "0x00d4aaff"
    boxborderw: 2

  # Benefit: Middle section
  - type: text
    timing_start_s: 8.0
    timing_end_s: 14.0
    text: "{{ key_benefit }}"
    fontsize: 44
    fontcolor: "0x00d4aaff"
    x: "w/2"
    y: "h/2"
    boxcolor: "0x000000cc"
    boxborderw: 0

  # CTA: Last 4 seconds
  - type: text
    timing_start_s: -4.0
    timing_end_s: 0
    text: "Follow @money_blueprints"
    fontsize: 40
    fontcolor: "black"
    x: "w/2"
    y: "h*0.85"
    boxcolor: "0x00d4aaff"
    boxborderw: 0
```

**Generated FFmpeg filter (simplified, actual command has escaped quotes):**
```
drawtext=text='Wall Street...':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',\
drawtext=text='Earn $500-$10K/month':fontsize=44:fontcolor=0x00d4aaff:x=w/2:y=h/2:enable='between(t,8,14)',\
drawtext=text='Follow @money_blueprints':fontsize=40:fontcolor=black:x=w/2:y=h*0.85:enable='between(t,41,45)',\
format=yuv420p
```

## Filter Syntax Breakdown

### Hook Overlay (0-3 seconds, top 1/4 of screen)

```
drawtext=
  text='Wall Street doesn'\''t want you to know...'    # Text with escaped quote
  :fontsize=54                                         # Size in pixels
  :fontcolor=white                                     # Color name
  :x=w/2                                              # Center horizontally
  :y=h/4                                              # 1/4 down vertically
  :line_spacing=10                                    # Auto-calculated
  :box=1                                              # Show background box
  :boxcolor=0x00d4aaff                                # Teal background (RGBA)
  :boxborderw=2                                       # 2px border
  :enable='between(t,0,3)'                            # Show 0-3 seconds
```

### Benefit Overlay (8-14 seconds, center)

```
drawtext=
  text='Earn $500-$10K/month'
  :fontsize=44
  :fontcolor=0x00d4aaff                               # Teal text
  :x=w/2
  :y=h/2                                              # Centered vertically
  :box=1
  :boxcolor=0x000000cc                                # Dark semi-transparent
  :boxborderw=0                                       # No border
  :enable='between(t,8,14)'
```

### CTA Overlay (Last 4 seconds, bottom)

```
drawtext=
  text='Follow @money_blueprints'
  :fontsize=40
  :fontcolor=black                                    # Black text
  :x=w/2
  :y=h*0.85                                           # 85% down screen
  :box=1
  :boxcolor=0x00d4aaff                                # Teal background
  :boxborderw=0
  :enable='between(t,41,45)'                          # Last 4 seconds (45-4=41)
```

## Common Positioning Patterns

### Centered Overlays
```
x=w/2                  # Center X
y=h/2                  # Center Y
```

### Top Section (Hook)
```
x=w/2                  # Center
y=h/4                  # 1/4 down (top 25%)
```

### Bottom Section (CTA)
```
x=w/2                  # Center
y=h*0.85               # 85% down (bottom 15%)
```

### Left Side
```
x=w*0.1                # 10% from left
y=h/2                  # Centered vertically
```

### Right Side
```
x=w*0.9                # 90% from left (10% from right)
y=h/2                  # Centered vertically
```

## Color Examples

### Named Colors
```
fontcolor=white
fontcolor=black
fontcolor=red
fontcolor=green
fontcolor=blue
fontcolor=yellow
fontcolor=cyan
fontcolor=magenta
```

### Hex Colors (RGBA)
```
fontcolor=0xFF0000FF       # Red (full alpha)
fontcolor=0xFF000080       # Red (50% transparent)
fontcolor=0x00FF00FF       # Green
fontcolor=0x0000FFFF       # Blue
fontcolor=0xFFFF00FF       # Yellow
fontcolor=0x00d4aaff       # Teal (money_blueprints brand)
```

### Box Background Colors
```
boxcolor=0x00000080        # Black, 50% transparent
boxcolor=0x000000cc        # Black, 80% transparent
boxcolor=0x1E3A8A80        # Dark blue, 50% transparent
boxcolor=0x8B0000A0        # Dark red, 63% transparent
boxcolor=0x00d4aaff        # Teal, fully opaque
```

## Timing Examples

### Show for First 3 Seconds
```
enable='between(t,0,3)'
```

### Show from 2-5 Seconds
```
enable='between(t,2,5)'
```

### Show Last 4 Seconds (45-second video)
```
enable='between(t,41,45)'              # 45 - 4 = 41
```
Or use relative timing:
```
timing_start_s: -4.0                   # Config file
timing_end_s: 0
# Engine converts to: between(t,41,45)
```

### Show Entire Video Except Last 2 Seconds
```
enable='between(t,0,43)'               # 45 - 2 = 43
```

### Advanced: Fade Out Effect
```
# Start at 40s, fade out by 45s
enable='gte(t,40)'                     # Greater than or equal to 40s
# Note: This doesn't fade, just on/off
# For smooth fade, need alpha masking (more complex)
```

## Special Characters in Text

### Single Quote (Apostrophe)
```python
text = "Don't worry"
# In filter, escaped as: 'Don'\''t worry'
# Split: 'Don' \' 't worry'
#        end quote, escaped quote, start quote
```

### Dollar Sign
```python
text = "Earn $500/month"
# In filter: 'Earn $500/month'
# No escaping needed for $ in quotes
```

### Percent Sign
```python
text = "50% profit"
# In filter: '50% profit'
# No escaping needed for % in quotes
```

### Multiple Quotes
```python
text = "Price: \"$100\""
# In filter: 'Price: "\\\"$100\\\""'
# Need backslash escape for inner quotes
```

## Common Issues & Solutions

### Issue: Text Not Appearing
**Solution:** Check the `enable` parameter
```
# Wrong (missing quotes):
enable=between(t,0,3)

# Right:
enable='between(t,0,3)'
```

### Issue: Garbled Special Characters
**Solution:** Properly escape quotes
```
# Wrong:
text='Don't worry'

# Right:
text='Don'\''t worry'
```

### Issue: Box Background Wrong Position
**Solution:** Check x, y coordinates
```
# If text is off-screen, box follows
# Verify: 0 <= x <= w, 0 <= y <= h
x=w/2       # Valid: center
x=w*2       # Invalid: off-screen right
y=h*1.5     # Invalid: off-screen bottom
```

### Issue: Color Looks Wrong
**Solution:** Check RGBA format
```
# Hex colors are RGBA: RR GG BB AA
0x00d4aaff  # Teal: R=00, G=d4, B=aa, A=ff (opaque)
0x00d4aa80  # Same teal but 50% transparent
0xFFFFFFFF  # White, opaque
0x00000000  # Black, fully transparent
```

## Testing Single Overlay

Test with this command to verify filter syntax:

```bash
# Create test video (5 seconds, 1080x1920)
ffmpeg -f lavfi -i color=c=black:s=1080x1920:d=5 \
  -f lavfi -i anullsrc=r=44100:cl=mono:d=5 \
  -c:v libx264 -preset fast -c:a aac -y test.mp4

# Apply hook overlay (0-3 seconds)
ffmpeg -i test.mp4 \
  -vf "drawtext=text='Hook':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',format=yuv420p" \
  -c:v libx264 -preset fast -c:a copy -y test_hook.mp4

# Extract frame at 1 second to verify
ffmpeg -i test_hook.mp4 -ss 1 -vframes 1 frame.jpg
```

If overlay appears in `frame.jpg`, syntax is correct!

## Integration with Python Code

```python
from src.content.graphics_engine import apply_overlays

# Simple usage
result = apply_overlays(
    input_video="input.mp4",
    output_video="output.mp4",
    channel_id="money_blueprints",
    script={
        "hook_text": "Your hook here",
        "key_benefit": "Your benefit here",
        "duration_s": 45,
    }
)

# With custom overlays config directory
result = apply_overlays(
    input_video="input.mp4",
    output_video="output.mp4",
    channel_id="custom_channel",
    script={
        "hook_text": "Custom hook",
        "key_benefit": "Custom benefit",
        "duration_s": 60,
    },
    overlays_config_dir="config/overlays"
)
```

## Performance Tips

1. **Use `format=yuv420p`** - Standard video format, good compatibility
2. **Use `libx264` codec** - H.264, widely supported
3. **Use `preset=medium`** - Balance speed and quality
4. **Use CRF=23** - Standard quality (0=lossless, 51=worst)
5. **Use `-c:a copy`** - Passthrough audio, no re-encoding

Example optimized command:
```bash
ffmpeg -i input.mp4 \
  -vf "drawtext=...,format=yuv420p" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a copy -y output.mp4
```

Processing time: ~1-2 minutes per minute of video (varies by hardware)

## References

- **FFmpeg drawtext filter**: https://ffmpeg.org/ffmpeg-filters.html#drawtext-1
- **Text expansion options**: https://ffmpeg.org/ffmpeg-filters.html#Text-expansion
- **Expression evaluation**: https://ffmpeg.org/ffmpeg-utils.html#Expressions
- **Color syntax**: https://ffmpeg.org/ffmpeg-utils.html#Color

## See Also

- `GRAPHICS_ENGINE_FFmpeg_FIX.md` - Technical details of the fix
- `src/content/overlay_templates.py` - Python overlay templates
- `config/overlays/*.yaml` - Channel-specific overlay configs
