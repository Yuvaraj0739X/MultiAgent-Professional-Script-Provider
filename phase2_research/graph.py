from langgraph.graph import StateGraph, END

from .state import Phase2State
from .nodes import (
    research_strategy_node,
    wikipedia_fetch_node,
    fact_extraction_node,
    fact_validation_node,
    timeline_build_node
)


def create_phase2_workflow():
    """
    Create Phase 2 research workflow.
    
    Workflow:
    START → RESEARCH_STRATEGY → WIKIPEDIA_FETCH → FACT_EXTRACTION →
    FACT_VALIDATION → TIMELINE_BUILD → END
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(Phase2State)
    
    workflow.add_node("research_strategy", research_strategy_node)
    workflow.add_node("wikipedia_fetch", wikipedia_fetch_node)
    workflow.add_node("fact_extraction", fact_extraction_node)
    workflow.add_node("fact_validation", fact_validation_node)
    workflow.add_node("timeline_build", timeline_build_node)
    
    workflow.set_entry_point("research_strategy")
    
    workflow.add_edge("research_strategy", "wikipedia_fetch")
    workflow.add_edge("wikipedia_fetch", "fact_extraction")
    workflow.add_edge("fact_extraction", "fact_validation")
    workflow.add_edge("fact_validation", "timeline_build")
    workflow.add_edge("timeline_build", END)
    
    return workflow.compile()


def run_phase2_workflow(initial_state: Phase2State):
    """
    Execute Phase 2 workflow.
    
    Args:
        initial_state: Initial Phase2State from Phase 1 output
    
    Returns:
        Final state after research completion
    """
    workflow = create_phase2_workflow()
    final_state = workflow.invoke(initial_state)
    return final_state