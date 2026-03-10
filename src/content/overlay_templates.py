"""
Overlay Templates Module - Pure data module with fallback overlay configs.

Provides default overlay configurations for each channel as Python dicts.
Used as fallback if YAML config file is missing.

Format matches the YAML overlay config structure:
{
    "overlays": [
        {
            "id": "unique_id",
            "type": "text",
            "text": "Text with {{template}} variables",
            "timing_start_s": 0,
            "timing_end_s": 5,
            "fontsize": 60,
            "fontcolor": "white",
            "x": "w/2",
            "y": "h/2",
            "boxcolor": "0x00000080",  # RGBA
            "boxborderw": 2
        },
        ...
    ]
}
"""

from typing import Any, Dict


def get_money_blueprints_overlays() -> Dict[str, Any]:
    """
    Get default overlays for money_blueprints channel (Finance niche).

    Returns:
        Dict with overlay configuration.
    """
    return {
        "overlays": [
            {
                "id": "hook_text",
                "type": "text",
                "text": "{{ hook_text }}",
                "timing_start_s": 0,
                "timing_end_s": 3,
                "fontsize": 72,
                "fontcolor": "white",
                "x": "w/2",
                "y": "h/4",
                "boxcolor": "0x00000080",
                "boxborderw": 2,
            },
            {
                "id": "key_benefit",
                "type": "text",
                "text": "{{ key_benefit }}",
                "timing_start_s": 2,
                "timing_end_s": -2,
                "fontsize": 60,
                "fontcolor": "0xFFD700FF",  # Gold
                "x": "w/2",
                "y": "h*3/4",
                "boxcolor": "0x00000080",
                "boxborderw": 1,
            },
            {
                "id": "channel_badge",
                "type": "text",
                "text": "Money Blueprints",
                "timing_start_s": -3,
                "timing_end_s": 0,
                "fontsize": 48,
                "fontcolor": "white",
                "x": "w/2",
                "y": "h/2",
                "boxcolor": "0x1E3A8A80",  # Dark blue background
                "boxborderw": 0,
            },
        ]
    }


def get_mind_unlocked_overlays() -> Dict[str, Any]:
    """
    Get default overlays for mind_unlocked channel (Psychology niche).

    Returns:
        Dict with overlay configuration.
    """
    return {
        "overlays": [
            {
                "id": "hook_text",
                "type": "text",
                "text": "{{ hook_text }}",
                "timing_start_s": 0,
                "timing_end_s": 4,
                "fontsize": 70,
                "fontcolor": "white",
                "x": "w/2",
                "y": "h/3",
                "boxcolor": "0x00000090",
                "boxborderw": 2,
            },
            {
                "id": "key_insight",
                "type": "text",
                "text": "{{ key_benefit }}",
                "timing_start_s": 2,
                "timing_end_s": -3,
                "fontsize": 55,
                "fontcolor": "0xFF6B9DFF",  # Psychology purple-pink
                "x": "w/2",
                "y": "h*2/3",
                "boxcolor": "0x00000080",
                "boxborderw": 1,
            },
        ]
    }


def get_untold_stories_overlays() -> Dict[str, Any]:
    """
    Get default overlays for untold_stories channel (Storytelling niche).

    Returns:
        Dict with overlay configuration.
    """
    return {
        "overlays": [
            {
                "id": "story_title",
                "type": "text",
                "text": "{{ hook_text }}",
                "timing_start_s": 0,
                "timing_end_s": 3,
                "fontsize": 75,
                "fontcolor": "white",
                "x": "w/2",
                "y": "h/4",
                "boxcolor": "0x8B0000A0",  # Dark red for dramatic effect
                "boxborderw": 2,
            },
            {
                "id": "story_detail",
                "type": "text",
                "text": "{{ key_benefit }}",
                "timing_start_s": 2,
                "timing_end_s": -3,
                "fontsize": 50,
                "fontcolor": "0xFFFFFFFF",  # White
                "x": "w/2",
                "y": "h*3/4",
                "boxcolor": "0x00000080",
                "boxborderw": 0,
            },
        ]
    }


def get_neural_forge_overlays() -> Dict[str, Any]:
    """
    Get default overlays for neural_forge channel (Tech/AI niche).

    Returns:
        Dict with overlay configuration.
    """
    return {
        "overlays": [
            {
                "id": "tech_hook",
                "type": "text",
                "text": "{{ hook_text }}",
                "timing_start_s": 0,
                "timing_end_s": 3,
                "fontsize": 68,
                "fontcolor": "0x00FF00FF",  # Bright green (hacker aesthetic)
                "x": "w/2",
                "y": "h/3",
                "boxcolor": "0x00000090",
                "boxborderw": 2,
            },
            {
                "id": "tech_detail",
                "type": "text",
                "text": "{{ key_benefit }}",
                "timing_start_s": 2,
                "timing_end_s": -2,
                "fontsize": 56,
                "fontcolor": "0x00FF00FF",  # Green
                "x": "w/2",
                "y": "h*2/3",
                "boxcolor": "0x00000080",
                "boxborderw": 1,
            },
        ]
    }


def get_prof8ssor_ai_overlays() -> Dict[str, Any]:
    """
    Get default overlays for prof8ssor_ai channel (AI Education niche).

    Returns:
        Dict with overlay configuration.
    """
    return {
        "overlays": [
            {
                "id": "lesson_title",
                "type": "text",
                "text": "{{ hook_text }}",
                "timing_start_s": 0,
                "timing_end_s": 4,
                "fontsize": 70,
                "fontcolor": "white",
                "x": "w/2",
                "y": "h/4",
                "boxcolor": "0x1F2937A0",  # Dark gray educational look
                "boxborderw": 2,
            },
            {
                "id": "learning_point",
                "type": "text",
                "text": "{{ key_benefit }}",
                "timing_start_s": 2,
                "timing_end_s": -3,
                "fontsize": 58,
                "fontcolor": "0x60A5FAFF",  # Light blue (professional)
                "x": "w/2",
                "y": "h*3/4",
                "boxcolor": "0x00000080",
                "boxborderw": 0,
            },
        ]
    }


# Mapping of channel_id to overlay generator function
OVERLAY_GENERATORS = {
    "money_blueprints": get_money_blueprints_overlays,
    "mind_unlocked": get_mind_unlocked_overlays,
    "untold_stories": get_untold_stories_overlays,
    "neural_forge": get_neural_forge_overlays,
    "prof8ssor_ai": get_prof8ssor_ai_overlays,
}


def get_overlays_for_channel(channel_id: str) -> Dict[str, Any]:
    """
    Get overlay config for a channel by ID.

    Args:
        channel_id: Channel identifier (e.g., "money_blueprints")

    Returns:
        Dict with overlay configuration, or empty overlays dict if channel not found.
    """
    generator = OVERLAY_GENERATORS.get(channel_id)

    if generator is None:
        # Return empty overlays for unknown channels
        return {"overlays": []}

    return generator()
