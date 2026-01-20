"""
Phase 4: LangGraph Workflow
Orchestrates the complete Phase 4 extraction and planning workflow.
"""

from langgraph.graph import StateGraph, END
from typing import Dict, List, Optional
import operator
from pathlib import Path
import json
from datetime import datetime

from .state import Phase4State, get_initial_phase4_state
from .nodes import (
    character_extraction_node,
    voice_profile_extraction_node,
    environment_extraction_node,
    scene_analysis_node,
    storyboard_planning_node
)


def create_phase4_graph(checkpointer=None) -> StateGraph:
    """
    Create Phase 4 LangGraph workflow.
    
    Workflow:
    1. extract_characters → Character extraction (Node 1)
    2. extract_voices → Voice profile extraction (Node 2)
    3. extract_environments → Environment extraction (Node 3)
    4. analyze_scenes → Scene analysis (Node 4)
    5. plan_storyboards → Storyboard planning (Node 5)
    
    Note: Node names must NOT match state key names (LangGraph limitation)
    
    Args:
        checkpointer: Optional checkpointer for persistence
    
    Returns:
        Compiled StateGraph
    """
    
    # Create workflow
    workflow = StateGraph(Phase4State)
    
    # Add nodes with different names than state keys
    workflow.add_node("extract_characters", character_extraction_node)
    workflow.add_node("extract_voices", voice_profile_extraction_node)
    workflow.add_node("extract_environments", environment_extraction_node)
    workflow.add_node("analyze_scenes", scene_analysis_node)
    workflow.add_node("plan_storyboards", storyboard_planning_node)
    
    # Set entry point
    workflow.set_entry_point("extract_characters")
    
    # Linear workflow: each node flows to the next
    workflow.add_edge("extract_characters", "extract_voices")
    workflow.add_edge("extract_voices", "extract_environments")
    workflow.add_edge("extract_environments", "analyze_scenes")
    workflow.add_edge("analyze_scenes", "plan_storyboards")
    workflow.add_edge("plan_storyboards", END)
    
    # Compile
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    else:
        return workflow.compile()


def run_phase4(
    screenplay_text: str,
    scene_breakdown: List[Dict],
    screenplay_metadata: Dict,
    session_id: str,
    output_directory: str,
    timeline: Optional[List[Dict]] = None,
    key_figures: Optional[List[Dict]] = None,
    key_locations: Optional[List[Dict]] = None,
    verified_facts: Optional[List[str]] = None,
    use_checkpointer: bool = False
) -> Dict:
    """
    Run complete Phase 4 workflow.
    
    Args:
        screenplay_text: Complete screenplay from Phase 3
        scene_breakdown: Scene list from Phase 3
        screenplay_metadata: Metadata from Phase 3
        session_id: Session identifier
        output_directory: Where to save outputs
        timeline: Optional historical timeline from Phase 2
        key_figures: Optional historical figures from Phase 2
        key_locations: Optional historical locations from Phase 2
        verified_facts: Optional verified facts from Phase 2
        use_checkpointer: Whether to use checkpointing
    
    Returns:
        Final Phase4State with all extracted data and storyboard plans
    """
    
    print("\n")
    print("🎬" * 40)
    print("PHASE 4: CHARACTER & ENVIRONMENT EXTRACTION + STORYBOARD PLANNING")
    print("🎬" * 40)
    print()
    
    # Create initial state
    initial_state = get_initial_phase4_state(
        screenplay_text=screenplay_text,
        scene_breakdown=scene_breakdown,
        screenplay_metadata=screenplay_metadata,
        session_id=session_id,
        output_directory=output_directory,
        timeline=timeline,
        key_figures=key_figures,
        key_locations=key_locations,
        verified_facts=verified_facts
    )
    
    print(f"📋 Session: {session_id}")
    print(f"📂 Output: {output_directory}")
    print(f"📄 Screenplay: {len(screenplay_text)} characters")
    print(f"🎬 Scenes: {len(scene_breakdown)}")
    print(f"📚 Historical data: {'Yes' if timeline else 'No'}")
    print()
    
    # Create and run graph
    checkpointer = None  # Could add MemorySaver() here if needed
    graph = create_phase4_graph(checkpointer if use_checkpointer else None)
    
    # Run workflow
    config = {"configurable": {"thread_id": session_id}} if use_checkpointer else None
    
    print("🚀 Starting Phase 4 workflow...")
    print("   This will take several minutes...\n")
    
    start_time = datetime.now()
    
    try:
        final_state = graph.invoke(initial_state, config=config)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Add metadata
        final_state['extraction_metadata'] = {
            "phase": 4,
            "session_id": session_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "duration_minutes": round(duration / 60, 2),
            "statistics": {
                "total_characters": len(final_state.get('characters_database', [])),
                "characters_with_voice_profiles": sum(
                    1 for c in final_state.get('characters_database', [])
                    if 'voice_profile' in c and 'error' not in c.get('voice_profile', {})
                ),
                "total_environments": len(final_state.get('environments_database', [])),
                "total_scenes": len(final_state.get('scenes', [])),
                "scenes_with_storyboards": sum(
                    1 for s in final_state.get('scenes', [])
                    if s.get('storyboard', {}).get('format') != 'error'
                ),
                "total_frames_planned": sum(
                    s.get('storyboard', {}).get('total_frames', 0)
                    for s in final_state.get('scenes', [])
                ),
                "total_video_clips": sum(
                    len(s.get('storyboard', {}).get('video_assembly', {}).get('clips', []))
                    for s in final_state.get('scenes', [])
                )
            }
        }
        
        print("\n" + "🎬" * 40)
        print("✅ PHASE 4 COMPLETE!")
        print("🎬" * 40)
        print(f"\n⏱️  Duration: {duration:.1f}s (~{duration/60:.1f} minutes)")
        print(f"\n📊 EXTRACTION SUMMARY:")
        stats = final_state['extraction_metadata']['statistics']
        print(f"   Characters extracted: {stats['total_characters']}")
        print(f"   Voice profiles: {stats['characters_with_voice_profiles']}")
        print(f"   Environments: {stats['total_environments']}")
        print(f"   Scenes analyzed: {stats['total_scenes']}")
        print(f"   Storyboards created: {stats['scenes_with_storyboards']}")
        print(f"   Total frames planned: {stats['total_frames_planned']}")
        print(f"   Total video clips: {stats['total_video_clips']}")
        print()
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ ERROR in Phase 4 workflow: {e}")
        raise


