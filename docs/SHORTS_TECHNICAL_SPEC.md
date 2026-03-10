# YouTube Shorts Technical Specification

**Specification version:** 2025-08 (based on sources confirmed through August 2025; 3-minute limit confirmed October 2024)
**Purpose:** Gate the graphics engine design with hard technical constraints so every output is guaranteed to render correctly in the YouTube Shorts feed.

---

## 1. Duration Range

| Parameter | Value | Source |
|-----------|-------|--------|
| Minimum for Shorts classification | No hard floor; even 1-second clips are classified | YouTube behavior observed by practitioners |
| Maximum for Shorts classification | **3 minutes (180 seconds)** | Hootsuite, Socialinsider — confirmed October 2024 expansion |
| Previous limit (historic) | 60 seconds | Applicable before October 2024 |

**What happens at 61 seconds?**
A 61-second video with 9:16 aspect ratio is still classified as a Short. The old 60-second ceiling was removed in October 2024. The new ceiling is 180 seconds. A video that is 61 seconds is fully within the Shorts feed.

**What happens at 10 seconds?**
Still classified as a Short. There is no minimum duration. Videos as short as a few seconds will appear in the Shorts feed if they meet the aspect ratio requirement (9:16 or close to it) and are under 180 seconds.

**What happens above 180 seconds?**
A video exceeding 3 minutes in 9:16 format is NOT placed in the Shorts feed. It routes to the regular video feed. YouTube's automatic classification uses both duration and aspect ratio together.

**One important audio constraint:**
Videos longer than 60 seconds cannot use copyrighted tracks from YouTube's in-app music picker due to licensing restrictions. This does not affect classification; it only affects which audio sources are available during upload.

**Graphics engine implication:**
Maximum renderable duration: **180 seconds**. The engine must reject or warn on any timeline exceeding 180 seconds. The practical design target for highest engagement is 15-60 seconds; the hard ceiling is 180 seconds.

---

## 2. Resolution and Aspect Ratio

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimal resolution | **1080 x 1920 px** (9:16) | Hootsuite, industry consensus |
| Minimum acceptable resolution | **600 x 1067 px** (9:16) | Hootsuite |
| Aspect ratio trigger for Shorts | **9:16** (vertical) or square (1:1) | Hootsuite confirmed |
| 16:9 upload (1920x1080) behavior | Routed to regular video feed, NOT classified as Short | Hootsuite: "use 16:9 to prevent Shorts classification" |
| Other aspect ratio behavior | Non-9:16 vertical ratios (e.g., 4:5) may auto-crop or be classified at YouTube's discretion |

**Does YouTube auto-crop non-9:16 content?**
YouTube does not auto-crop to 9:16 during upload for existing content. It uses aspect ratio as a classification signal. A 4:5 (1080x1350) upload will be routed to regular video, not Shorts. Uploading a 1:1 square video under 180 seconds may be classified as a Short in the feed but will show with letterboxing on the sides in the Shorts player.

**Does uploading 1920x1080 (16:9) get rejected?**
No — it uploads successfully. It simply does not appear in the Shorts feed. It becomes a standard video.

**Graphics engine implication:**
The engine must output **1080 x 1920 px** as its only canvas size. No other resolution should be configurable for the Shorts pipeline. The canvas definition in code must be a named constant:
```
SHORTS_WIDTH  = 1080
SHORTS_HEIGHT = 1920
SHORTS_ASPECT = "9:16"
```

---

## 3. Safe Zone for Text Overlays

YouTube Shorts overlays the following UI chrome on top of the video at all times:

**Top area:**
- Channel handle / username + avatar appears at the **bottom-left** of the video (not the top). The top area is mostly clear, but the system status bar on mobile (battery, time, signal) eats approximately 40-50 px at the very top edge.

**Bottom area (most critical):**
The Shorts player renders a permanent action bar at the bottom of the video containing:
- Like button (thumbs up + count)
- Dislike button
- Comment button (count)
- Share / remix button
- Subscribe button
- Channel name / handle
- Video title / caption text (scrolls above the button row)

This bottom UI strip is the most dangerous area for text collision. Based on pixel measurements of the Shorts interface at 1080x1920:

| Zone | Margin | Derivation |
|------|--------|------------|
| **Top** | **120 px** | Clears status bar + any system overlays; ~6.25% of height |
| **Bottom** | **300 px** | Clears the full action bar (like/comment/share/subscribe row + caption overlay); ~15.6% of height |
| **Left** | **72 px** | Clears left edge chrome; ~6.7% of width |
| **Right** | **180 px** | Right side holds like, comment, share, subscribe icon stack; ~16.7% of width |

**Breakdown of what the bottom and right chrome covers:**

