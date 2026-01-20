import os
from typing import Dict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from phase3_screenplay.state import Phase3State
from phase3_screenplay.nodes.scene_breakdown import scene_breakdown_node
from phase3_screenplay.nodes.screenplay_generation import screenplay_generation_node
from phase3_screenplay.nodes.screenplay_validation import screenplay_validation_node


def create_phase3_graph(checkpointer: Optional[MemorySaver] = None) -> StateGraph:
    """
    Create the Phase 3 screenplay generation workflow graph.
    
    Workflow:
        START
          ↓
        analyze_scenes (scene_breakdown_node)
          ↓
        generate_screenplay (screenplay_generation_node)
          ↓
        validate_screenplay (screenplay_validation_node)
          ↓
        END
    
    Args:
        checkpointer: Optional MemorySaver for state persistence
        
    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(Phase3State)
    
    workflow.add_node("analyze_scenes", scene_breakdown_node)
    workflow.add_node("generate_screenplay", screenplay_generation_node)
    workflow.add_node("validate_screenplay", screenplay_validation_node)
    
    workflow.set_entry_point("analyze_scenes")
    workflow.add_edge("analyze_scenes", "generate_screenplay")
    workflow.add_edge("generate_screenplay", "validate_screenplay")
    workflow.add_edge("validate_screenplay", END)
    
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    else:
        return workflow.compile()


def run_phase3(
    phase1_brief: str,
    user_input: str,
    research_required: bool = False,
    timeline: Optional[list] = None,
    key_figures: Optional[list] = None,
    key_locations: Optional[list] = None,
    verified_facts: Optional[list] = None,
    session_id: Optional[str] = None,
    output_directory: Optional[str] = None,
    use_checkpointer: bool = False
) -> Dict:
    """
    Run the complete Phase 3 screenplay generation workflow.
    
    Args:
        phase1_brief: Story brief from Phase 1
        user_input: Original user input
        research_required: Whether research was performed (historical story)
        timeline: Timeline events from Phase 2 (if available)
        key_figures: Character profiles from Phase 2 (if available)
        key_locations: Location details from Phase 2 (if available)
        verified_facts: Verified facts from Phase 2 (if available)
        session_id: Session identifier
        output_directory: Directory to save outputs
        use_checkpointer: Whether to use checkpoint persistence
        
    Returns:
        Final state dict with screenplay and metadata
    """
    print("\n" + "="*80)
    print("PHASE 3: SCREENPLAY GENERATION - WORKFLOW START")
    print("="*80)
    
    from phase3_screenplay.state import get_initial_phase3_state
    
    initial_state = get_initial_phase3_state(
        phase1_brief=phase1_brief,
        user_input=user_input,
        research_required=research_required,
        timeline=timeline,
        key_figures=key_figures,
        key_locations=key_locations,
        verified_facts=verified_facts,
        session_id=session_id,
        output_directory=output_directory
    )
    
    print(f"\n📋 Input Summary:")
    print(f"  User Input: {user_input}")
    print(f"  Story Brief: {len(phase1_brief)} characters")
    print(f"  Historical Story: {research_required}")
    if timeline:
        print(f"  Timeline Events: {len(timeline)}")
    
    checkpointer = MemorySaver() if use_checkpointer else None
    
    graph = create_phase3_graph(checkpointer=checkpointer)
    
    print(f"\n🚀 Starting workflow execution...")
    
    config = {"configurable": {"thread_id": session_id or "default"}} if checkpointer else None
    
    try:
        final_state = graph.invoke(initial_state, config=config)
        
        print(f"\n{'='*80}")
        print("PHASE 3: WORKFLOW COMPLETE ✅")
        print("="*80)
        
        if final_state.get("validation_passed"):
            print(f"✅ Screenplay validated successfully")
            print(f"   Compliance Score: {final_state.get('validation_result', {}).get('compliance_score', 0):.1f}%")
        else:
            print(f"⚠️  Screenplay generated but validation issues found")
            errors = final_state.get("validation_result", {}).get("errors", [])
            if errors:
                print(f"   Errors: {len(errors)}")
        
        metadata = final_state.get("screenplay_metadata", {})
        print(f"\n📊 Screenplay Statistics:")
        print(f"   Pages: {metadata.get('page_count', 0)}")
        print(f"   Duration: {metadata.get('estimated_duration', 0)} minutes")
        print(f"   Scenes: {metadata.get('scene_count', 0)}")
        print(f"   Characters: {metadata.get('character_count', 0)}")
        print(f"   Locations: {metadata.get('location_count', 0)}")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Workflow execution failed: {e}")
        raise


def save_phase3_outputs(state: Dict, output_directory: str) -> Dict[str, str]:
    """
    Save Phase 3 outputs to files.
    
    Args:
        state: Final Phase3State dict
        output_directory: Directory to save outputs
        
    Returns:
        Dict mapping output type to file path
    """
    from phase3_screenplay.utils import save_screenplay, save_json
    
    phase3_dir = os.path.join(output_directory, "phase3_screenplay")
    os.makedirs(phase3_dir, exist_ok=True)
    
    print(f"\n💾 Saving Phase 3 outputs to: {phase3_dir}")
    
    saved_files = {}
    
    if state.get("scene_breakdown"):
        scene_breakdown_path = os.path.join(phase3_dir, "scene_breakdown.json")
        save_json(
            {"scenes": state["scene_breakdown"], "total_scenes": state.get("total_scenes", 0)},
            scene_breakdown_path
        )
        saved_files["scene_breakdown"] = scene_breakdown_path
        print(f"  ✅ scene_breakdown.json")
    
    if state.get("screenplay_text"):
        screenplay_path = os.path.join(phase3_dir, "screenplay.fountain")
        save_screenplay(state["screenplay_text"], screenplay_path)
        saved_files["screenplay"] = screenplay_path
        print(f"  ✅ screenplay.fountain")
    
    if state.get("screenplay_metadata"):
        metadata_path = os.path.join(phase3_dir, "screenplay_metadata.json")
        save_json(state["screenplay_metadata"], metadata_path)
        saved_files["metadata"] = metadata_path
        print(f"  ✅ screenplay_metadata.json")
    
    if state.get("validation_result"):
        validation_path = os.path.join(phase3_dir, "validation_result.json")
        save_json(state["validation_result"], validation_path)
        saved_files["validation"] = validation_path
        print(f"  ✅ validation_result.json")
    
    print(f"\n✅ All outputs saved to: {phase3_dir}")
    
    return saved_files


if __name__ == "__main__":
    print("Testing Phase 3 complete workflow...")
    
    test_brief = """# THE FINAL STAND - Story Brief

