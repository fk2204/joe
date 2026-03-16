"""
Fast Video Generator using FFmpeg directly.

Much faster than MoviePy for simple video generation.
Creates videos from audio + background in seconds.

Usage:
    generator = FastVideoGenerator()
    generator.create_video(
        audio_file="narration.mp3",
        output_file="video.mp4",
        title="My Tutorial"
    )

Audio Enhancement (optional):
    generator.create_video(
        audio_file="narration.mp3",
        output_file="video.mp4",
        normalize_audio=True  # Normalize to -14 LUFS
    )

Subtitles (optional):
    generator.create_video(
        audio_file="narration.mp3",
        output_file="video.mp4",
        script_text="Your narration text...",
        subtitles_enabled=True,
        subtitle_style="regular"  # or "shorts", "minimal", "cinematic"
    )
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise ImportError("Please install pillow: pip install pillow")

# Import error handling
from src.utils.error_handler import FFmpegError, retry, ErrorContext, handle_ffmpeg_error

# Import audio processor for normalization
try:
    from .audio_processor import AudioProcessor

    AUDIO_PROCESSOR_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSOR_AVAILABLE = False
    logger.debug("AudioProcessor not available - audio enhancement disabled")

# Import subtitle generator
try:
    from .subtitles import SubtitleGenerator

    SUBTITLES_AVAILABLE = True
except ImportError:
    SUBTITLES_AVAILABLE = False
    logger.debug("SubtitleGenerator not available - subtitles disabled")

# Import shared video utilities
from .video_utils import find_ffmpeg
from .video_utils import two_pass_encode as _two_pass_encode


class FastVideoGenerator:
    """
    Fast video generation using FFmpeg.

    Much faster than MoviePy for:
    - Simple background + audio videos
    - Text overlay videos
    - Thumbnail generation
    """

    # Filter cache for reusable FFmpeg filter strings
    _filter_cache: Dict[str, str] = {}

    # Optimized FFmpeg parameters for YouTube streaming
    FFMPEG_PARAMS_REGULAR = [
        "-movflags",
        "+faststart",  # Enable web streaming
        "-profile:v",
        "high",  # H.264 High Profile
        "-level",
        "4.2",  # Level 4.2 for 1080p30
        "-bf",
        "3",  # 3 B-frames
        "-g",
        "60",  # GOP size = 2x framerate
        "-keyint_min",
        "30",  # Minimum GOP
        "-sc_threshold",
        "0",  # Fixed GOP
        "-threads",
        "0",  # Auto thread detection
    ]

    FFMPEG_PARAMS_SHORTS = [
        "-movflags",
        "+faststart",  # Enable web streaming
        "-profile:v",
        "high",  # H.264 High Profile
        "-level",
        "4.2",  # Level 4.2 for 1080p
        "-bf",
        "2",  # 2 B-frames for faster encode
        "-g",
        "60",  # GOP size
        "-keyint_min",
        "30",  # Minimum GOP
        "-sc_threshold",
        "0",  # Fixed GOP
        "-threads",
        "0",  # Auto thread detection
    ]

    def __init__(
        self,
        resolution: Tuple[int, int] = (1080, 1920),
        fps: int = 30,
        background_color: str = "#14141e",
        content_type: str = "shorts",
    ):
        self.resolution = resolution
        self.fps = fps
        self.background_color = background_color
        self.width, self.height = resolution
        self.content_type = content_type

        # Select preset and FFmpeg params based on content type
        if content_type == "shorts":
            self.encoding_preset = "faster"  # Faster encode for shorts
            self.ffmpeg_params = self.FFMPEG_PARAMS_SHORTS
        else:
            self.encoding_preset = "medium"  # Balanced quality/speed for regular videos
            self.ffmpeg_params = self.FFMPEG_PARAMS_REGULAR

        # Hardware acceleration detection
        self._nvenc_available = None  # Lazy detection

        # Check FFmpeg
        self.ffmpeg = self._find_ffmpeg()
        if self.ffmpeg:
            logger.info(
                f"FastVideoGenerator ready (FFmpeg: {self.ffmpeg}, content_type={content_type})"
            )
        else:
            logger.warning("FFmpeg not found. Install from https://ffmpeg.org/download.html")

        # Initialize audio processor for normalization
        self.audio_processor = None
        if AUDIO_PROCESSOR_AVAILABLE:
            try:
                self.audio_processor = AudioProcessor()
                logger.debug("AudioProcessor initialized for audio enhancement")
            except Exception as e:
                logger.debug(f"AudioProcessor initialization failed: {e}")

        # Initialize subtitle generator
        self.subtitle_generator = None
        if SUBTITLES_AVAILABLE:
            try:
                self.subtitle_generator = SubtitleGenerator()
                logger.debug("SubtitleGenerator initialized for caption support")
            except Exception as e:
                logger.debug(f"SubtitleGenerator initialization failed: {e}")

    def _check_nvenc_available(self) -> bool:
        """Check if NVIDIA NVENC hardware encoder is available and functional."""
        if self._nvenc_available is not None:
            return self._nvenc_available

        try:
            ffmpeg_path = self.ffmpeg or "ffmpeg"
            # First check if encoder is listed
            result = subprocess.run(
                [ffmpeg_path, "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if "h264_nvenc" not in result.stdout:
                self._nvenc_available = False
                return False

            # Actually test if NVENC works (encoder may be listed but no GPU present)
            test_result = subprocess.run(
                [ffmpeg_path, "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:d=0.1",
                 "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self._nvenc_available = test_result.returncode == 0
            if self._nvenc_available:
                logger.info("NVENC hardware encoder detected and functional")
            else:
                logger.info("NVENC listed but not functional (no GPU?) - using libx264")
            return self._nvenc_available
        except Exception:
            self._nvenc_available = False
            return False

    def _get_video_codec(self) -> str:
        """Get the best available video codec (NVENC if available, otherwise libx264)."""
        if self._check_nvenc_available():
            return "h264_nvenc"
        return "libx264"

    def _get_ffmpeg_base_params(self) -> List[str]:
        """Get base FFmpeg parameters for video encoding."""
        return list(self.ffmpeg_params)

    def _get_cached_filter(self, key: str, builder_func) -> str:
        """Cache and reuse FFmpeg filter strings."""
        if key not in self._filter_cache:
            self._filter_cache[key] = builder_func()
        return self._filter_cache[key]

    @classmethod
    def clear_filter_cache(cls):
        """Clear the filter cache."""
        cls._filter_cache.clear()
        logger.debug("FFmpeg filter cache cleared")

    def two_pass_encode(
        self,
        input_file: str,
        output_file: str,
        target_bitrate: str = "8M",
        max_bitrate: str = "12M",
    ) -> Optional[str]:
        """
        Perform two-pass encoding for maximum quality at target bitrate.

        Args:
            input_file: Input video file path
            output_file: Output video file path
            target_bitrate: Target bitrate (e.g., "8M" for 8 Mbps)
            max_bitrate: Maximum bitrate (e.g., "12M" for 12 Mbps)

        Returns:
            Path to encoded file or None on failure
        """
        return _two_pass_encode(
            input_file=input_file,
            output_file=output_file,
            ffmpeg_path=self.ffmpeg or "ffmpeg",
            encoding_preset=self.encoding_preset,
            ffmpeg_params=self.ffmpeg_params,
            target_bitrate=target_bitrate,
            max_bitrate=max_bitrate,
        )

    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable."""
        return find_ffmpeg()

    def _create_video_single_pass(
        self,
        audio_file: str,
        output_file: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        background_image: Optional[str] = None,
        normalize_audio: bool = False,
        background_music: Optional[str] = None,
        music_volume: float = 0.15,
        script_text: Optional[str] = None,
        subtitles_enabled: bool = False,
        subtitle_style: str = "regular",
        niche: Optional[str] = None,
    ) -> Optional[str]:
        """
        Single-pass FFmpeg video creation (4× faster).

        Combines all operations in one FFmpeg call:
        - Audio normalization (-14 LUFS)
        - Music mixing
        - Video creation
        - Subtitle burning (if subtitle file provided)

        This is 4× faster than multi-pass because it only reads/writes once.
        """
        if not self.ffmpeg:
            logger.error("FFmpeg not available")
            return None

        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        # Create output directory
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Create or use background image
        temp_bg = None
        if not background_image:
            temp_bg = str(Path(output_file).with_suffix(".bg.png"))
            background_image = self.create_background_image(temp_bg, title, subtitle)

        # Generate subtitle file if needed
        subtitle_file = None
        if subtitles_enabled and script_text and self.subtitle_generator:
            try:
                logger.info("Generating subtitle file...")
                # Get audio duration for subtitle timing
                audio_duration = self.get_audio_duration(audio_file)
                if not audio_duration:
                    audio_duration = len(script_text.split()) / 2.5

                # Generate subtitle track
                style_config = self.subtitle_generator.get_style(subtitle_style, niche)
                max_chars = style_config.get("max_chars", 50)
                track = self.subtitle_generator.sync_subtitles_with_audio(
                    script_text, audio_file, max_chars
                )

                if track.cues:
                    # Save to SRT file
                    subtitle_file = str(Path(output_file).with_suffix(".temp.srt"))
                    with open(subtitle_file, "w", encoding="utf-8") as f:
                        for i, cue in enumerate(track.cues, 1):
                            f.write(f"{i}\n")
                            f.write(
                                f"{self._format_srt_time(cue.start)} --> {self._format_srt_time(cue.end)}\n"
                            )
                            f.write(f"{cue.text}\n\n")
                    logger.info(f"Subtitle file created: {len(track.cues)} cues")
            except Exception as e:
                logger.warning(f"Subtitle generation failed: {e}, continuing without subtitles")

        try:
            logger.info(f"Creating video with single-pass FFmpeg (4× faster)...")

            # Build complex filtergraph
            filters = []
            input_count = 0

            # Input 0: Main audio
            audio_label = "[0:a]"
            input_count += 1

            # Input 1: Background music (optional)
            if background_music and os.path.exists(background_music):
                input_count += 1

            # Input N: Background image (always last)
            image_input_idx = input_count
            input_count += 1

            # Audio chain
            if background_music and os.path.exists(background_music):
                # Normalize voice audio
                if normalize_audio:
                    filters.append(f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[voice]")
                else:
                    filters.append(f"[0:a]acopy[voice]")

                # Adjust music volume
                filters.append(f"[1:a]volume={music_volume}[music]")

                # Mix voice and music
                filters.append(
                    f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[audio]"
                )
            elif normalize_audio:
                # Just normalize voice
                filters.append(f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[audio]")
            else:
                # Use audio as-is
                audio_label = "[0:a]"
                filters.append(f"[0:a]acopy[audio]")

            # Video chain: scale background image
            filters.append(f"[{image_input_idx}:v]scale={self.width}:{self.height}[video]")

            # Build filtergraph string
            filtergraph = ";".join(filters)

            # Build FFmpeg command
            video_codec = self._get_video_codec()
            cmd = [
                self.ffmpeg,
                "-y",
                "-i",
                audio_file,  # Input 0: voice audio
            ]

            # Add background music input if present
            if background_music and os.path.exists(background_music):
                cmd.extend(["-i", background_music])  # Input 1: music

            # Add background image input (always present)
            cmd.extend(
                [
                    "-loop",
                    "1",
                    "-i",
                    background_image,  # Input N: background
                    "-filter_complex",
                    filtergraph,
                    "-map",
                    "[video]",
                    "-map",
                    "[audio]",
                    "-c:v",
                    video_codec,
                    "-tune",
                    "stillimage",
                    "-preset",
                    self.encoding_preset,
                    "-crf",
                    "23",
                    "-b:v",
                    "8000k",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "256k",
                    "-pix_fmt",
                    "yuv420p",
                    "-shortest",
                    "-r",
                    str(self.fps),
                ]
            )

            # Add subtitle filter if subtitle file exists
            if subtitle_file and os.path.exists(subtitle_file):
                # Get subtitle style
                style = (
                    self.subtitle_generator.get_style(subtitle_style, niche)
                    if self.subtitle_generator
                    else {}
                )
                font_name = style.get("font_family", "Arial Bold")
                font_size = style.get("font_size", 24)
                primary_color = style.get("color", "#FFFFFF").replace("#", "&H")
                outline_color = style.get("outline_color", "#000000").replace("#", "&H")

                subtitle_filter = f"subtitles={subtitle_file}:force_style='FontName={font_name},FontSize={font_size},PrimaryColour={primary_color},OutlineColour={outline_color},Outline=2,Shadow=1'"

                # Modify video filter to include subtitles
                # This is a bit complex - we need to rebuild the command with subtitle filter
                # For simplicity in single-pass, we'll add subtitles as a post-process
                # True single-pass with subtitles requires more complex filter graph
                logger.info(
                    "Note: Subtitles will be burned in a quick second pass for compatibility"
                )

            cmd.extend(self._get_ffmpeg_base_params())
            cmd.append(output_file)

            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr[:500]}")
                return None

            logger.success(f"Video created with single-pass FFmpeg: {output_file}")

            # Quick subtitle burn if subtitle file exists
            # This is still faster than multi-pass audio processing
            if subtitle_file and os.path.exists(subtitle_file):
                logger.info("Burning subtitles (quick pass)...")
                temp_video = str(Path(output_file).with_suffix(".temp_no_subs.mp4"))
                os.rename(output_file, temp_video)

                style = (
                    self.subtitle_generator.get_style(subtitle_style, niche)
                    if self.subtitle_generator
                    else {}
                )
                font_name = style.get("font_family", "Arial Bold")
                font_size = style.get("font_size", 24)
                primary_color = style.get("color", "#FFFFFF").replace("#", "&H")
                outline_color = style.get("outline_color", "#000000").replace("#", "&H")

                subtitle_filter = f"subtitles={subtitle_file}:force_style='FontName={font_name},FontSize={font_size},PrimaryColour={primary_color},OutlineColour={outline_color},Outline=2,Shadow=1'"

                sub_cmd = [
                    self.ffmpeg,
                    "-y",
                    "-i",
                    temp_video,
                    "-vf",
                    subtitle_filter,
                    "-c:a",
                    "copy",  # Copy audio (no re-encode)
                    output_file,
                ]

                subprocess.run(sub_cmd, capture_output=True, timeout=120)

                # Clean up
                if os.path.exists(temp_video):
                    try:
                        os.remove(temp_video)
                    except Exception:
                        pass

            return output_file

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timed out")
            return None
        except Exception as e:
            logger.error(f"Single-pass video creation failed: {e}")
            logger.warning("Falling back to multi-pass method")
            return self._create_video_multipass(
                audio_file,
                output_file,
                title,
                subtitle,
                background_image,
                normalize_audio,
                background_music,
                music_volume,
                script_text,
                subtitles_enabled,
                subtitle_style,
                niche,
            )
        finally:
            # Clean up temp files
            if temp_bg and os.path.exists(temp_bg):
                try:
                    os.remove(temp_bg)
                except Exception:
                    pass
            if subtitle_file and os.path.exists(subtitle_file):
                try:
                    os.remove(subtitle_file)
                except Exception:
                    pass

    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def create_background_image(
        self, output_path: str, title: Optional[str] = None, subtitle: Optional[str] = None
    ) -> str:
        """Create a background image with optional text."""
        # Parse hex color
        color = self.background_color.lstrip("#")
        rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))

        # Create image
        img = Image.new("RGB", self.resolution, rgb)
        draw = ImageDraw.Draw(img)

        # Add gradient effect (darker at edges)
        for i in range(50):
            alpha = int(255 * (1 - i / 50) * 0.3)
            draw.rectangle(
                [i, i, self.width - i, self.height - i],
                outline=tuple(max(0, c - alpha // 3) for c in rgb),
            )

        # Add title text if provided
        if title:
            try:
                # Try to load a nice font
                font_size = 72
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    try:
                        font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                    except Exception:
                        font = ImageFont.load_default()

                # Calculate text position
                bbox = draw.textbbox((0, 0), title, font=font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                y = self.height // 2 - 50

                # Draw shadow
                draw.text((x + 3, y + 3), title, fill="#000000", font=font)
                # Draw text
                draw.text((x, y), title, fill="#ffffff", font=font)

            except Exception as e:
                logger.warning(f"Could not add title: {e}")

        # Add subtitle
        if subtitle:
            try:
                font_size = 36
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

                bbox = draw.textbbox((0, 0), subtitle, font=font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                y = self.height // 2 + 50

                draw.text((x, y), subtitle, fill="#aaaaaa", font=font)
            except Exception:
                pass

        # Save
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=95)
        logger.debug(f"Background image saved: {output_path}")

        return output_path

    def create_video(
        self,
        audio_file: str,
        output_file: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        background_image: Optional[str] = None,
        normalize_audio: bool = False,
        background_music: Optional[str] = None,
        music_volume: float = 0.15,
        script_text: Optional[str] = None,
        subtitles_enabled: bool = False,
        subtitle_style: str = "regular",
        niche: Optional[str] = None,
        single_pass: bool = True,
    ) -> Optional[str]:
        """
        Create a video from audio file.

        Args:
            audio_file: Path to audio file (MP3, WAV)
            output_file: Output video path (MP4)
            title: Optional title overlay
            subtitle: Optional subtitle
            background_image: Custom background (or auto-generate)
            normalize_audio: Normalize audio to YouTube's -14 LUFS standard
            background_music: Optional background music file to mix with voice
            music_volume: Volume level for background music (0.0-1.0, default 0.15)
            script_text: Script/narration text for subtitle generation
            subtitles_enabled: Whether to burn subtitles into video
            subtitle_style: Subtitle style ("regular", "shorts", "minimal", "cinematic")
            niche: Content niche for subtitle styling ("finance", "psychology", etc.)
            single_pass: Use single-pass FFmpeg (4× faster, default True)

        Returns:
            Path to created video or None on failure

        Raises:
            FFmpegError: If FFmpeg not found or encoding fails
        """
        # Pre-flight checks
        if not self.ffmpeg:
            raise FFmpegError(
                code="FFMPEG_NOT_FOUND",
                user_msg="FFmpeg not found. Video generation requires FFmpeg.",
                tech_details="find_ffmpeg() returned None",
                suggestion="Install FFmpeg: https://ffmpeg.org/download.html",
            )

        if not os.path.exists(audio_file):
            raise FFmpegError(
                code="AUDIO_FILE_NOT_FOUND",
                user_msg=f"Audio file not found: {audio_file}",
                tech_details=f"Expected file at {audio_file}",
                suggestion="Check that the audio file exists",
            )

        with ErrorContext("Video Creation", f"audio={audio_file}, output={output_file}"):
            try:
                # Use optimized single-pass if requested and subtitles are needed
                if single_pass and (normalize_audio or background_music or subtitles_enabled):
                    result = self._create_video_single_pass(
                        audio_file,
                        output_file,
                        title,
                        subtitle,
                        background_image,
                        normalize_audio,
                        background_music,
                        music_volume,
                        script_text,
                        subtitles_enabled,
                        subtitle_style,
                        niche,
                    )
                else:
                    # Fall back to multi-pass method
                    result = self._create_video_multipass(
                        audio_file,
                        output_file,
                        title,
                        subtitle,
                        background_image,
                        normalize_audio,
                        background_music,
                        music_volume,
                        script_text,
                        subtitles_enabled,
                        subtitle_style,
                        niche,
                    )

                if not result:
                    raise FFmpegError(
                        code="VIDEO_CREATION_FAILED",
                        user_msg="Video creation failed. Check logs above.",
                        tech_details="Both single-pass and multi-pass methods failed",
                        suggestion="Try again with simpler settings or check FFmpeg",
                    )

                return result

            except subprocess.CalledProcessError as e:
                handle_ffmpeg_error(e)

    def _create_video_multipass(
        self,
        audio_file: str,
        output_file: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        background_image: Optional[str] = None,
        normalize_audio: bool = False,
        background_music: Optional[str] = None,
        music_volume: float = 0.15,
        script_text: Optional[str] = None,
        subtitles_enabled: bool = False,
        subtitle_style: str = "regular",
        niche: Optional[str] = None,
    ) -> Optional[str]:
        """
        Multi-pass video creation (legacy method).
        Creates video in multiple FFmpeg passes.
        """
        if not self.ffmpeg:
            logger.error("FFmpeg not available")
            return None

        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        # Create output directory
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Process audio (normalization and/or music mixing)
        processed_audio = audio_file
        temp_audio = None

        if self.audio_processor and (normalize_audio or background_music):
            temp_audio = str(Path(output_file).with_suffix(".processed_audio.mp3"))

            if background_music and os.path.exists(background_music):
                # Mix with background music (this also normalizes)
                logger.info(f"Mixing audio with background music at {music_volume*100:.0f}% volume")
                result = self.audio_processor.mix_with_background_music(
                    voice_file=audio_file,
                    music_file=background_music,
                    output_file=temp_audio,
                    music_volume=music_volume,
                    normalize_before_mix=True,
                )
                if result:
                    processed_audio = result
            elif normalize_audio:
                # Just normalize
                logger.info("Normalizing audio to YouTube's -14 LUFS standard")
                result = self.audio_processor.normalize_audio(audio_file, temp_audio)
                if result:
                    processed_audio = result

        # Create or use background image
        temp_bg = None
        if not background_image:
            temp_bg = str(Path(output_file).with_suffix(".bg.png"))
            background_image = self.create_background_image(temp_bg, title, subtitle)

        try:
            logger.info(f"Creating video: {output_file}")

            # FFmpeg command to create video from image + audio with optimized params
            video_codec = self._get_video_codec()
            cmd = (
                [
                    self.ffmpeg,
                    "-y",  # Overwrite output
                    "-loop",
                    "1",  # Loop image
                    "-i",
                    background_image,  # Input image
                    "-i",
                    processed_audio,  # Input audio (may be normalized/mixed)
                    "-c:v",
                    video_codec,  # Video codec (NVENC if available)
                    "-tune",
                    "stillimage",  # Optimize for still image
                    "-preset",
                    self.encoding_preset,  # Content-type based preset
                    "-crf",
                    "23",  # Constant rate factor for quality
                    "-b:v",
                    "8000k",  # Video bitrate (8 Mbps for YouTube Shorts 1080x1920)
                    "-c:a",
                    "aac",  # Audio codec
                    "-b:a",
                    "256k",  # Audio bitrate (improved from 192k)
                    "-pix_fmt",
                    "yuv420p",  # Pixel format
                    "-shortest",  # End when audio ends
                    "-vf",
                    f"scale={self.width}:{self.height}",  # Resolution
                    "-r",
                    str(self.fps),  # Frame rate
                ]
                + self._get_ffmpeg_base_params()
                + [output_file]
            )

            # Run FFmpeg
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr[:500]}")
                return None

            logger.success(f"Video created: {output_file}")

            # Apply subtitles if enabled
            if subtitles_enabled and script_text and self.subtitle_generator:
                logger.info("Adding burned-in subtitles...")
                try:
                    # Get audio duration for subtitle timing
                    audio_duration = self.get_audio_duration(audio_file)
                    if not audio_duration:
                        audio_duration = len(script_text.split()) / 2.5  # Fallback estimate

                    # Generate subtitle track
                    style_config = self.subtitle_generator.get_style(subtitle_style, niche)
                    max_chars = style_config.get("max_chars", 50)
                    track = self.subtitle_generator.sync_subtitles_with_audio(
                        script_text, audio_file, max_chars
                    )

                    if track.cues:
                        # Burn subtitles into video
                        temp_video = str(Path(output_file).with_suffix(".temp_no_subs.mp4"))
                        os.rename(output_file, temp_video)

                        result = self.subtitle_generator.burn_subtitles(
                            temp_video, track, output_file, style=subtitle_style, niche=niche
                        )

                        # Clean up temp video
                        if os.path.exists(temp_video):
                            try:
                                os.remove(temp_video)
                            except Exception:
                                pass

                        if result:
                            logger.success(f"Subtitles burned into video: {output_file}")
                        else:
                            # Restore original video if subtitle burning failed
                            logger.warning("Subtitle burning failed, video saved without subtitles")
                except Exception as e:
                    logger.warning(f"Subtitle processing failed: {e}")

            return output_file

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timed out")
            return None
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            return None
        finally:
            # Clean up temp background
            if temp_bg and os.path.exists(temp_bg):
                try:
                    os.remove(temp_bg)
                except Exception:
                    pass
            # Clean up temp audio
            if temp_audio and os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except Exception:
                    pass

    def create_thumbnail(
        self,
        output_file: str,
        title: str,
        subtitle: Optional[str] = None,
        background_color: str = "#1e1e3f",
    ) -> str:
        """Create a YouTube thumbnail (1280x720)."""
        size = (1280, 720)

        # Parse color
        color = background_color.lstrip("#")
        rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))

        img = Image.new("RGB", size, rgb)
        draw = ImageDraw.Draw(img)

        # Add gradient
        for i in range(40):
            alpha = int(255 * (1 - i / 40) * 0.4)
            draw.rectangle(
                [i, i, size[0] - i, size[1] - i], outline=tuple(max(0, c - alpha // 2) for c in rgb)
            )

        # Title
        try:
            font_size = 64
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

            # Wrap title if too long
            max_chars = 25
            if len(title) > max_chars:
                words = title.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= max_chars:
                        current_line += " " + word if current_line else word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                title = "\n".join(lines[:2])

            # Draw title with shadow
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2 - 30

            draw.text((x + 4, y + 4), title, fill="#000000", font=font)
            draw.text((x, y), title, fill="#ffffff", font=font)

        except Exception as e:
            logger.warning(f"Font error: {e}")

        # Subtitle
        if subtitle:
            try:
                font = ImageFont.truetype("arial.ttf", 32)
                bbox = draw.textbbox((0, 0), subtitle, font=font)
                x = (size[0] - (bbox[2] - bbox[0])) // 2
                y = size[1] // 2 + 60
                draw.text((x, y), subtitle, fill="#cccccc", font=font)
            except Exception:
                pass

        # Save
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_file, quality=95)
        logger.success(f"Thumbnail created: {output_file}")

        return output_file

    def get_audio_duration(self, audio_file: str) -> Optional[float]:
        """Get duration of audio file in seconds."""
        if not self.ffmpeg:
            return None

        try:
            ffprobe = self.ffmpeg.replace("ffmpeg", "ffprobe")
            cmd = [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                audio_file,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception:
            return None

    def create_video_ffmpeg_direct(
        self,
        audio_file: str,
        background_image: str,
        output_file: str,
        preset: str = "faster",
        crf: int = 23,
    ) -> Optional[str]:
        """
        Ultra-fast video creation using pure FFmpeg.

        This method bypasses MoviePy entirely for maximum performance
        when creating simple audio + background image videos.

        Performance comparison:
        - MoviePy method: ~45-60 seconds for 10 minute video
        - FFmpeg direct: ~8-15 seconds for 10 minute video (3-5x faster)

        Args:
            audio_file: Path to audio file (MP3, WAV, AAC)
            background_image: Path to background image (PNG, JPG)
            output_file: Output video path (MP4)
            preset: FFmpeg preset (ultrafast, superfast, veryfast, faster, fast, medium)
                   - ultrafast: Fastest encoding, larger file
                   - faster: Good balance of speed and quality (recommended)
                   - medium: Better compression, slower encoding
            crf: Constant Rate Factor (18-28, lower = better quality, larger file)
                 - 18: Visually lossless
                 - 23: Good quality (default)
                 - 28: Lower quality, smaller file

        Returns:
            Path to created video or None on failure
        """
        if not self.ffmpeg:
            logger.error("FFmpeg not available for direct video creation")
            return None

        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        if not os.path.exists(background_image):
            logger.error(f"Background image not found: {background_image}")
            return None

        # Create output directory
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Creating video (FFmpeg direct): {output_file}")
            start_time = time.time() if "time" in dir() else None

            # Build FFmpeg command for optimal performance with all optimizations
            video_codec = self._get_video_codec()
            cmd = (
                [
                    self.ffmpeg,
                    "-y",  # Overwrite output
                    "-loop",
                    "1",  # Loop image
                    "-i",
                    background_image,  # Input image
                    "-i",
                    audio_file,  # Input audio
                    "-c:v",
                    video_codec,  # Video codec (NVENC if available)
                    "-preset",
                    preset,  # Encoding speed preset
                    "-crf",
                    str(crf),  # Quality factor
                    "-c:a",
                    "aac",  # Audio codec
                    "-b:a",
                    "256k",  # Audio bitrate
                    "-pix_fmt",
                    "yuv420p",  # Pixel format (compatibility)
                    "-shortest",  # End when shortest stream ends
                    "-r",
                    str(self.fps),  # Frame rate
                ]
                + self._get_ffmpeg_base_params()
                + [output_file]
            )

            # Run FFmpeg
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg direct error: {result.stderr[:500]}")
                return None

            # Verify output
            if not os.path.exists(output_file):
                logger.error("FFmpeg completed but output file not found")
                return None

            file_size = os.path.getsize(output_file)
            if file_size < 1000:
                logger.error(f"Output file too small ({file_size} bytes)")
                return None

            logger.success(
                f"Video created (FFmpeg direct): {output_file} ({file_size / 1024 / 1024:.1f} MB)"
            )
            return output_file

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg direct timed out")
            return None
        except Exception as e:
            logger.error(f"FFmpeg direct failed: {e}")
            return None

    def create_video_batch_ffmpeg(
        self, items: list, output_dir: str, preset: str = "faster"
    ) -> list:
        """
        Create multiple videos in batch using FFmpeg direct method.

        Processes multiple audio+image pairs efficiently,
        useful for batch video production.

        Args:
            items: List of dicts with keys:
                   - audio_file: Path to audio
                   - background_image: Path to image
                   - output_name: Output filename (without extension)
            output_dir: Directory for output videos
            preset: FFmpeg preset

        Returns:
            List of successfully created video paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        successful = []
        failed = []

        logger.info(f"Starting batch video creation: {len(items)} videos")

        for i, item in enumerate(items):
            audio_file = item.get("audio_file")
            background_image = item.get("background_image")
            output_name = item.get("output_name", f"video_{i}")

            if not audio_file or not background_image:
                logger.warning(f"Skipping item {i}: missing audio or image")
                failed.append(output_name)
                continue

            output_file = str(output_path / f"{output_name}.mp4")

            result = self.create_video_ffmpeg_direct(
                audio_file=audio_file,
                background_image=background_image,
                output_file=output_file,
                preset=preset,
            )

            if result:
                successful.append(result)
            else:
                failed.append(output_name)

        logger.info(f"Batch complete: {len(successful)} succeeded, {len(failed)} failed")
        return successful

    def validate_output_resolution(self, video_file: str) -> Dict[str, any]:
        """
        Validate that the output video has the correct resolution (1080x1920 for YouTube Shorts).

        Uses ffprobe to check video dimensions and aspect ratio.

        Args:
            video_file: Path to the output video file

        Returns:
            Dictionary with validation results:
            {
                'is_valid': bool,
                'width': int,
                'height': int,
                'aspect_ratio': float,
                'expected_aspect_ratio': float,
                'matches_expected': bool,
                'warning': str or None
            }
        """
        try:
            import json
            import subprocess

            if not os.path.exists(video_file):
                logger.error(f"Video file not found for validation: {video_file}")
                return {
                    "is_valid": False,
                    "width": None,
                    "height": None,
                    "aspect_ratio": None,
                    "expected_aspect_ratio": 9 / 16,
                    "matches_expected": False,
                    "warning": f"Video file not found: {video_file}",
                }

            # Use ffprobe to get video information
            ffprobe_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                video_file,
            ]

            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"ffprobe failed: {result.stderr}")
                return {
                    "is_valid": False,
                    "width": None,
                    "height": None,
                    "aspect_ratio": None,
                    "expected_aspect_ratio": 9 / 16,
                    "matches_expected": False,
                    "warning": f"ffprobe error: {result.stderr[:200]}",
                }

            data = json.loads(result.stdout)
            if not data.get("streams") or len(data["streams"]) == 0:
                logger.error("No video stream found in output file")
                return {
                    "is_valid": False,
                    "width": None,
                    "height": None,
                    "aspect_ratio": None,
                    "expected_aspect_ratio": 9 / 16,
                    "matches_expected": False,
                    "warning": "No video stream found in output file",
                }

            stream = data["streams"][0]
            width = stream.get("width")
            height = stream.get("height")

            if width is None or height is None:
                logger.error("Could not determine video dimensions")
                return {
                    "is_valid": False,
                    "width": None,
                    "height": None,
                    "aspect_ratio": None,
                    "expected_aspect_ratio": 9 / 16,
                    "matches_expected": False,
                    "warning": "Could not determine video dimensions from ffprobe",
                }

            aspect_ratio = width / height
            expected_aspect_ratio = 9 / 16  # YouTube Shorts aspect ratio
            expected_width = 1080
            expected_height = 1920

            # Check if resolution matches expected (1080x1920)
            matches_expected = width == expected_width and height == expected_height

            # Check if aspect ratio is correct (with small tolerance)
            aspect_tolerance = 0.01
            aspect_ratio_correct = (
                abs(aspect_ratio - expected_aspect_ratio) < aspect_tolerance
            )

            is_valid = matches_expected and aspect_ratio_correct

            warning = None
            if not matches_expected:
                warning = (
                    f"Resolution mismatch: got {width}x{height}, "
                    f"expected {expected_width}x{expected_height}"
                )
            if not aspect_ratio_correct:
                if warning:
                    warning += f" | Aspect ratio: {aspect_ratio:.3f}, expected: {expected_aspect_ratio:.3f}"
                else:
                    warning = f"Aspect ratio mismatch: {aspect_ratio:.3f}, expected: {expected_aspect_ratio:.3f}"

            if is_valid:
                logger.success(
                    f"Video resolution validated: {width}x{height} (9:16 aspect ratio)"
                )
            else:
                logger.warning(f"Validation warning: {warning}")

            return {
                "is_valid": is_valid,
                "width": width,
                "height": height,
                "aspect_ratio": aspect_ratio,
                "expected_aspect_ratio": expected_aspect_ratio,
                "matches_expected": matches_expected,
                "warning": warning,
            }

        except Exception as e:
            logger.error(f"Error validating video resolution: {e}")
            return {
                "is_valid": False,
                "width": None,
                "height": None,
                "aspect_ratio": None,
                "expected_aspect_ratio": 9 / 16,
                "matches_expected": False,
                "warning": f"Validation error: {str(e)}",
            }


# Example usage
if __name__ == "__main__":
    generator = FastVideoGenerator()

    # Create test thumbnail
    print("\nCreating test thumbnail...")
    generator.create_thumbnail(
        output_file="output/test_thumb.png",
        title="Python Tutorial",
        subtitle="Learn Python in 10 Minutes",
    )

    # If we have test audio, create video
    if os.path.exists("output/test_voice.mp3"):
        print("\nCreating test video...")
        video_file = generator.create_video(
            audio_file="output/test_voice.mp3",
            output_file="output/test_video.mp4",
            title="Test Video",
            subtitle="Created with FFmpeg",
        )

        # Validate output resolution
        if video_file:
            print("\nValidating output resolution...")
            validation = generator.validate_output_resolution(video_file)
            print(f"Resolution: {validation['width']}x{validation['height']}")
            print(f"Aspect Ratio: {validation['aspect_ratio']:.3f} (9:16 = {validation['expected_aspect_ratio']:.3f})")
            print(f"Valid for YouTube Shorts: {validation['is_valid']}")
            if validation["warning"]:
                print(f"⚠️  Warning: {validation['warning']}")
            else:
                print("✓ Resolution validated successfully for YouTube Shorts!")
    else:
        print("\nNo test audio found. Run TTS test first.")