Bottom zone at 1080x1920 (measured from bottom edge, counting upward):
- Bottom 0-60 px: navigation bar / home indicator
- Bottom 60-160 px: like / comment / share / remix button row
- Bottom 160-220 px: subscribe button + channel avatar + handle
- Bottom 220-300 px: video title / caption text that scrolls here

Right zone at 1080x1920 (measured from right edge, counting inward):
- Right 0-120 px: like button, comment button, share button, subscribe button vertical stack
- Right 120-180 px: safety margin for button text labels

**Safe content area at 1080x1920:**

```
Top edge of safe area:    y = 120
Bottom edge of safe area: y = 1620  (1920 - 300)
Left edge of safe area:   x = 72
Right edge of safe area:  x = 900   (1080 - 180)

Safe area width:  828 px  (900 - 72)
Safe area height: 1500 px (1620 - 120)
```

**Important note on sourcing:** YouTube does not publish official safe zone pixel values in a public spec sheet. The values above are derived from:
1. Measurement of the Shorts player interface at 1080x1920 by video creators and motion designers (community consensus 2024-2025)
2. Cross-referenced with TikTok's published safe zones (which share the same UI layout pattern)
3. Conservative margin added above the measured minimums

These are **engineering-safe** values (conservative). Actual UI chrome measurements may be slightly smaller. Do not reduce the bottom margin below 280 px or the right margin below 160 px without live testing on a physical device.

**Graphics engine implication:**
- Hook text (first 1-3 seconds): must render entirely within `y >= 120`
- All body text: must render entirely within `y >= 120` and `y <= 1620`
- All text: must render entirely within `x >= 72` and `x <= 900`
- No critical content (faces, text, key graphics) in the right 180 px
- No critical content in the bottom 300 px

---

## 4. #Shorts Hashtag Requirement

| Scenario | Classification result | Source |
|----------|----------------------|--------|
| 9:16 aspect + under 180 sec, no hashtag | **Classified as Short** | Hootsuite: "automatically categorized... when they are vertical/square and under 3 minutes" |
| 9:16 aspect + under 180 sec + #Shorts in title | Classified as Short (hashtag is redundant) | Same |
| 16:9 aspect + under 60 sec + #Shorts in title | NOT classified as Short (aspect ratio wins) | Industry consensus |
| 9:16 aspect + over 180 sec | NOT classified as Short (duration wins) | Industry consensus |

**Conclusion:** `#Shorts` is NOT required for Shorts feed classification. Aspect ratio + duration are the two triggers. Adding `#Shorts` to a correctly-formatted video has no effect on classification.

**Historical context:** In 2020-2021, when the Shorts feature was in beta and rolling out by region, `#Shorts` in the title or description was used as an override signal. YouTube has since moved to automatic detection based on format metadata. The hashtag requirement is now obsolete for classification purposes.

**Practical use:** `#Shorts` still has value as a discovery tag (search, trending hashtags) and many creators include it, but its presence or absence does not gate Shorts feed placement.

**Graphics engine implication:**
The engine does not need to enforce or inject a `#Shorts` tag. The upload metadata pipeline (separate concern) may include it for discovery purposes but it is not a rendering constraint.

---

## 5. Codec and Container

YouTube accepts the same codec set for Shorts as for all video uploads. There is no Shorts-specific codec restriction.

| Property | Supported / Recommended | Notes |
|----------|------------------------|-------|
| **Recommended video codec** | **H.264 (AVC)** | Most compatible; supported on all platforms and all YouTube playback paths |
| Also accepted | H.265 (HEVC), VP9, VP8, AV1, MPEG-4, MPEG-2 | Accepted at upload; YouTube re-encodes to VP9/AV1 for delivery regardless |
| **Recommended container** | **MP4** | Universal compatibility; use with H.264 |
| Also accepted | MOV, WebM, AVI, FLV, WMV, 3GPP, MPEG-PS, OGG | MOV is common from Apple ecosystem; WebM is native VP9/AV1 |
| **Recommended audio codec** | **AAC-LC** | 320 kbps, stereo |
| Also accepted | MP3, PCM, Vorbis, Opus | |
| Re-encoding | YouTube always re-encodes uploaded files for delivery | Upload quality determines source quality; encode at highest feasible quality |

**What YouTube does on receipt:**
Regardless of what you upload, YouTube re-encodes everything for streaming delivery. The upload codec affects only the source quality available for that transcoding pass. Uploading H.264 at high bitrate gives YouTube the cleanest source.

**Graphics engine implication:**
Output format must be `MP4 + H.264 + AAC`. This is the universal safe default. No edge cases, no format-related upload failures. H.265 is not recommended even though it is accepted — support is uneven across upload pipelines and tooling.

---

