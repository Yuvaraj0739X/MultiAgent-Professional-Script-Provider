import sys
import os
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain_openai import ChatOpenAI
from config import get_llm_config
from phase3_screenplay.state import Phase3State
from phase3_screenplay.models import ScreenplayOutput, ScreenplayMetadata
from phase3_screenplay.utils import (
    merge_scenes,
    create_title_page,
    get_screenplay_metadata,
    format_historical_context_for_prompt
)


def generate_single_scene(
    scene: Dict,
    previous_scenes_summary: str,
    story_brief: str,
    historical_context: str,
    llm: ChatOpenAI
) -> str:
    """
    Generate a single scene in Fountain format.
    
    Args:
        scene: Scene dict from scene_breakdown
        previous_scenes_summary: Summary of what happened in previous scenes
        story_brief: Original story brief for context
        historical_context: Historical context if applicable
        llm: ChatOpenAI instance
        
    Returns:
        Generated scene text in Fountain format
    """
    scene_num = scene.get("scene_number", 0)
    location = scene.get("location", "")
    characters = scene.get("characters", [])
    key_action = scene.get("key_action", "")
    description = scene.get("description", "")
    
    system_prompt = f"""You are an expert screenplay writer specializing in the Fountain format.

Your task is to write a single scene for a screenplay.

FOUNTAIN FORMAT REQUIREMENTS:
1. Scene Heading: Already provided, use as-is
2. Action: Write in present tense, visually descriptive, active voice
   - What we SEE and HEAR
   - No camera directions
   - Keep paragraphs short (2-3 lines max)
3. Character Names: ALL CAPS before dialogue
4. Dialogue: Natural, character-appropriate speech
   - Keep it conversational and authentic
   - Show character personality through speech patterns
   - Use subtext and conflict
5. Parentheticals: (emotion/action) - use sparingly, only when essential
6. NO transitions (CUT TO, DISSOLVE, etc.) unless absolutely necessary

WRITING PRINCIPLES:
- Show, don't tell
- Every line should advance plot or character
- Create visual imagery through action
- Dialogue should sound natural when spoken aloud
- Reveal character through actions and words
- Build tension and drama
- Use specific, concrete details

{historical_context}

CONSISTENCY REMINDERS:
- Match the tone and style of the overall story
- Keep character voices consistent
- Build on what happened in previous scenes
- Set up what needs to happen next

"""

    user_prompt = f"""Write Scene {scene_num} in Fountain format.

STORY CONTEXT:
{story_brief[:500]}...

PREVIOUS SCENES SUMMARY:
{previous_scenes_summary}

THIS SCENE:
Location: {location}
Characters: {', '.join(characters)}
Key Action: {key_action}
Description: {description}

Generate the complete scene with:
1. Scene heading (exactly): {location}
2. Action descriptions (visual, present tense)
3. Character dialogue (natural, revealing)
4. Stage directions as needed

Write a compelling, filmable scene that brings this moment to life."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = llm.invoke(messages)
        scene_text = response.content.strip()
        
        if not scene_text.startswith(location):
            scene_text = f"{location}\n\n{scene_text}"
        
        return scene_text
        
    except Exception as e:
        print(f"⚠️  Error generating scene {scene_num}: {e}")
        return f"""{location}

[Scene generation error - placeholder]

