# FFmpeg Overlay Filter Syntax Fix

**Status:** FIXED
**Date:** 2026-03-10
**File:** `src/content/graphics_engine.py`

## Problem

The original FFmpeg filter syntax used complex labeled pads, which had escaping and syntax errors:

```
# OLD (BROKEN):
[0:v]drawtext=...[tmp0]; [tmp0]drawtext=...[tmp1]; [tmp1]format=yuv420p[v_out]
```

Issues:
- Complex escaping of quotes and colons
- Hard to debug filter syntax errors
- Unreliable with multiple overlays
- Used `-filter_complex` with complex pad mapping

## Solution

Simplified to **comma-separated filter syntax** (standard FFmpeg approach):

```
# NEW (FIXED):
drawtext=...,drawtext=...,drawtext=...,format=yuv420p
```

Benefits:
- Clean, simple syntax
- No complex pad labels
- Easy to debug
- Standard FFmpeg -vf usage
- Reliable multi-filter chaining

## Code Changes

### 1. Simplified `_build_filter_complex()` function

**Before:**
```python
# Complex labeled pad syntax with many intermediate labels
filter_chain = f"[0:v]{filter_parts[0]}[tmp0]"
for i, part in enumerate(filter_parts[1:], start=1):
    if i == len(filter_parts) - 1:
        filter_chain += f"; [tmp{i-1}]{part}[v_out_temp]"
    else:
        filter_chain += f"; [tmp{i-1}]{part}[tmp{i}]"
filter_chain += "; [v_out_temp]format=yuv420p[v_out]"
```

**After:**
```python
# Simple comma-separated syntax
if not filter_parts:
    return "format=yuv420p"

filter_chain = ",".join(filter_parts) + ",format=yuv420p"
```

### 2. Updated FFmpeg command

**Before:**
```python
cmd = [
    ffmpeg_path,
    "-i", input_video,
    "-filter_complex", filter_complex,      # Complex with pad labels
    "-map", "[v_out]",                       # Map filtered output
    "-map", "0:a",                           # Map audio
    ...
]
```

**After:**
```python
cmd = [
    ffmpeg_path,
    "-i", input_video,
    "-vf", filter_complex,                   # Simple video filter
    # Removed -map arguments (audio copied with -c:a copy)
    ...
]
```

## Filter Syntax Examples

### Single Hook Overlay (0-3 seconds)

```
drawtext=text='Hook':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',format=yuv420p
```

### Multiple Overlays (Hook + Benefit + CTA)

```
drawtext=text='Hook':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',\
drawtext=text='Earn $500K/month':fontsize=44:fontcolor=0x00d4aaff:x=w/2:y=h/2:enable='between(t,2,43)',\
drawtext=text='Follow @money_blueprints':fontsize=40:fontcolor=black:x=w/2:y=h*0.85:enable='between(t,41,45)',\
format=yuv420p
```

## Key Components Explained

### Text Parameter
```
text='Hook text here'
```
- Use single quotes
- Special characters (apostrophes, quotes) escaped with backslash

### Timing with `enable` Parameter
```
enable='between(t,start,end)'
```
- `t` = current time in seconds
- `between(t,0,3)` = show from 0-3 seconds
- Works with relative timing: `-4` = 4 seconds before end

### Positioning
```
x=w/2              # Center horizontally (w = width)
y=h/4              # 1/4 down vertically (h = height)
y=h*0.85           # 85% down
x=(w-text_w)/2    # Center text (account for text width)
```

### Colors
```
fontcolor=white           # Named colors
fontcolor=0x00d4aaff    # Hex RGB (0xRRGGBBAA)
fontcolor=0xFF0000FF    # Red with full alpha
```

### Box (Background)
```
box=1                      # Enable box background
boxcolor=0x00000080       # Dark semi-transparent
boxborderw=2              # Border width in pixels
```

## Testing

Run the comprehensive test:

```bash
python test_overlay_filters_fixed.py
```

This tests:
1. Simple drawtext filter syntax
2. Chained filters for multiple overlays
3. Template variable substitution
4. Real channel configuration
5. Timing resolution (negative = relative to end)

## Real-World Example

For `money_blueprints` channel with 45-second video:

```
Input:
- Hook: "Wall Street doesn't want you to know..."
- Benefit: "Earn $500-$10K/month"
- CTA: "Follow @money_blueprints"

Generated Filter:
drawtext=text='Wall Street doesn'\''t want you to know...':fontsize=54:fontcolor=white:x=w/2:y=h/4:enable='between(t,0,3)',\
drawtext=text='Earn $500-$10K/month':fontsize=44:fontcolor=0x00d4aaff:x=w/2:y=h/2:enable='between(t,2,43)',\
drawtext=text='Follow @money_blueprints':fontsize=40:fontcolor=black:x=w/2:y=h*0.85:enable='between(t,41,45)',\
format=yuv420p

FFmpeg Command:
ffmpeg -i input.mp4 -vf "drawtext=...,...,...,format=yuv420p" -c:v libx264 -preset medium -crf 23 -c:a copy output.mp4
```

## Troubleshooting

### "Enable expression syntax invalid" error
- Check `between(t,start,end)` format
- Use comma separator, not colon

### Text not appearing
- Verify `enable='between(t,start,end)'` is correct
- Check timing values are within video duration
- Ensure text is not empty after template substitution

### Garbled special characters
- Use single quotes for text: `text='your text'`
- Escape single quotes inside: `text='don'\''t'`
- Test with simple ASCII text first

### "Invalid filter graph" error
- Verify comma separation between filters
- No spaces around commas
- Each filter must have valid syntax
- `format=yuv420p` must be last filter

## Migration Notes

If upgrading from old code:

1. No code changes needed in callers
2. `apply_overlays()` API unchanged
3. Internal filter syntax is transparent to users
4. Configuration files (YAML) remain unchanged

## Performance

- Simpler filter syntax → faster FFmpeg validation
- Single-pass encoding (no change)
- No measurable performance difference
- Better reliability = fewer re-encodes on errors

## Future Improvements

1. Add more filter types:
   - `drawbox` for solid rectangles
   - `drawline` for borders
   - `scale` for zoom effects

2. Support font files:
   - System fonts
   - Custom fonts for branding

3. Animation support:
   - Fade in/out effects
   - Slide transitions
   - Scale animations

4. Color effects:
   - Gradients
   - Color overlays
   - Transparency

## References

- FFmpeg filter documentation: https://ffmpeg.org/ffmpeg-filters.html#Text-expansion-_0028a_002epaste_0029
- drawtext filter: https://ffmpeg.org/ffmpeg-filters.html#drawtext-1
- Filter syntax: https://ffmpeg.org/ffmpeg-filters.html#Filtering-Introduction

## Testing Checklist

- [x] Simple single overlay renders
- [x] Multiple overlays chain correctly
- [x] Timing works (start and end)
- [x] Negative timing (relative to end) works
- [x] Template variables substitute
- [x] Special characters preserved
- [x] Colors work (named and hex)
- [x] Box backgrounds render
- [x] Text positioning correct
- [x] Audio passthrough works

## Deployment

Deploy to production:

1. Update `src/content/graphics_engine.py`
2. No migration needed (API compatible)
3. Test with existing channel configs
4. Monitor first few videos for overlay rendering

All existing overlay configurations (YAML files) remain valid.
