from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime



class Scene(BaseModel):
    """
    Individual scene structure for screenplay.
    
    Represents a single scene with location, time, characters, and action.
    """
    scene_number: int = Field(
        ...,
        description="Scene number in sequence (1, 2, 3, ...)",
        ge=1
    )
    
    location: str = Field(
        ...,
        description="Scene location in Fountain format (e.g., 'INT. NAPOLEON'S TENT - NIGHT')",
        min_length=1
    )
    
    time: str = Field(
        ...,
        description="Time of day (DAY, NIGHT, DAWN, DUSK, etc.)",
        min_length=1
    )
    
    description: str = Field(
        ...,
        description="Brief description of what happens in this scene",
        min_length=10
    )
    
    characters: List[str] = Field(
        ...,
        description="List of characters appearing in this scene",
        min_items=1
    )
    
    key_action: str = Field(
        ...,
        description="The main action or turning point in this scene",
        min_length=10
    )
    
    estimated_duration: int = Field(
        ...,
        description="Estimated scene duration in seconds (typically 30-120)",
        ge=10,
        le=300
    )
    
    act: Optional[int] = Field(
        None,
        description="Which act this scene belongs to (1, 2, or 3)",
        ge=1,
        le=3
    )
    
    emotional_tone: Optional[str] = Field(
        None,
        description="Emotional tone of the scene (tense, hopeful, tragic, etc.)"
    )


class SceneBreakdown(BaseModel):
    """
    Complete scene breakdown for the screenplay.
    
    Contains all scenes in order with total metadata.
    """
    scenes: List[Scene] = Field(
        ...,
        description="List of all scenes in order",
        min_items=5,
        max_items=50
    )
    
    total_scenes: int = Field(
        ...,
        description="Total number of scenes",
        ge=5
    )
    
    estimated_total_duration: int = Field(
        ...,
        description="Total estimated duration in minutes",
        ge=5,
        le=60
    )
    
    act_breakdown: Optional[List[int]] = Field(
        None,
        description="Number of scenes in each act [act1, act2, act3]",
        min_items=3,
        max_items=3
    )
    
    notes: Optional[str] = Field(
        None,
        description="Any notes about the scene breakdown structure"
    )



class ScreenplayMetadata(BaseModel):
    """
    Metadata about the generated screenplay.
    
    Contains statistics and information about the screenplay.
    """
    page_count: int = Field(
        ...,
        description="Number of pages in the screenplay",
        ge=5,
        le=50
    )
    
    estimated_duration: int = Field(
        ...,
        description="Estimated runtime in minutes (1 page ≈ 1 minute)",
        ge=5,
        le=60
    )
    
    scene_count: int = Field(
        ...,
        description="Total number of scenes",
        ge=5
    )
    
    character_count: int = Field(
        ...,
        description="Total number of unique characters",
        ge=1
    )
    
    location_count: int = Field(
        ...,
        description="Total number of unique locations",
        ge=1
    )
    
    locations: List[str] = Field(
        ...,
        description="List of all unique locations used",
        min_items=1
    )
    
    characters: List[str] = Field(
        ...,
        description="List of all unique characters",
        min_items=1
    )
    
    generation_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When the screenplay was generated (ISO format)"
    )
    
    historical_accuracy: Optional[str] = Field(
        None,
        description="'verified' if based on Phase 2 research, None if fictional"
    )
    
    genre: Optional[str] = Field(
        None,
        description="Genre classification (drama, action, historical, etc.)"
    )
    
    tone: Optional[str] = Field(
        None,
        description="Overall tone (serious, lighthearted, dark, etc.)"
    )


class ScreenplayOutput(BaseModel):
    """
    Complete screenplay output.
    
    Contains the full screenplay text in Fountain format plus metadata.
    """
    screenplay_text: str = Field(
        ...,
        description="Full screenplay in Fountain format",
        min_length=1000
    )
    
    metadata: ScreenplayMetadata = Field(
        ...,
        description="Metadata about the screenplay"
    )
    
    generation_notes: str = Field(
        default="",
        description="Any notes about the generation process"
    )



class ValidationResult(BaseModel):
    """
    Screenplay format validation result.
    
    Contains validation status, errors, warnings, and compliance score.
    """
    is_valid: bool = Field(
        ...,
        description="Whether the screenplay passes validation"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="Critical errors that prevent valid Fountain format"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical issues that should be reviewed"
    )
    
    compliance_score: float = Field(
        ...,
        description="Overall compliance score (0-100)",
        ge=0.0,
        le=100.0
    )
    
    format_checks: Optional[dict] = Field(
        None,
        description="Detailed results of specific format checks"
    )
    
    recommendations: Optional[List[str]] = Field(
        None,
        description="Recommendations for improvement"
    )