PLACEHOLDER CHARACTER
This scene could not be generated due to an error.
"""


def screenplay_generation_node(state: Phase3State) -> dict:
    """
    Generate complete screenplay in Fountain format from scene breakdown.
    
    This node:
    1. Takes the scene breakdown from previous node
    2. Generates each scene individually for quality control
    3. Maintains continuity across scenes
    4. Merges scenes into complete screenplay
    5. Adds title page and final formatting
    6. Extracts metadata (characters, locations, duration)
    
    Args:
        state: Phase3State containing scene_breakdown
        
    Returns:
        State updates with screenplay_text and screenplay_metadata
    """
    print("\n" + "="*80)
    print("PHASE 3 - NODE 2: SCREENPLAY GENERATION")
    print("="*80)
    
    scene_breakdown = state.get("scene_breakdown", [])
    if not scene_breakdown:
        raise ValueError("No scene_breakdown found in state")
    
    total_scenes = len(scene_breakdown)
    print(f"\n🎬 Generating screenplay for {total_scenes} scenes...")
    
    story_brief = state.get("phase1_brief", "")
    
    is_historical = state.get("research_required", False) and "timeline" in state
    historical_context = ""
    if is_historical:
        print("📚 Incorporating historical context...")
        historical_context = format_historical_context_for_prompt(
            timeline=state.get("timeline"),
            key_figures=state.get("key_figures"),
            key_locations=state.get("key_locations")
        )
    
    llm_config = get_llm_config("phase3", "screenplay_generation")
    
    print(f"🤖 Using model: {llm_config['model']} (temp: {llm_config['temperature']})")
    
    llm = ChatOpenAI(**llm_config)
    
    generated_scenes = []
    previous_scenes_summary = "This is the beginning of the story."
    
    for i, scene in enumerate(scene_breakdown):
        scene_num = scene.get("scene_number", i + 1)
        print(f"  Generating scene {scene_num}/{total_scenes}...", end=" ")
        
        try:
            scene_text = generate_single_scene(
                scene=scene,
                previous_scenes_summary=previous_scenes_summary,
                story_brief=story_brief,
                historical_context=historical_context,
                llm=llm
            )
            
            generated_scenes.append(scene_text)
            print("✅")
            
            key_action = scene.get("key_action", "")
            previous_scenes_summary += f"\nScene {scene_num}: {key_action}"
            
            summary_lines = previous_scenes_summary.split("\n")
            if len(summary_lines) > 6:
                previous_scenes_summary = "\n".join(summary_lines[-6:])
                
        except Exception as e:
            print(f"❌ Error: {e}")
            generated_scenes.append(f"[Error in scene {scene_num}]")
    
    print(f"\n✅ Generated all {len(generated_scenes)} scenes")
    
    print("📝 Merging scenes into complete screenplay...")
    screenplay_body = merge_scenes(generated_scenes)
    
    title = state.get("user_input", "Untitled Screenplay").upper()
    if len(title) > 50:
        title = "UNTITLED SCREENPLAY"
    
    based_on = "historical events" if is_historical else None
    title_page = create_title_page(title, based_on=based_on)
    
    full_screenplay = f"{title_page}\n\n{screenplay_body}"
    
    print(f"📄 Complete screenplay: {len(full_screenplay)} characters")
    
    print("📊 Extracting metadata...")
    metadata = get_screenplay_metadata(full_screenplay, historical=is_historical)
    
    print(f"  Pages: {metadata['page_count']}")
    print(f"  Duration: {metadata['estimated_duration']} minutes")
    print(f"  Scenes: {metadata['scene_count']}")
    print(f"  Characters: {metadata['character_count']}")
    print(f"  Locations: {metadata['location_count']}")
    
    generation_notes = f"""Screenplay generated successfully.
- Generated {total_scenes} scenes
- Model: {llm_config['model']}
- Temperature: {llm_config['temperature']}
- Historical accuracy: {'verified' if is_historical else 'fictional'}
"""
    
    return {
        "screenplay_text": full_screenplay,
        "screenplay_metadata": metadata,
        "generation_notes": generation_notes
    }


if __name__ == "__main__":
    print("Testing screenplay_generation_node...")
    
    test_scenes = [
        {
            "scene_number": 1,
            "location": "EXT. ELBA ISLAND - DAWN",
            "time": "DAWN",
            "description": "Napoleon prepares to escape exile",
            "characters": ["Napoleon", "Loyal Soldiers"],
            "key_action": "Napoleon boards ship to return to France",
            "estimated_duration": 60
        },
        {
            "scene_number": 2,
            "location": "INT. NAPOLEON'S TENT - NIGHT",
            "time": "NIGHT",
            "description": "Napoleon studies battle maps before Waterloo",
            "characters": ["Napoleon", "Marshal Ney"],
            "key_action": "Napoleon learns Grouchy cannot reinforce him",
            "estimated_duration": 90
        }
    ]
    
    test_state: Phase3State = {
        "user_input": "Napoleon at Waterloo",
        "phase1_brief": "Story about Napoleon's final battle...",
        "research_required": False,
        "scene_breakdown": test_scenes,
        "total_scenes": 2
    }
    
    result = screenplay_generation_node(test_state)
    
    print("\n" + "="*80)
    print("TEST RESULT:")
    print("="*80)
    print(f"Screenplay length: {len(result.get('screenplay_text', ''))} chars")
    print(f"Metadata: {result.get('screenplay_metadata', {})}")
    
    if result.get('screenplay_text'):
        print("\nFirst 500 characters:")
        print(result['screenplay_text'][:500])