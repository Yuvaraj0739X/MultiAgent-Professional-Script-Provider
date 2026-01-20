import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain_openai import ChatOpenAI
from config import get_llm_config
from phase3_screenplay.state import Phase3State
from phase3_screenplay.models import SceneBreakdown
from phase3_screenplay.utils import format_historical_context_for_prompt


def scene_breakdown_node(state: Phase3State) -> dict:
    """
    Break story brief into structured list of scenes.
    
    This node:
    1. Analyzes the story structure (3-act, hero's journey, etc.)
    2. Identifies key plot points and turning moments
    3. Breaks the story into 15-30 filmable scenes
    4. For each scene, defines:
       - Location (INT/EXT)
       - Time of day
       - Characters present
       - Key action/turning point
       - Estimated duration
    5. For historical stories, ensures timeline events are represented
    
    Args:
        state: Phase3State containing phase1_brief and optional timeline
        
    Returns:
        State updates with scene_breakdown, total_scenes, estimated_total_duration
    """
    print("\n" + "="*80)
    print("PHASE 3 - NODE 1: SCENE BREAKDOWN")
    print("="*80)
    
    story_brief = state.get("phase1_brief", "")
    if not story_brief:
        raise ValueError("No phase1_brief found in state")
    
    print(f"\n📖 Analyzing story brief ({len(story_brief)} characters)...")
    
    is_historical = state.get("research_required", False) and "timeline" in state
    
    historical_context = ""
    if is_historical:
        print("📚 Historical story detected - incorporating timeline...")
        historical_context = format_historical_context_for_prompt(
            timeline=state.get("timeline"),
            key_figures=state.get("key_figures"),
            key_locations=state.get("key_locations")
        )
    
    system_prompt = f"""You are an expert screenplay structure analyst and story breakdown specialist.

Your task is to analyze the provided story brief and break it down into a structured list of 15-30 scenes suitable for a screenplay.

STORY ANALYSIS APPROACH:
1. Identify the story structure (3-act, hero's journey, etc.)
2. Find the key plot points, turning points, and climactic moments
3. Determine the emotional arc and pacing
4. Break the story into filmable scenes

SCENE REQUIREMENTS:
- Each scene should be 30-120 seconds (0.5-2 minutes)
- Each scene needs a clear location (INT. or EXT.)
- Each scene needs a specific time (DAY, NIGHT, DAWN, DUSK, etc.)
- Each scene must list the characters present
- Each scene must have a clear action or purpose
- Scenes should flow logically and build dramatic tension

SCENE STRUCTURE:
- Target: 15-30 scenes total
- Total estimated duration: 15-30 minutes
- Act 1: ~25% of scenes (setup)
- Act 2: ~50% of scenes (confrontation)
- Act 3: ~25% of scenes (resolution)

{historical_context}

IMPORTANT FOR HISTORICAL STORIES:
- Ensure all major timeline events are represented in scenes
- Characters should match the historical figures from research
- Locations should align with historical settings
- Maintain historical accuracy while creating compelling narrative

OUTPUT REQUIREMENTS:
Return a structured breakdown with:
- List of all scenes in order
- Each scene with: number, location, time, description, characters, key_action, estimated_duration
- Total scene count
- Total estimated duration
- Optional act breakdown

"""

    user_prompt = f"""Analyze this story brief and create a detailed scene breakdown:

{story_brief}

Create a structured scene-by-scene breakdown suitable for a {
    'historically accurate' if is_historical else 'compelling'
} screenplay."""

    llm_config = get_llm_config("phase3", "scene_breakdown")
    
    print(f"🤖 Using model: {llm_config['model']} (temp: {llm_config['temperature']})")
    print("🎬 Generating scene breakdown...")
    
    llm = ChatOpenAI(**llm_config)
    structured_llm = llm.with_structured_output(SceneBreakdown)
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        scene_breakdown = structured_llm.invoke(messages)
        
        if not scene_breakdown or not scene_breakdown.scenes:
            raise ValueError("LLM returned empty scene breakdown")
        
        print(f"✅ Generated {len(scene_breakdown.scenes)} scenes")
        print(f"⏱️  Estimated total duration: {scene_breakdown.estimated_total_duration} minutes")
        
        print(f"\n📋 Scene Summary:")
        for i, scene in enumerate(scene_breakdown.scenes[:5]):  # Show first 5
            print(f"  Scene {scene.scene_number}: {scene.location}")
            print(f"    Characters: {', '.join(scene.characters)}")
            print(f"    Action: {scene.key_action[:60]}...")
        
        if len(scene_breakdown.scenes) > 5:
            print(f"  ... and {len(scene_breakdown.scenes) - 5} more scenes")
        
        scenes_dict = [scene.model_dump() for scene in scene_breakdown.scenes]
        
        return {
            "scene_breakdown": scenes_dict,
            "total_scenes": scene_breakdown.total_scenes,
            "estimated_total_duration": scene_breakdown.estimated_total_duration
        }
        
    except Exception as e:
        error_msg = f"Error in scene_breakdown_node: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg],
            "scene_breakdown": [],
            "total_scenes": 0
        }


if __name__ == "__main__":
    print("Testing scene_breakdown_node...")
    
    test_state: Phase3State = {
        "user_input": "Story about Napoleon at Waterloo",
        "phase1_brief": """
# NAPOLEON'S LAST STAND - Story Brief

## Logline
A military genius faces his final battle as his empire crumbles around him.

## Setting
Belgium, June 1815 - The fields of Waterloo

## Main Characters
- Napoleon Bonaparte (45): Exiled emperor making desperate comeback
- Duke of Wellington (46): British commander
- Marshal Ney (46): Napoleon's loyal cavalry commander

## Act 1: The Hundred Days
Napoleon escapes from Elba and returns to France, rallying his army.

## Act 2: The Campaign  
Napoleon marches into Belgium and defeats the Prussians at Ligny.

## Act 3: The Battle
June 18, 1815 - The final confrontation at Waterloo. Ney's cavalry charges.
Prussian reinforcements arrive. Napoleon's defeat and abdication.
        """,
        "research_required": False
    }
    
    result = scene_breakdown_node(test_state)
    
    print("\n" + "="*80)
    print("TEST RESULT:")
    print("="*80)
    print(f"Scenes generated: {result.get('total_scenes', 0)}")
    print(f"Duration: {result.get('estimated_total_duration', 0)} minutes")
    
    if result.get('scene_breakdown'):
        print(f"\nFirst scene:")
        first_scene = result['scene_breakdown'][0]
        for key, value in first_scene.items():
            print(f"  {key}: {value}")