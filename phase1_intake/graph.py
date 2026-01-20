from langgraph.graph import StateGraph, END

from .state import Phase1State
from .nodes import (
    intake_node,
    clarification_node,
    human_input_node,
    integration_node,
    re_intake_node,
    summary_node
)



def route_after_intake(state: Phase1State) -> str:
    """
    Route after INTAKE_NODE.
    
    Decision: Is story complete or needs clarification?
    
    Returns:
        "summary" if complete
        "clarification" if needs more info
    """
    if state.get("is_complete", False):
        return "summary"
    else:
        return "clarification"


def route_after_re_intake(state: Phase1State) -> str:
    """
    Route after RE_INTAKE_NODE.
    
    Decision: Is story now complete, max iterations reached, or loop again?
    
    Returns:
        "summary" if complete or max iterations
        "clarification" if needs another round
    """
    is_complete = state.get("is_complete", False)
    iteration = state.get("clarification_iteration", 0)
    max_iterations = 5
    
    if is_complete or iteration >= max_iterations:
        return "summary"
    else:
        return "clarification"



def create_phase1_workflow():
    """
    Create the complete Phase 1 workflow graph.
    
    Workflow:
    START → INTAKE → (complete?) → SUMMARY → END
                  ↓ (incomplete)
              CLARIFICATION → HUMAN_INPUT → INTEGRATION → RE_INTAKE
                                                              ↓
                                                         (loop back or summary)
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(Phase1State)
    
    workflow.add_node("intake", intake_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("human_input", human_input_node)
    workflow.add_node("integration", integration_node)
    workflow.add_node("re_intake", re_intake_node)
    workflow.add_node("summary", summary_node)
    
    workflow.set_entry_point("intake")
    
    
    workflow.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            "summary": "summary",
            "clarification": "clarification"
        }
    )
    
    workflow.add_edge("clarification", "human_input")
    
    workflow.add_edge("human_input", "integration")
    
    workflow.add_edge("integration", "re_intake")
    
    workflow.add_conditional_edges(
        "re_intake",
        route_after_re_intake,
        {
            "summary": "summary",
            "clarification": "clarification"
        }
    )
    
    workflow.add_edge("summary", END)
    
    return workflow.compile()



def run_phase1_workflow(user_input: str, session_id: str):
    """
    Execute Phase 1 workflow end-to-end.
    
    Args:
        user_input: User's story idea
        session_id: Unique session identifier
    
    Returns:
        Final state after workflow completion
    """
    from .state import create_initial_state
    
    initial_state = create_initial_state(user_input, session_id)
    
    workflow = create_phase1_workflow()
    
    final_state = workflow.invoke(initial_state)
    
    return final_state