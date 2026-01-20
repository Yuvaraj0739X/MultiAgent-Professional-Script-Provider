"""
Phase 4 - Node 1: Character Extraction
Extracts all unique characters from screenplay with complete physical descriptions
and costume tracking per scene.
"""

from langchain_openai import ChatOpenAI
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..state import Phase4State
from ..models import Character, CharacterExtractionOutput
from ..utils import (
    parse_fountain_screenplay,
    extract_character_names_from_dialogue,
    extract_costume_for_scene,
    generate_character_image_prompt
)

# Import config from project root
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import get_llm_config


def character_extraction_node(state: Phase4State) -> Dict:
    """
    Extract all characters from screenplay.
    
    Process:
    1. Parse Fountain screenplay
    2. Find all dialogue character names (in CAPS)
    3. Find character descriptions in action lines
    4. Match descriptions to character names
    5. Track scenes where each character appears
    6. Extract costume per scene
    7. Generate base physical description
    8. Create character image prompt
    
    Uses:
    - Model: gpt-4o
    - Temperature: 0.3 (factual extraction)
    - Structured output: CharacterExtractionOutput
    
    Returns:
        Dict with 'characters_database' key
    """
    
    print("=" * 80)
    print("NODE 1: CHARACTER EXTRACTION")
    print("=" * 80)
    
    screenplay_text = state['screenplay_text']
    scenes = state.get('scene_breakdown', [])
    
    print(f"Analyzing screenplay ({len(screenplay_text)} characters)...")
    print(f"Processing {len(scenes)} scenes...")
    
    # Parse screenplay
    parsed_screenplay = parse_fountain_screenplay(screenplay_text)
    print(f"✓ Parsed screenplay: {len(parsed_screenplay['scenes'])} scenes found")
    
    # Extract character names from dialogue
    character_names = extract_character_names_from_dialogue(parsed_screenplay)
    print(f"✓ Found {len(character_names)} unique characters in dialogue:")
    for name in character_names:
        print(f"  - {name}")
    
    # LLM extraction
    print("\n🤖 Calling LLM for detailed character extraction...")
    llm = ChatOpenAI(**get_llm_config("phase4", "character_extraction"))
    structured_llm = llm.with_structured_output(CharacterExtractionOutput, method="function_calling")
    
    # Limit screenplay text for context (first 10K chars)
    screenplay_sample = screenplay_text[:10000]
    
    extraction_prompt = f"""
Analyze this screenplay and extract ALL unique characters with complete details.

SCREENPLAY (sample):
{screenplay_sample}

CHARACTER NAMES FOUND IN DIALOGUE: {', '.join(character_names)}

For each character, extract:

1. NAMES:
   - name: Character name as appears in dialogue (e.g., "ARJUN")
   - full_name: Full character name if mentioned (e.g., "Inspector Arjun Rao")

2. BASIC INFO:
   - age: Exact age or range (e.g., "mid-40s", "25", "early 20s")
   - gender: male/female/non-binary
   - ethnicity: If mentioned in text (e.g., "Indian", "British", "African-American")

3. PHYSICAL DESCRIPTION:
   - Complete physical description from action lines
   - height: If mentioned (e.g., "5'10\"", "tall", "short")
   - build: Body type (e.g., "athletic", "slender", "stocky", "weathered")
   - face_description: Face features (e.g., "rugged, square jaw, stress lines")
   - eyes: Color and expression (e.g., "dark brown, intense, tired")
   - hair: Color, style, length (e.g., "short black with grey streaks")
   - distinctive_marks: Scars, tattoos, etc. if mentioned

4. CHARACTER TRAITS:
   - personality_traits: List from descriptions (e.g., ["introspective", "determined"])
   - typical_expression: Common facial expression if noted

5. APPEARANCES:
   - scenes_appeared: List of scene numbers where character appears

IMPORTANT RULES:
- Extract ONLY from the screenplay text
- Don't invent details not present in the text
- If a detail isn't mentioned, use "not specified" or leave as None
- Use exact quotes from action lines for descriptions
- Be precise with physical details (these will be used for AI image generation)

Return a structured list of all characters.
"""
    
    result = structured_llm.invoke(extraction_prompt)
    print(f"✓ LLM extracted {len(result.characters)} characters")
    
    # Post-process: assign IDs, generate prompts, extract costumes
    print("\n📦 Post-processing character data...")
    characters_database = []
    
    for idx, char in enumerate(result.characters, 1):
        character_id = f"char_{idx:03d}"
        
        print(f"\nProcessing {char.name} (#{idx})...")
        
        # Generate image prompt
        image_prompt = generate_character_image_prompt(char)
        print(f"  ✓ Generated image prompt")
        
        # Build costume dictionary
        costumes_by_scene = {}
        for scene_num in char.scenes_appeared:
            costume = extract_costume_for_scene(screenplay_text, char.name, scene_num)
            if costume:
                costumes_by_scene[str(scene_num)] = costume
                print(f"  ✓ Found costume for scene {scene_num}")
        
        # Build character database entry
        character_entry = {
            "character_id": character_id,
            "name": char.name,
            "full_name": char.full_name,
            "age": char.age,
            "gender": char.gender,
            "ethnicity": char.ethnicity,
            "base_physical_description": char.physical_description,
            "permanent_features": {
                "height": char.height,
                "build": char.build,
                "face": char.face_description,
                "eyes": char.eyes,
                "hair": char.hair,
                "distinctive_marks": char.distinctive_marks
            },
            "personality_traits": char.personality_traits,
            "scenes_appeared": char.scenes_appeared,
            "costumes_by_scene": costumes_by_scene,
            "typical_expression": char.typical_expression,
            "image_generation_prompt": image_prompt
        }
        
        # ===== CHARACTER ENHANCEMENT =====
        # Automatically enhance characters with missing/generic details
        from phase4_extraction.character_enhancement import should_enhance_character, enhance_character_description
        
        if should_enhance_character(character_entry):
            print(f"  🎨 Enhancing character description...")
            enhancement_result = enhance_character_description(character_entry, screenplay_text)
            
            if enhancement_result.get('enhanced_features'):
                character_entry['enhancement'] = enhancement_result
                print(f"  ✓ Character enhanced with inferred details")
                
                # Update image prompt with enhanced version if available
                if enhancement_result.get('enhanced_image_prompt'):
                    character_entry['image_generation_prompt_enhanced'] = enhancement_result['enhanced_image_prompt']
            else:
                print(f"  ⚠️ Enhancement skipped (error occurred)")
        else:
            print(f"  ℹ️  Enhancement not needed (sufficient detail)")
        
        characters_database.append(character_entry)
        print(f"  ✓ Added to database")
    
    print("\n" + "=" * 80)
    print(f"✅ CHARACTER EXTRACTION COMPLETE")
    print(f"   Total characters: {len(characters_database)}")
    print("=" * 80 + "\n")
    
    return {"characters_database": characters_database}
