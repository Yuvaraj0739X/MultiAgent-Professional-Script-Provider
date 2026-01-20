"""
Phase 4: Character & Environment Extraction + Storyboard Planning
State Schema Definition

This module defines the state structure that flows through the Phase 4 workflow.
"""

from typing import TypedDict, List, Dict, Optional, NotRequired


class Phase4State(TypedDict):
    """
    State structure for Phase 4 workflow.
    
    Inputs (from Phase 3):
    - screenplay_text: Complete Fountain format screenplay
    - scene_breakdown: List of scenes from Phase 3
    - screenplay_metadata: Metadata from Phase 3
    - timeline: Optional historical timeline (from Phase 2)
    - key_figures: Optional historical figures (from Phase 2)
    - key_locations: Optional historical locations (from Phase 2)
    - verified_facts: Optional verified facts (from Phase 2)
    
    Outputs (Phase 4):
    - characters_database: Complete character database with voice profiles
    - environments_database: Complete environment database with anchor specs
    - scenes: Detailed scenes with storyboard plans
    - extraction_metadata: Statistics and summary
    """
    
    # ===== INPUTS FROM PREVIOUS PHASES =====
    screenplay_text: str
    scene_breakdown: List[Dict]
    screenplay_metadata: Dict
    session_id: str
    output_directory: str
    
    # Optional historical data from Phase 2
    timeline: NotRequired[List[Dict]]
    key_figures: NotRequired[List[Dict]]
    key_locations: NotRequired[List[Dict]]
    verified_facts: NotRequired[List[str]]
    
    # ===== PHASE 4 OUTPUTS =====
    # Node 1 & 2: Characters with voice profiles
    characters_database: NotRequired[List[Dict]]
    
    # Node 3: Environments with anchor specifications
    environments_database: NotRequired[List[Dict]]
    
    # Node 4 & 5: Detailed scenes with storyboard plans
    scenes: NotRequired[List[Dict]]
    
    # Metadata
    extraction_metadata: NotRequired[Dict]


def get_initial_phase4_state(
    screenplay_text: str,
    scene_breakdown: List[Dict],
    screenplay_metadata: Dict,
    session_id: str,
    output_directory: str,
    timeline: Optional[List[Dict]] = None,
    key_figures: Optional[List[Dict]] = None,
    key_locations: Optional[List[Dict]] = None,
    verified_facts: Optional[List[str]] = None
) -> Phase4State:
    """
    Create initial state for Phase 4 workflow.
    
    Args:
        screenplay_text: Complete screenplay from Phase 3
        scene_breakdown: Scene list from Phase 3
        screenplay_metadata: Metadata from Phase 3
        session_id: Session identifier
        output_directory: Where to save outputs
        timeline: Optional historical timeline
        key_figures: Optional historical figures
        key_locations: Optional historical locations
        verified_facts: Optional verified facts
    
    Returns:
        Initial Phase4State
    """
    state = Phase4State(
        screenplay_text=screenplay_text,
        scene_breakdown=scene_breakdown,
        screenplay_metadata=screenplay_metadata,
        session_id=session_id,
        output_directory=output_directory
    )
    
    # Add optional historical data if present
    if timeline:
        state['timeline'] = timeline
    if key_figures:
        state['key_figures'] = key_figures
    if key_locations:
        state['key_locations'] = key_locations
    if verified_facts:
        state['verified_facts'] = verified_facts
    
    return state