class RefinementChange(BaseModel):
    """
    A single refinement change made to the screenplay.
    """
    change_type: str = Field(
        ...,
        description="Type of change (format_fix, dialogue_improvement, etc.)"
    )
    
    location: str = Field(
        ...,
        description="Where the change was made (scene number or description)"
    )
    
    description: str = Field(
        ...,
        description="Description of what was changed"
    )
    
    before: Optional[str] = Field(
        None,
        description="Text before the change (if applicable)"
    )
    
    after: Optional[str] = Field(
        None,
        description="Text after the change (if applicable)"
    )


class RefinementOutput(BaseModel):
    """
    Output from the refinement node.
    
    Contains the refined screenplay and list of changes made.
    """
    refined_screenplay: str = Field(
        ...,
        description="Refined screenplay text in Fountain format",
        min_length=1000
    )
    
    changes_made: List[RefinementChange] = Field(
        ...,
        description="List of all changes made during refinement",
        min_items=1
    )
    
    total_changes: int = Field(
        ...,
        description="Total number of changes made",
        ge=1
    )
    
    refinement_notes: str = Field(
        default="",
        description="General notes about the refinement process"
    )



class CharacterIntroduction(BaseModel):
    """
    Information about when a character is introduced in the screenplay.
    """
    name: str = Field(
        ...,
        description="Character name"
    )
    
    first_scene: int = Field(
        ...,
        description="Scene number where character first appears",
        ge=1
    )
    
    description: Optional[str] = Field(
        None,
        description="Brief character description at introduction"
    )
    
    role: Optional[str] = Field(
        None,
        description="Character's role in the story (protagonist, antagonist, etc.)"
    )


class LocationUsage(BaseModel):
    """
    Information about where a location is used in the screenplay.
    """
    name: str = Field(
        ...,
        description="Location name"
    )
    
    location_type: str = Field(
        ...,
        description="INT or EXT"
    )
    
    scenes: List[int] = Field(
        ...,
        description="Scene numbers where this location appears",
        min_items=1
    )
    
    total_usage: int = Field(
        ...,
        description="Total number of times this location is used",
        ge=1
    )



def scene_to_fountain_heading(scene: Scene) -> str:
    """
    Convert a Scene object to a Fountain scene heading.
    
    Args:
        scene: Scene object
        
    Returns:
        Formatted scene heading (e.g., "INT. NAPOLEON'S TENT - NIGHT")
    """
    return scene.location


def estimate_page_count(screenplay_text: str) -> int:
    """
    Estimate page count from screenplay text.
    
    Rough estimation: ~55 lines per page
    
    Args:
        screenplay_text: Full screenplay text
        
    Returns:
        Estimated page count
    """
    lines = screenplay_text.split("\n")
    return max(1, len(lines) // 55)


def extract_characters_from_screenplay(screenplay_text: str) -> List[str]:
    """
    Extract unique character names from screenplay text.
    
    Looks for lines that are all caps (character names in Fountain format).
    
    Args:
        screenplay_text: Full screenplay text
        
    Returns:
        List of unique character names
    """
    import re
    
    character_pattern = r"^([A-Z][A-Z\s\.\']+)$"
    
    characters = set()
    for line in screenplay_text.split("\n"):
        line = line.strip()
        
        if not line or line.startswith("INT.") or line.startswith("EXT."):
            continue
        
        match = re.match(character_pattern, line)
        if match:
            name = match.group(1).strip()
            if name not in ["FADE IN:", "FADE OUT:", "CUT TO:", "DISSOLVE TO:"]:
                characters.add(name)
    
    return sorted(list(characters))


def extract_locations_from_screenplay(screenplay_text: str) -> List[str]:
    """
    Extract unique locations from screenplay text.
    
    Looks for scene headings (INT./EXT. patterns).
    
    Args:
        screenplay_text: Full screenplay text
        
    Returns:
        List of unique locations
    """
    import re
    
    scene_heading_pattern = r"^(INT\.|EXT\.)\s+(.+?)\s+-\s+(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS)"
    
    locations = set()
    for line in screenplay_text.split("\n"):
        line = line.strip()
        match = re.match(scene_heading_pattern, line)
        if match:
            location = match.group(2).strip()
            locations.add(location)
    
    return sorted(list(locations))