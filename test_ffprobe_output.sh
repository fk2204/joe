#!/bin/bash
# Test script showing how ffprobe validates video resolution
# This demonstrates the validation function's use of ffprobe

echo "=========================================="
echo "FFprobe Output for Video Resolution Check"
echo "=========================================="

VIDEO_FILE="output/video.mp4"

if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: Video file not found: $VIDEO_FILE"
    exit 1
fi

echo ""
echo "Video file: $VIDEO_FILE"
echo ""

echo "1. Full ffprobe output:"
echo "   ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json $VIDEO_FILE"
echo ""

ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json "$VIDEO_FILE"

echo ""
echo ""
echo "2. Interpretation:"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json "$VIDEO_FILE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['streams']:
    w = data['streams'][0]['width']
    h = data['streams'][0]['height']
    aspect = w / h
    print(f'   Width:  {w} px')
    print(f'   Height: {h} px')
    print(f'   Aspect Ratio: {aspect:.4f}')
    print(f'   Expected (9:16): 0.5625')
    print(f'   Match: {aspect:.4f} == 0.5625? {abs(aspect - 0.5625) < 0.01}')
    print()
    if w == 1080 and h == 1920:
        print('   [OK] Correct for YouTube Shorts!')
    else:
        print(f'   [FAIL] Expected 1080x1920, got {w}x{h}')
"

echo ""
echo "=========================================="
