"""
Video Specifications and Standards
Defines all video-related constants for storyboard generation and Phase 5 production.
"""

# ===== ASPECT RATIO =====
# ALL storyboard frames MUST be 16:9 ratio for video production
ASPECT_RATIO = "16:9"
ASPECT_RATIO_DECIMAL = 16 / 9  # 1.777...

# Standard resolutions (all 16:9)
RESOLUTIONS = {
    "4K": (3840, 2160),      # 16:9
    "1080p": (1920, 1080),   # 16:9
    "720p": (1280, 720),     # 16:9
    "480p": (854, 480),      # 16:9
}

# Recommended resolution for AI image generation
RECOMMENDED_RESOLUTION = "1080p"  # 1920x1080
RECOMMENDED_WIDTH = 1920
RECOMMENDED_HEIGHT = 1080

# ===== VIDEO CLIP SPECIFICATIONS =====
# Maximum duration per video clip (AI video generation limitation)
MAX_VIDEO_CLIP_DURATION = 8  # seconds

# Frame rate for final video
FRAME_RATE = 24  # fps (cinematic standard)

# ===== IMAGE GENERATION SPECIFICATIONS =====
IMAGE_QUALITY = "8K quality"  # For prompts
IMAGE_STYLE = "cinematic, photorealistic"

# Critical aspect ratio enforcement for image generation
ASPECT_RATIO_PROMPT = f"""
CRITICAL: Image MUST be exactly {ASPECT_RATIO} aspect ratio ({RECOMMENDED_WIDTH}x{RECOMMENDED_HEIGHT} pixels).
Widescreen cinematic format. NO letterboxing, NO pillarboxing.
Frame composition should fill entire 16:9 rectangle.
"""

# ===== CAMERA SPECIFICATIONS =====
# Standard camera angles maintaining 16:9 frame
CAMERA_ANGLES = {
    "wide": "Wide shot capturing entire scene, 16:9 widescreen frame",
    "medium": "Medium shot waist-up or group, 16:9 widescreen frame",
    "close-up": "Close-up head and shoulders, 16:9 widescreen frame",
    "extreme_close-up": "Extreme close-up face/object detail, 16:9 widescreen frame",
    "over-shoulder": "Over-the-shoulder dialogue shot, 16:9 widescreen frame",
    "insert": "Insert shot of prop/object, 16:9 widescreen frame"
}

# ===== STORYBOARD GRID SPECIFICATIONS =====
# When assembling multiple frames into a storyboard visualization
# Each individual frame is still 16:9, but the grid is for presentation only
STORYBOARD_GRIDS = {
    "4x1": {
        "rows": 4,
        "cols": 1,
        "description": "4 frames vertical, each 16:9"
    },
    "2x3": {
        "rows": 2,
        "cols": 3,
        "description": "6 frames (2 rows × 3 cols), each 16:9"
    },
    "3x3": {
        "rows": 3,
        "cols": 3,
        "description": "9 frames (3×3 grid), each 16:9"
    },
    "4x4": {
        "rows": 4,
        "cols": 4,
        "description": "16 frames (4×4 grid), each 16:9"
    }
}

# ===== VIDEO ASSEMBLY SPECIFICATIONS =====
# For Phase 5 video assembly
VIDEO_CODEC = "h264"
AUDIO_CODEC = "aac"
VIDEO_BITRATE = "5000k"
AUDIO_BITRATE = "192k"

# ===== VALIDATION =====
def validate_aspect_ratio(width: int, height: int, tolerance: float = 0.01) -> bool:
    """
    Validate that dimensions match 16:9 aspect ratio.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        tolerance: Acceptable deviation from exact ratio
    
    Returns:
        True if aspect ratio is valid 16:9
    """
    actual_ratio = width / height
    expected_ratio = ASPECT_RATIO_DECIMAL
    
    deviation = abs(actual_ratio - expected_ratio)
    
    return deviation <= tolerance


def get_image_dimensions(resolution: str = "1080p") -> tuple:
    """
    Get image dimensions for specified resolution.
    
    Args:
        resolution: Resolution name ("4K", "1080p", etc.)
    
    Returns:
        Tuple of (width, height)
    """
    return RESOLUTIONS.get(resolution, RESOLUTIONS["1080p"])


def format_aspect_ratio_prompt() -> str:
    """
    Get formatted aspect ratio requirement for AI image generation prompts.
    
    Returns:
        String to include in all image generation prompts
    """
    return ASPECT_RATIO_PROMPT.strip()