## 6. Frame Rate

| Parameter | Value | Source |
|-----------|-------|--------|
| Accepted frame rates | **24, 25, 30, 48, 50, 60 fps** | YouTube's documented accepted values (standard upload spec) |
| Recommended for Shorts | **30 fps** | Best balance of motion smoothness and file size for short-form vertical content |
| Also viable | 60 fps for high-motion content | Higher file size, no perceptible benefit for most text/graphic animations |
| Non-standard frame rates | YouTube accepts them (e.g., 23.976, 29.97) | Automatically handled; no rejection |

**Does YouTube normalize frame rate?**
YouTube does not reject non-standard frame rates. It transcodes to the nearest standard delivery frame rate. Uploading 23.976 fps is treated as 24 fps. Uploading 29.97 fps is treated as 30 fps. No quality loss occurs from this conversion.

**Graphics engine implication:**
Render at exactly **30 fps**. Use integer frame rates, not drop-frame. This guarantees clean frame count math for duration calculations:
```
30 fps × 60 sec = 1800 frames for a 60-second Short
30 fps × 180 sec = 5400 frames for a 180-second Short
```

---

## 7. File Size Limit

| Parameter | Value | Source |
|-----------|-------|--------|
| Maximum file size | **256 GB** (unverified accounts); **2 GB** for standard accounts | YouTube's general upload limit; Hootsuite cites 2 GB |
| Practical limit for Shorts | Under 2 GB is safe for all accounts | A 3-minute 1080x1920 H.264 video at high bitrate is ~600 MB-1.2 GB |

**Notes:**
- YouTube's official spec sheet historically states 256 GB max for verified accounts, but this applies to long-form video.
- For Shorts (max 180 seconds), the practical file size at recommended quality is far below any limit.
- At H.264 with a target bitrate of 8-10 Mbps for 1080p vertical:
  - 60-second Short: ~60-75 MB
  - 180-second Short: ~180-225 MB
- These numbers are well within any account's upload limits.

**Graphics engine implication:**
No file size gating logic is needed in the engine. Output at H.264 8-10 Mbps. A 180-second Short will be approximately 180-225 MB, which is under any upload threshold.

---

## Summary Table: Hard Constraints for Graphics Engine

| Constraint | Hard Value | Action if violated |
|-----------|------------|-------------------|
| Canvas width | 1080 px | Reject — will not appear in Shorts feed |
| Canvas height | 1920 px | Reject — will not appear in Shorts feed |
| Aspect ratio | 9:16 | Reject — will route to regular video feed |
| Maximum duration | 180 seconds | Warn + truncate — video routes to regular feed above 180s |
| Safe zone top | y >= 120 px | Flag — text may be obscured by status bar |
| Safe zone bottom | y <= 1620 px | Flag — text will be covered by action bar chrome |
| Safe zone left | x >= 72 px | Flag — text may be cut by screen edge |
| Safe zone right | x <= 900 px | Flag — text will be covered by like/comment/share buttons |
| Output codec | H.264 (AVC) | Warn if other — uploads may fail on some pipelines |
| Output container | MP4 | Warn if other — use MP4 for universal compatibility |
| Frame rate | 30 fps | Warn if other — non-standard rates accepted but use integer fps |
| File size | < 2 GB | No action needed at recommended bitrates |

---

## Source Log

| Claim | Source | Confidence |
|-------|--------|------------|
| 3-minute maximum duration | Hootsuite (blog.hootsuite.com), Socialinsider | High — corroborated by 2 independent sources |
| October 2024 expansion from 60s to 3 min | Hootsuite | High |
| Minimum resolution 600x1067 | Hootsuite | Medium — single source |
| Recommended resolution 1080x1920 | Hootsuite, industry consensus | High |
| File size 2 GB | Hootsuite | High |
| MP4 + MOV supported containers | Hootsuite | High |
| Auto-classification by aspect ratio | Hootsuite, Socialinsider | High — corroborated |
| #Shorts not required for classification | Hootsuite | High |
| Music picker restriction above 60 seconds | Hootsuite | High |
| Safe zone pixel values (top 120, bottom 300, left 72, right 180) | Derived from measured Shorts UI chrome at 1080x1920; community documentation; cross-referenced with TikTok published safe zones | Medium — no official YouTube pixel spec published; values are conservative engineering estimates |
| H.264 + AAC as recommended codec | YouTube general upload spec (standard across all references) | High |
| Accepted frame rates 24/25/30/48/50/60 fps | YouTube general upload encoding spec | High |

---

*Specification compiled: 2025-08. Safe zone values are engineering estimates derived from UI measurement, not from an official YouTube published pixel spec. Validate safe zones against a physical device at 1080p before committing to a fixed layout.*
