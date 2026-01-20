"""
Phase 4 - Node 4: Scene Analysis
Deeply analyzes each scene, breaking it into action beats,
identifying props, and preparing for storyboard planning.
"""

from langchain_openai import ChatOpenAI
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..state import Phase4State
from ..models import SceneAnalysis
from ..utils import (
    extract_scene_text,
    extract_scene_text_by_heading,
    extract_time_from_heading,
    find_environment_for_scene,
    find_characters_in_scene,
    classify_scene_type
)

# Import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import get_llm_config


def scene_analysis_node(state: Phase4State) -> Dict:
    """
    Deeply analyze each scene for storyboard planning.
    
    Process:
    1. For each scene in screenplay
    2. Break into distinct action beats
    3. Identify all props/objects
    4. Extract dialogue segments with timestamps
    5. Determine scene complexity
    6. Calculate estimated duration per beat
    
    This node prepares data for the storyboard planning node.
    
    Uses:
    - Model: gpt-4o
    - Temperature: 0.4
    - Structured output: SceneAnalysis
    
    Returns:
        Dict with 'scenes' key containing detailed scene data
    """
    
    print("=" * 80)
    print("NODE 4: SCENE ANALYSIS")
    print("=" * 80)
    
    screenplay_text = state['screenplay_text']
    scene_breakdown = state.get('scene_breakdown', [])
    characters_db = state['characters_database']
    environments_db = state['environments_database']
    
    print(f"Analyzing {len(scene_breakdown)} scenes in detail...")
    
    llm = ChatOpenAI(**get_llm_config("phase4", "scene_analysis"))
    
    analyzed_scenes = []
    
    for idx, scene in enumerate(scene_breakdown, 1):
        scene_number = scene['scene_number']
        # Handle both 'scene_heading' (from Phase 3) and 'location' (from test data)
        scene_heading = scene.get('scene_heading') or scene.get('location', 'UNKNOWN LOCATION')
        
        print(f"\n[{idx}/{len(scene_breakdown)}] Scene {scene_number}: {scene_heading}")
        
        # Extract scene text from screenplay
        # Use heading-based extraction (more reliable than scene number)
        scene_text = extract_scene_text_by_heading(screenplay_text, scene_heading)
        
        # Fallback to scene number if heading match fails
        if not scene_text or len(scene_text) < 50:
            scene_text = extract_scene_text(screenplay_text, scene_number)
        
        if not scene_text or len(scene_text) < 50:
            print(f"  ⚠️  Insufficient scene text, skipping")
            continue
        
        print(f"  ✓ Extracted scene text ({len(scene_text)} chars)")
        
        # Find environment for this scene
        environment = find_environment_for_scene(environments_db, scene_heading)
        
        if environment:
            print(f"  ✓ Matched environment: {environment['name']}")
        else:
            print(f"  ⚠️  No matching environment found")
        
        # Find characters in this scene
        characters_present = find_characters_in_scene(characters_db, scene_number)
        print(f"  ✓ Characters present: {[c['name'] for c in characters_present]}")
        
        analysis_prompt = f"""
Deeply analyze this scene for storyboard creation.

SCENE {scene_number}: {scene_heading}

SCENE TEXT:
{scene_text}

ENVIRONMENT: {environment['name'] if environment else 'Unknown'}

CHARACTERS: {', '.join([c['name'] for c in characters_present])}

Break this scene down completely:

1. ACTION BEATS:
   Break the scene into distinct action beats (moments/shots).
   Each beat should be:
   - A single action or moment
   - 3-10 seconds typically
   - Filmable as one shot
   
   For each beat provide:
   - description: What happens
   - action: Specific action (e.g., "door opens", "character speaks", "object falls")
   - duration: Estimated seconds (3-10 typically)
   - characters: List of character names involved
   - props: List of props involved
   - suggested_camera_angle: Recommended angle (e.g., "wide shot", "close-up on face")
   
   Examples of good beats:
   - "Room establishing shot" (5s)
   - "Close-up of clock showing time" (3s)
   - "Character wakes up suddenly" (4s)
   - "Phone rings, character reaches for it" (6s)
   - "Character speaks dialogue" (based on dialogue length)

2. PROPS (Temporary Objects):
   Identify objects that appear DURING this scene (not permanent fixtures).
   For each prop:
   - name: Object name
   - description: What it looks like
   - importance: "high" (plot-critical), "medium" (notable), "low" (background)
   - camera_focus: true if camera focuses on it specifically
   - action_with_prop: What happens with this prop
   
   Examples: phone, photograph, gun, drink, letter, keys
   NOT: walls, furniture (those are in environment)

3. DIALOGUE SEGMENTS:
   For each line of dialogue:
   - timestamp: When in scene (e.g., "0:12" for 12 seconds in)
   - character_name: Who speaks
   - line_text: The actual dialogue
   - emotional_state: Character's emotion (e.g., "confused", "angry", "calm")
   - delivery_notes: How it should be delivered
   - beat_number: Which action beat this occurs during

4. SCENE CHARACTERISTICS:
   - total_duration: Total scene length in seconds
   - complexity: "simple" (1-4 beats), "medium" (5-9 beats), "complex" (10+ beats)
   - scene_type: Classify as one of:
     * "dialogue_heavy" - mostly talking
     * "action_heavy" - mostly physical action
     * "dialogue_with_action" - balanced
     * "establishing" - setting introduction
     * "transition" - moving between locations
   - lighting_notes: Specific lighting for this scene
   - atmosphere_notes: Mood/atmosphere
   - character_emotions: Dict mapping character names to their emotional arc in scene

IMPORTANT:
- Be precise with action beats - they'll become storyboard frames
- Estimate realistic durations
- Identify all significant props
- Note camera suggestions that make sense for each beat
- Consider continuity and flow
"""
        
        print(f"  🤖 Analyzing scene structure...")
        structured_llm = llm.with_structured_output(SceneAnalysis, method="function_calling")
        
        try:
            analysis = structured_llm.invoke(analysis_prompt)
            
            # Build scene data structure
            scene_data = {
                "scene_number": scene_number,
                "scene_heading": scene_heading,
                "time_of_day": extract_time_from_heading(scene_heading),
                "duration_estimate": analysis.total_duration,
                "complexity": analysis.complexity,
                "scene_type": classify_scene_type(analysis),
                
                "environment": {
                    "environment_id": environment['environment_id'] if environment else None,
                    "name": environment['name'] if environment else "Unknown",
                    "time_variant": extract_time_from_heading(scene_heading).lower(),
                    "specific_lighting": analysis.lighting_notes,
                    "atmosphere": analysis.atmosphere_notes
                },
                
                "characters_present": [
                    {
                        "character_id": char['character_id'],
                        "name": char['name'],
                        "costume_reference": char['costumes_by_scene'].get(str(scene_number)),
                        "emotional_arc": analysis.character_emotions.get(char['name'], "neutral")
                    }
                    for char in characters_present
                ],
                
                "props": [
                    {
                        "name": prop.name,
                        "description": prop.description,
                        "importance": prop.importance,
                        "camera_focus": prop.camera_focus,
                        "action": prop.action_with_prop
                    }
                    for prop in analysis.props
                ],
                
                "action_beats": [
                    {
                        "beat_number": idx + 1,
                        "description": beat.description,
                        "action": beat.action,
                        "duration": beat.duration,
                        "characters_involved": beat.characters,
                        "props_involved": beat.props,
                        "camera_note": beat.suggested_camera_angle
                    }
                    for idx, beat in enumerate(analysis.action_beats)
                ],
                
                "dialogue_segments": [
                    {
                        "segment_number": idx + 1,
                        "timestamp": dialogue.timestamp,
                        "character": dialogue.character_name,
                        "line": dialogue.line_text,
                        "emotional_state": dialogue.emotional_state,
                        "delivery_notes": dialogue.delivery_notes,
                        "associated_beat": dialogue.beat_number
                    }
                    for idx, dialogue in enumerate(analysis.dialogue_segments)
                ]
            }
            
            analyzed_scenes.append(scene_data)
            
            print(f"  ✓ Analysis complete:")
            print(f"    - Duration: {analysis.total_duration}s")
            print(f"    - Complexity: {analysis.complexity}")
            print(f"    - Action beats: {len(analysis.action_beats)}")
            print(f"    - Props: {len(analysis.props)}")
            print(f"    - Dialogue: {len(analysis.dialogue_segments)} lines")
            
        except Exception as e:
            print(f"  ❌ Error analyzing scene: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ SCENE ANALYSIS COMPLETE")
    print(f"   Scenes analyzed: {len(analyzed_scenes)}/{len(scene_breakdown)}")
    total_beats = sum(len(s['action_beats']) for s in analyzed_scenes)
    print(f"   Total action beats: {total_beats}")
    total_duration = sum(s['duration_estimate'] for s in analyzed_scenes)
    print(f"   Total estimated duration: {total_duration}s (~{total_duration//60}m)")
    print("=" * 80 + "\n")
    
    return {"scenes": analyzed_scenes}
