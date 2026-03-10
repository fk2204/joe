# Content generation modules
from .audio_processor import AudioProcessor
from .parallel_downloader import BatchDownloadResult, DownloadResult, ParallelDownloader
from .script_validator import (
    ScriptValidator,
    ValidationResult,
    clean_script,
    improve_script,
    validate_script,
)
from .script_writer import ScriptWriter
from .stock_cache import SmartPrefetcher, StockCache
from .subtitles import (
    NICHE_SUBTITLE_STYLES,
    SUBTITLE_STYLES,
    SubtitleCue,
    SubtitleGenerator,
    SubtitlePosition,
    SubtitleTrack,
)
from .thumbnail_generator import ThumbnailGenerator
from .tts import TextToSpeech
from .video_hooks import (
    HookAnimationType,
    HookTemplate,
    HookValidationResult,
    VideoHookGenerator,
    create_hook_generator,
)

# Viral Hooks (Integrated 2026-01-20)
try:
    from .viral_hooks import (
        HookFormula,
        OpenLoop,
        PatternInterrupt,
        ViralHookGenerator,
        enhance_retention,
        generate_viral_hook,
    )

    VIRAL_HOOKS_AVAILABLE = True
except ImportError:
    VIRAL_HOOKS_AVAILABLE = False

# Chatterbox TTS (MIT Licensed, Integrated 2026-01-20)
try:
    from .tts_chatterbox import ChatterboxTTS, generate_chatterbox_speech

    CHATTERBOX_AVAILABLE = True
except ImportError:
    CHATTERBOX_AVAILABLE = False

__all__ = [
    "TextToSpeech",
    "ScriptWriter",
    "AudioProcessor",
    "ScriptValidator",
    "ValidationResult",
    "clean_script",
    "validate_script",
    "improve_script",
    "SubtitleGenerator",
    "SubtitleTrack",
    "SubtitleCue",
    "SubtitlePosition",
    "SUBTITLE_STYLES",
    "NICHE_SUBTITLE_STYLES",
    # Video Hooks
    "VideoHookGenerator",
    "HookTemplate",
    "HookAnimationType",
    "HookValidationResult",
    "create_hook_generator",
    # Viral Hooks (NEW)
    "ViralHookGenerator",
    "HookFormula",
    "OpenLoop",
    "PatternInterrupt",
    "generate_viral_hook",
    "enhance_retention",
    # Chatterbox TTS (NEW)
    "ChatterboxTTS",
    "generate_chatterbox_speech",
    # Thumbnails
    "ThumbnailGenerator",
    # Stock footage caching and prefetching
    "StockCache",
    "SmartPrefetcher",
    # Parallel downloading
    "ParallelDownloader",
    "DownloadResult",
    "BatchDownloadResult",
]
