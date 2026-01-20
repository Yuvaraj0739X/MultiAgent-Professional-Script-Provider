from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


class Phase2State(TypedDict):
    """
    Complete state object for Phase 2 workflow.
    Handles research and fact verification for real events/people.
    """
    
    phase1_brief: str
    """Complete story brief from Phase 1"""
    
    classification: str
    """Story classification: "real" | "fictional" | "mixed" """
    
    research_required: bool
    """Whether research is needed (from Phase 1)"""
    
    detected_entities: Dict[str, str]
    """Entities detected in Phase 1 (people, events, etc.)"""
    
    user_input_refined: str
    """Final refined story description from Phase 1"""
    
    research_queries: List[Dict]
    """Generated Wikipedia search queries with metadata"""
    
    query_strategy: Optional[str]
    """Strategy explanation for query generation"""
    
    wikipedia_articles: List[Dict]
    """Fetched Wikipedia articles (title, summary, full_text, sections, url)"""
    
    fetch_success_count: int
    """Number of successfully fetched articles"""
    
    fetch_failed_queries: List[str]
    """Queries that failed to return results"""
    
    extracted_facts: List[Dict]
    """All facts extracted from Wikipedia articles"""
    
    fact_categories: Dict[str, List]
    """Facts organized by category (people, events, locations, dates)"""
    
    verified_facts: List[Dict]
    """Facts confirmed by multiple sources"""
    
    disputed_facts: List[Dict]
    """Facts with conflicting information across sources"""
    
    unverified_facts: List[Dict]
    """Facts from single source only"""
    
    validation_summary: Optional[Dict]
    """Summary of validation results"""
    
    timeline: List[Dict]
    """Chronological timeline of verified events"""
    
    key_figures: List[Dict]
    """Important people with verified details"""
    
    key_locations: List[Dict]
    """Important places with verified details"""
    
    timeline_metadata: Optional[Dict]
    """Timeline span, event count, etc."""
    
    research_summary: Optional[str]
    """Markdown summary of all research findings"""
    
    verified_facts_json: Optional[str]
    """JSON string of verified facts for Phase 3"""
    
    current_step: str
    """Current node in workflow"""
    
    errors: Annotated[List[str], add]
    """Accumulated errors"""
    
    workflow_complete: bool
    """Phase 2 complete"""
    
    session_id: str
    """Session identifier (inherited from Phase 1)"""
    
    checkpoint_path: Optional[str]
    """Current checkpoint file path"""


def create_phase2_initial_state(
    phase1_output: Dict,
    session_id: str
) -> Phase2State:
    """
    Create initial Phase 2 state from Phase 1 output.
    
    Args:
        phase1_output: Final state from Phase 1
        session_id: Session identifier
    
    Returns:
        Initialized Phase2State
    """
    return Phase2State(
        phase1_brief=phase1_output.get("final_brief", ""),
        classification=phase1_output.get("classification", "unknown"),
        research_required=phase1_output.get("research_required", False),
        detected_entities=phase1_output.get("detected_elements", {}),
        user_input_refined=phase1_output.get("user_input_refined", ""),
        
        research_queries=[],
        query_strategy=None,
        
        wikipedia_articles=[],
        fetch_success_count=0,
        fetch_failed_queries=[],
        
        extracted_facts=[],
        fact_categories={},
        
        verified_facts=[],
        disputed_facts=[],
        unverified_facts=[],
        validation_summary=None,
        
        timeline=[],
        key_figures=[],
        key_locations=[],
        timeline_metadata=None,
        
        research_summary=None,
        verified_facts_json=None,
        
        current_step="initialized",
        errors=[],
        workflow_complete=False,
        
        session_id=session_id,
        checkpoint_path=None
    )