## Logline
A soldier must defend a critical position against overwhelming odds.

## Setting
Modern warfare, desert battlefield

## Main Characters
- Captain Miller (35): Battle-hardened infantry commander
- Sergeant Hayes (28): Loyal second-in-command
- Enemy Commander (40): Ruthless tactical genius

## Act 1: The Assignment
Captain Miller receives orders to hold a strategic hill.
Team arrives and sets up defensive positions.

## Act 2: The Siege
Enemy forces attack in waves.
Team holds position despite casualties.
Sergeant Hayes is wounded.

## Act 3: The Resolution
Final enemy assault.
Miller makes desperate last stand.
Reinforcements arrive just in time.
Victory at great cost.
"""

    result = run_phase3(
        phase1_brief=test_brief,
        user_input="Story about a last stand battle",
        research_required=False,
        session_id="test_phase3",
        use_checkpointer=False
    )
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print(f"Screenplay generated: {len(result.get('screenplay_text', ''))} characters")
    print(f"Validation passed: {result.get('validation_passed', False)}")
    
    import tempfile
    test_output_dir = tempfile.mkdtemp()
    saved = save_phase3_outputs(result, test_output_dir)
    print(f"\nTest outputs saved to: {test_output_dir}")
    for output_type, path in saved.items():
        print(f"  - {output_type}: {path}")