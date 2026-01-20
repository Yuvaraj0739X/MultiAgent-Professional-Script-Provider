from typing import TypedDict, List, Dict, Optional, Annotated
from typing_extensions import NotRequired
import operator


class Phase3State(TypedDict):
    """
    State for Phase 3: Screenplay Generation
    
    This state inherits outputs from Phase 1 and Phase 2, then adds
    screenplay-specific data as scenes are generated.
    """
    
    
    user_input: str
    phase1_brief: str  # 10-15 page detailed story brief
    research_required: bool  # True for real/historical, False for fictional
    
    timeline: NotRequired[List[Dict]]  # Chronological events
    key_figures: NotRequired[List[Dict]]  # Character profiles
    key_locations: NotRequired[List[Dict]]  # Setting details
    verified_facts: NotRequired[List[Dict]]  # Cross-verified facts
    
    
    scene_breakdown: NotRequired[List[Dict]]  # List of structured scenes
    """
    Each scene dict contains:
    {
        "scene_number": 1,
        "location": "INT. NAPOLEON'S TENT - NIGHT",
        "time": "NIGHT",
        "description": "Napoleon studies battle maps...",
        "characters": ["Napoleon", "Marshal Ney"],
        "key_action": "Napoleon receives news...",
        "estimated_duration": 60  # seconds
    }
    """
    
    total_scenes: NotRequired[int]  # Total number of scenes
    estimated_total_duration: NotRequired[int]  # Total estimated runtime (minutes)
    
    
    screenplay_text: NotRequired[str]  # Full screenplay in Fountain format
    """
    Complete screenplay text in Fountain format:
    - Scene headings: INT./EXT. LOCATION - TIME
    - Action descriptions
    - Character dialogue
    - Stage directions
    """
    
    screenplay_metadata: NotRequired[Dict]  # Metadata about the screenplay
    """
    Metadata dict contains:
    {
        "page_count": 25,
        "estimated_duration": 25,
        "scene_count": 28,
        "character_count": 12,
        "location_count": 8,
        "locations": ["Napoleon's Tent", "Waterloo Battlefield", ...],
        "characters": ["Napoleon Bonaparte", "Duke of Wellington", ...],
        "generation_timestamp": "2026-01-18T14:30:22Z",
        "historical_accuracy": "verified"  # if Phase 2 ran
    }
    """
    
    generation_notes: NotRequired[str]  # Notes about the generation process
    
    
    validation_result: NotRequired[Dict]  # Format validation results
    """
    Validation dict contains:
    {
        "is_valid": True,
        "errors": [],
        "warnings": ["Minor formatting issue..."],
        "compliance_score": 95.0
    }
    """
    
    validation_passed: NotRequired[bool]  # Quick boolean check
    
    
    refinement_applied: NotRequired[bool]  # Whether refinement was needed
    refinement_changes: NotRequired[List[str]]  # List of changes made
    
    
    session_id: NotRequired[str]  # Session identifier
    output_directory: NotRequired[str]  # Where to save outputs
    checkpoint_path: NotRequired[str]  # State persistence path
    
    
    errors: NotRequired[List[str]]  # Any errors encountered
    warnings: NotRequired[List[str]]  # Any warnings generated


Phase3StateWithAdd = TypedDict(
    "Phase3StateWithAdd",
    {
        **{k: v for k, v in Phase3State.__annotations__.items()},
        
        "errors": Annotated[List[str], operator.add],
        "warnings": Annotated[List[str], operator.add],
    }
)


def get_initial_phase3_state(
    phase1_brief: str,
    user_input: str,
    research_required: bool,
    timeline: Optional[List[Dict]] = None,
    key_figures: Optional[List[Dict]] = None,
    key_locations: Optional[List[Dict]] = None,
    verified_facts: Optional[List[Dict]] = None,
    session_id: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> Phase3State:
    """
    Create initial Phase3State from Phase 1 and Phase 2 outputs.
    
    Args:
        phase1_brief: Story brief from Phase 1
        user_input: Original user input
        research_required: Whether research was needed
        timeline: Timeline events from Phase 2 (if available)
        key_figures: Character profiles from Phase 2 (if available)
        key_locations: Location details from Phase 2 (if available)
        verified_facts: Verified facts from Phase 2 (if available)
        session_id: Session identifier
        output_directory: Output directory path
        
    Returns:
        Initial Phase3State with Phase 1 & 2 data
    """
    state: Phase3State = {
        "user_input": user_input,
        "phase1_brief": phase1_brief,
        "research_required": research_required,
    }
    
    if timeline is not None:
        state["timeline"] = timeline
    if key_figures is not None:
        state["key_figures"] = key_figures
    if key_locations is not None:
        state["key_locations"] = key_locations
    if verified_facts is not None:
        state["verified_facts"] = verified_facts
    
    if session_id is not None:
        state["session_id"] = session_id
    if output_directory is not None:
        state["output_directory"] = output_directory
    
    return state


def is_historical_story(state: Phase3State) -> bool:
    """
    Check if this is a historical story with Phase 2 research data.
    
    Args:
        state: Phase3State
        
    Returns:
        True if historical story with timeline data
    """
    return state.get("research_required", False) and "timeline" in state


def get_historical_context(state: Phase3State) -> str:
    """
    Get formatted historical context from Phase 2 for screenplay generation.
    
    Args:
        state: Phase3State
        
    Returns:
        Formatted historical context string
    """
    if not is_historical_story(state):
        return ""
    
    context_parts = []
    
    if "timeline" in state:
        context_parts.append("HISTORICAL TIMELINE:")
        for event in state["timeline"]:
            date = event.get("date", "Unknown date")
            event_name = event.get("event", "Unknown event")
            context_parts.append(f"- {date}: {event_name}")
        context_parts.append("")
    
    if "key_figures" in state:
        context_parts.append("KEY HISTORICAL FIGURES:")
        for figure in state["key_figures"]:
            name = figure.get("name", "Unknown")
            role = figure.get("role", "")
            context_parts.append(f"- {name}: {role}")
        context_parts.append("")
    
    if "key_locations" in state:
        context_parts.append("KEY LOCATIONS:")
        for location in state["key_locations"]:
            name = location.get("name", "Unknown")
            loc_type = location.get("type", "")
            context_parts.append(f"- {name} ({loc_type})")
        context_parts.append("")
    
    return "\n".join(context_parts)