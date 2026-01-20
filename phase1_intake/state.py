from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


class Phase1State(TypedDict):
    """
    Complete state object passed between all nodes in Phase 1.
    Uses TypedDict for LangGraph compatibility.
    """
    
    user_input_raw: str
    """Original user input - never modified"""
    
    user_input_refined: str
    """Current refined version after integrating user responses"""
    
    clarity_score: int
    """Clarity score from 0-100"""
    
    is_complete: bool
    """Whether story idea has sufficient detail to proceed"""
    
    missing_elements: List[str]
    """List of missing critical elements (e.g., temporal_boundaries)"""
    
    detected_elements: Dict[str, str]
    """Elements that ARE present (e.g., {"genre": "war", "protagonist": "Napoleon"})"""
    
    ambiguities: List[str]
    """Unclear aspects that need clarification"""
    
    classification: str
    """Story type: "real" | "fictional" | "mixed" """
    
    research_required: bool
    """Whether external research is needed (true for real events)"""
    
    clarification_iteration: int
    """Number of clarification rounds completed (max 5)"""
    
    questions_asked: Annotated[List[Dict], add]
    """Complete history of all questions asked across iterations"""
    
    current_questions: List[Dict]
    """Questions waiting for user response in current iteration"""
    
    pending_user_response: bool
    """True when graph is paused waiting for human input"""
    
    user_responses: Annotated[List[Dict], add]
    """All user answers accumulated across iterations"""
    
    final_brief: Optional[str]
    """Complete story brief markdown document"""
    
    brief_metadata: Optional[Dict]
    """Metadata about the generated brief"""
    
    current_step: str
    """Name of current/last executed node"""
    
    errors: Annotated[List[str], add]
    """Accumulated errors during workflow"""
    
    workflow_complete: bool
    """True when Phase 1 is complete"""
    
    session_id: str
    """Unique session identifier for state persistence"""
    
    checkpoint_path: Optional[str]
    """File path where state is saved"""


def create_initial_state(user_input: str, session_id: str) -> Phase1State:
    """
    Create initial state object from user input.
    
    Args:
        user_input: Raw user story idea
        session_id: Unique identifier for this session
    
    Returns:
        Initialized Phase1State
    """
    return Phase1State(
        user_input_raw=user_input,
        user_input_refined=user_input,
        
        clarity_score=0,
        is_complete=False,
        missing_elements=[],
        detected_elements={},
        ambiguities=[],
        classification="unknown",
        research_required=False,
        
        clarification_iteration=0,
        questions_asked=[],
        current_questions=[],
        pending_user_response=False,
        
        user_responses=[],
        
        final_brief=None,
        brief_metadata=None,
        
        current_step="initialized",
        errors=[],
        workflow_complete=False,
        
        session_id=session_id,
        checkpoint_path=None
    )