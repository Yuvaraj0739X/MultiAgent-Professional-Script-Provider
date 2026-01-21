"""
Phase 4: Pydantic Models
Complete model definitions for character extraction, voice profiles,
environments, scene analysis, and storyboard planning.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ===== CHARACTER MODELS =====

class CharacterCostume(BaseModel):
    """Costume for a specific scene."""
    scene_heading: str
    clothing: str
    condition: str
    accessories: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class Character(BaseModel):
    """Complete character definition."""
    name: str = Field(description="Character name as appears in dialogue (e.g., 'ARJUN')")
    full_name: str = Field(description="Full character name (e.g., 'Inspector Arjun Rao')")
    age: str = Field(description="Age or age range (e.g., 'mid-40s', '25')")
    gender: str
    ethnicity: Optional[str] = None
    
    # Physical description
    physical_description: str = Field(description="Complete physical description")
    height: Optional[str] = None
    build: str
    face_description: str
    eyes: str
    hair: str
    distinctive_marks: Optional[str] = None
    
    # Character details
    personality_traits: List[str] = Field(default_factory=list)
    scenes_appeared: List[int] = Field(default_factory=list)
    typical_expression: Optional[str] = None


class CharacterExtractionOutput(BaseModel):
    """Output from character extraction node."""
    characters: List[Character]


# ===== VOICE PROFILE MODELS =====

class VoiceCharacteristics(BaseModel):
    """Voice characteristics for a character."""
    pitch: str = Field(description="high/medium/low/medium-low")
    tone: str = Field(description="gravelly/smooth/sharp/warm/cold/etc")
    pace: str = Field(description="fast/moderate/slow/deliberate")
    volume: str = Field(description="quiet/normal/loud")
    distinctive_qualities: List[str] = Field(default_factory=list)


class SpeechPatterns(BaseModel):
    """Speech patterns and verbal habits."""
    formality: str
    sentence_structure: str
    common_phrases: List[str] = Field(default_factory=list)
    verbal_tics: List[str] = Field(default_factory=list)
    slang: str


class EmotionalVoiceVariation(BaseModel):
    """How voice changes in emotional state."""
    pitch: str
    pace: str
    tone: str
    notes: str


class DialogueDelivery(BaseModel):
    """Delivery notes for specific dialogue line."""
    scene: int
    line: str
    context: str
    emotional_state: str
    pitch: str
    pace: str
    volume: str
    tone: str
    emphasis: str
    notes: str


class AIVoiceGenerationProfile(BaseModel):
    """Settings for AI voice generation."""
    recommended_service: str = "ElevenLabs"
    voice_type: str
    stability: float = 0.75
    similarity_boost: float = 0.80
    style_exaggeration: float = 0.30
    speaker_boost: bool = True
    reference_audio_needed: bool = True
    notes: str


class VoiceProfile(BaseModel):
    """Complete voice profile for a character."""
    accent: str
    dialect_notes: str
    voice_characteristics: VoiceCharacteristics
    speech_patterns: SpeechPatterns
    emotional_variations: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Emotional voice variations")
    dialogue_examples: List[DialogueDelivery] = Field(default_factory=list)
    ai_voice_generation_profile: AIVoiceGenerationProfile


# ===== ENVIRONMENT MODELS =====

class EnvironmentFixture(BaseModel):
    """Permanent fixture in an environment."""
    name: str
    description: str
    position: Optional[str] = None


class Environment(BaseModel):
    """Complete environment/location definition."""
    name: str
    type: str = Field(description="interior/exterior")
    category: str = Field(description="residential/commercial/outdoor/etc")
    description: str
    
    # Physical elements
    walls: str
    floor: str
    ceiling: str
    furniture_list: List[str] = Field(default_factory=list)
    fixtures_list: List[str] = Field(default_factory=list)
    
    # Lighting and atmosphere
    default_lighting: str
    light_sources: List[str] = Field(default_factory=list)
    atmosphere: str
    
    # Dimensions
    size: str
    ceiling_height: str
    layout_description: str
    
    # Camera setup for anchor image
    camera_position: str
    camera_coverage: str


# ===== SCENE ANALYSIS MODELS =====

class PropObject(BaseModel):
    """Temporary object/prop in a scene."""
    name: str
    description: str
    importance: str = Field(description="high/medium/low")
    camera_focus: bool = False
    action_with_prop: Optional[str] = None


class ActionBeat(BaseModel):
    """Individual action beat within a scene."""
    description: str
    action: str
    duration: int = Field(description="Duration in seconds")
    characters: List[str] = Field(default_factory=list)
    props: List[str] = Field(default_factory=list)
    suggested_camera_angle: Optional[str] = None


class DialogueSegment(BaseModel):
    """Dialogue segment in a scene."""
    timestamp: str = Field(description="Timestamp in scene (e.g., '0:12')")
    character_name: str
    line_text: str
    emotional_state: str
    delivery_notes: str
    beat_number: Optional[int] = None


class SceneAnalysis(BaseModel):
    """Complete scene analysis output."""
    total_duration: int
    complexity: str = Field(description="simple/medium/complex")
    scene_type: str
    lighting_notes: str
    atmosphere_notes: str
    character_emotions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Character emotional states")
    props: List[PropObject] = Field(default_factory=list)
    action_beats: List[ActionBeat] = Field(default_factory=list)
    dialogue_segments: List[DialogueSegment] = Field(default_factory=list)


# ===== STORYBOARD PLANNING MODELS =====

class StartFrameDetails(BaseModel):
    """Details for start frame (when using start+end frame approach)."""
    character_position: str
    character_pose: str
    description: str


class EndFrameDetails(BaseModel):
    """Details for end frame (when using start+end frame approach)."""
    character_position: str
    character_pose: str
    description: str
    state_change: str = Field(description="What changed from start to end")


class DialogueLine(BaseModel):
    """Dialogue line in a storyboard frame."""
    character: str
    line_text: str
    timestamp: str
    delivery_notes: str
    emotional_state: str


class StoryboardFrame(BaseModel):
    """Individual storyboard frame specification."""
    shot_type: str = Field(description="establishing/character_intro/action/dialogue/reaction/insert/transition/ending")
    camera_angle: str = Field(description="wide/medium/close-up/extreme_close-up/over-shoulder/insert")
    camera_movement: str = Field(description="static/slow_push_in/slow_pull_out/pan_left/pan_right/tilt_up/tilt_down/handheld")
    character_distance: Optional[str] = Field(None, description="far/medium_far/medium/close/extreme_close")
    
    # Aspect ratio (CRITICAL for video production)
    aspect_ratio: str = Field(default="16:9", description="MUST be 16:9 for video production")
    resolution: str = Field(default="1920x1080", description="Recommended resolution for image generation")
    
    description: str
    focus_elements: List[str] = Field(default_factory=list)
    action_beat_number: int
    
    # Character details (if visible)
    character_visible: bool = False
    character_name: Optional[str] = None
    character_pose: Optional[str] = None
    facial_expression: Optional[str] = None
    body_language: Optional[str] = None
    
    # Sequence metadata (START/MIDDLE/END system)
    sequence_type: str = Field(default="standalone", description="standalone/start/middle/end")
    sequence_id: Optional[str] = None
    sequence_position: Optional[int] = None
    sequence_total: Optional[int] = None
    
    # Start+End frame system
    has_end_frame: bool = False
    start_frame_details: Optional[StartFrameDetails] = None
    end_frame_details: Optional[EndFrameDetails] = None
    
    # Dialogue
    has_dialogue: bool = False
    dialogue_lines: Optional[List[DialogueLine]] = None
    
    # Video generation
    estimated_duration: int = Field(description="Duration in seconds")
    video_type: str = Field(description="static/animated/interpolated")
    video_generation_note: str
    interpolate_to_frame: Optional[int] = None  # For sequences
    
    # Image generation
    composition_notes: str
    image_generation_note: str
    
    # Generation strategy (CRITICAL for Phase 5)
    generation_strategy: str = Field(
        default="individual",
        description="individual/composite_grid - how this frame should be generated"
    )
    generation_reason: str = Field(
        default="default",
        description="Why this strategy was chosen"
    )
    composite_group_id: Optional[str] = None  # Links frames in same composite


class VideoClip(BaseModel):
    """Video clip assembly plan."""
    clip_number: int
    source_frames: List[int]
    duration: int
    audio: Optional[Dict[str, Any]] = None
    transition_to_next: str = Field(description="cut/fade/dissolve/end")


class StoryboardPlan(BaseModel):
    """Complete storyboard plan for a scene."""
    format: str = Field(description="3x3/4x1/2x3/4x4/custom")
    total_frames: int
    format_reasoning: str
    frames: List[StoryboardFrame]


# ===== COMPLETE SCENE MODEL =====

class Scene(BaseModel):
    """Complete scene with all analysis and storyboard."""
    scene_number: int
    scene_heading: str
    time_of_day: str
    duration_estimate: int
    complexity: str
    scene_type: str
    
    environment: Dict[str, Any]
    characters_present: List[Dict[str, Any]]
    props: List[Dict[str, Any]]
    action_beats: List[Dict[str, Any]]
    dialogue_segments: List[Dict[str, Any]]
    
    storyboard: Optional[Dict[str, Any]] = None


# ===== OUTPUT MODELS =====

class Phase4Output(BaseModel):
    """Complete Phase 4 output."""
    characters_database: List[Dict[str, Any]]
    environments_database: List[Dict[str, Any]]
    scenes: List[Scene]
    extraction_metadata: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