def save_phase4_outputs(state: Dict, output_dir: str) -> Dict[str, str]:
    """
    Save all Phase 4 outputs to JSON files.
    
    Output structure:
    output_dir/
        phase4_extraction/
            characters_database.json
            environments_database.json
            scenes_detailed.json
            storyboard_summary.json
            phase4_metadata.json
    
    Args:
        state: Final Phase4State
        output_dir: Output directory path
    
    Returns:
        Dict mapping output types to file paths
    """
    
    print("\n💾 Saving Phase 4 outputs...")
    
    # Create phase4 directory
    phase4_dir = Path(output_dir) / "phase4_extraction"
    phase4_dir.mkdir(parents=True, exist_ok=True)
    
    output_paths = {}
    
    # 1. Characters database
    if 'characters_database' in state:
        chars_path = phase4_dir / "characters_database.json"
        with open(chars_path, 'w', encoding='utf-8') as f:
            json.dump(state['characters_database'], f, indent=2, ensure_ascii=False)
        output_paths['characters'] = str(chars_path)
        print(f"   ✓ {chars_path.name}")
    
    # 2. Environments database
    if 'environments_database' in state:
        envs_path = phase4_dir / "environments_database.json"
        with open(envs_path, 'w', encoding='utf-8') as f:
            json.dump(state['environments_database'], f, indent=2, ensure_ascii=False)
        output_paths['environments'] = str(envs_path)
        print(f"   ✓ {envs_path.name}")
    
    # 3. Detailed scenes (MAIN OUTPUT - has storyboards)
    if 'scenes' in state:
        scenes_path = phase4_dir / "scenes_detailed.json"
        with open(scenes_path, 'w', encoding='utf-8') as f:
            json.dump(state['scenes'], f, indent=2, ensure_ascii=False)
        output_paths['scenes'] = str(scenes_path)
        print(f"   ✓ {scenes_path.name}")
    
    # 4. Storyboard summary (quick reference)
    if 'scenes' in state:
        summary = {
            "total_scenes": len(state['scenes']),
            "scenes": [
                {
                    "scene_number": s['scene_number'],
                    "heading": s['scene_heading'],
                    "duration": s['duration_estimate'],
                    "complexity": s['complexity'],
                    "storyboard_format": s.get('storyboard', {}).get('format', 'none'),
                    "total_frames": s.get('storyboard', {}).get('total_frames', 0),
                    "video_clips": len(s.get('storyboard', {}).get('video_assembly', {}).get('clips', []))
                }
                for s in state['scenes']
            ]
        }
        
        summary_path = phase4_dir / "storyboard_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        output_paths['summary'] = str(summary_path)
        print(f"   ✓ {summary_path.name}")
    
    # 5. Phase 4 metadata
    if 'extraction_metadata' in state:
        meta_path = phase4_dir / "phase4_metadata.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(state['extraction_metadata'], f, indent=2, ensure_ascii=False)
        output_paths['metadata'] = str(meta_path)
        print(f"   ✓ {meta_path.name}")
    
    print(f"\n✅ All outputs saved to: {phase4_dir}")
    print()
    
    return output_paths
