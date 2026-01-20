"""
Phase 4 - Node 2: Voice Profile Extraction
Extracts voice profiles for all characters by analyzing dialogue patterns,
delivery notes, and speech characteristics.
"""

from langchain_openai import ChatOpenAI
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..state import Phase4State
from ..models import VoiceProfile
from ..utils import (
    extract_character_dialogue,
    format_dialogue_for_analysis
)

# Import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import get_llm_config


def voice_profile_extraction_node(state: Phase4State) -> Dict:
    """
    Extract voice profiles for all characters.
    
    Process:
    1. Get characters from previous node
    2. For each character, extract all dialogue
    3. Analyze parentheticals for delivery notes
    4. Determine voice characteristics from descriptions
    5. Extract speech patterns from dialogue content
    6. Map emotional variations
    7. Create consistency profile for AI voice generation
    
    Uses:
    - Model: gpt-4o
    - Temperature: 0.4 (somewhat creative but consistent)
    - Structured output: VoiceProfile per character
    
    Returns:
        Dict updating 'characters_database' with voice profiles
    """
    
    print("=" * 80)
    print("NODE 2: VOICE PROFILE EXTRACTION")
    print("=" * 80)
    
    screenplay_text = state['screenplay_text']
    characters = state['characters_database']
    
    print(f"Analyzing voice profiles for {len(characters)} characters...")
    
    llm = ChatOpenAI(**get_llm_config("phase4", "voice_extraction"))
    
    # Process each character
    for idx, character in enumerate(characters, 1):
        char_name = character['name']
        print(f"\n[{idx}/{len(characters)}] Analyzing voice for {char_name}...")
        
        # Extract all dialogue for this character
        character_dialogue = extract_character_dialogue(screenplay_text, char_name)
        
        if not character_dialogue:
            print(f"  ⚠️  No dialogue found for {char_name}, skipping voice profile")
            continue
        
        print(f"  ✓ Found {len(character_dialogue)} dialogue lines")
        
        # Build analysis prompt
        voice_analysis_prompt = f"""
Analyze the voice and speech patterns for: {character['full_name']}

CHARACTER INFO:
- Name: {character['full_name']}
- Age: {character['age']}
- Gender: {character['gender']}
- Ethnicity: {character.get('ethnicity', 'not specified')}
- Description: {character['base_physical_description']}
- Personality: {', '.join(character['personality_traits'])}

ALL DIALOGUE:
{format_dialogue_for_analysis(character_dialogue[:20])}  # First 20 lines

Extract complete voice profile:

1. ACCENT/DIALECT:
   - accent: Primary accent (e.g., "Indian English", "British RP", "American Southern")
   - dialect_notes: Specific dialect details, regional markers, education level in speech

2. VOICE CHARACTERISTICS:
   - pitch: "high", "medium", "low", "medium-low", etc.
   - tone: Quality of voice (e.g., "gravelly", "smooth", "sharp", "warm", "cold", "raspy")
   - pace: Speaking speed ("fast", "moderate", "slow", "deliberate", "measured")
   - volume: Typical volume ("quiet", "normal", "loud", "soft", "booming")
   - distinctive_qualities: List unique voice qualities (e.g., ["raspy when tired", "voice drops when angry"])

3. SPEECH PATTERNS:
   - formality: Level of formality ("formal", "professional", "casual", "colloquial", "mixed")
   - sentence_structure: How they construct sentences (e.g., "short and direct", "long and complex", "fragmented under stress")
   - common_phrases: List of phrases they repeat (e.g., ["Listen to me", "What have you done"])
   - verbal_tics: Verbal habits (e.g., ["pauses before important statements", "sighs when frustrated"])
   - slang: Type and frequency of slang usage

4. EMOTIONAL VARIATIONS:
   For each emotional state, describe how voice changes:
   - calm: {{pitch, pace, tone, notes}}
   - stressed: {{pitch, pace, tone, notes}}
   - angry: {{pitch, pace, tone, notes}}
   - tired: {{pitch, pace, tone, notes}}
   - determined: {{pitch, pace, tone, notes}}
   (Add more if relevant: happy, sad, scared, etc.)

5. DIALOGUE EXAMPLES (at least 3-5):
   For key dialogue lines, provide:
   - scene: Scene number or context
   - line: The actual dialogue
   - context: What's happening in the scene
   - emotional_state: Character's emotional state
   - pitch: Specific pitch for this line
   - pace: Specific pace for this line
   - volume: Specific volume for this line
   - tone: Specific tone for this line
   - emphasis: Which words are stressed, where pauses occur
   - notes: Detailed delivery notes

6. AI VOICE GENERATION PROFILE:
   - recommended_service: "ElevenLabs" or "Azure TTS"
   - voice_type: Description for voice selection (e.g., "Mature Indian Male, Professional")
   - stability: 0.0-1.0 (how consistent voice should be)
   - similarity_boost: 0.0-1.0 (how much to match reference)
   - style_exaggeration: 0.0-1.0 (how expressive)
   - speaker_boost: true/false
   - reference_audio_needed: true/false
   - notes: Implementation notes

IMPORTANT:
- Base analysis on actual dialogue in the screenplay
- Note parentheticals in original dialogue: (bleary), (warily), (softly)
- Consider character background for accent/dialect
- Maintain consistency with character's personality
- Provide specific, actionable voice direction
"""
        
        # Get structured voice profile
        print(f"  🤖 Analyzing voice characteristics...")
        structured_llm = llm.with_structured_output(VoiceProfile, method="function_calling")
        
        try:
            voice_profile = structured_llm.invoke(voice_analysis_prompt)
            
            # Convert to dict and add to character
            character['voice_profile'] = voice_profile.dict()
            
            print(f"  ✓ Voice profile created")
            print(f"    - Accent: {voice_profile.accent}")
            print(f"    - Pitch: {voice_profile.voice_characteristics.pitch}")
            print(f"    - Tone: {voice_profile.voice_characteristics.tone}")
            
            # Safe access to emotional_variations
            emotional_vars = voice_profile.emotional_variations
            if emotional_vars and isinstance(emotional_vars, dict):
                print(f"    - Emotional variations: {len(emotional_vars)}")
            else:
                print(f"    - Emotional variations: 0")
            
            # Safe access to dialogue_examples
            dialogue_examples = voice_profile.dialogue_examples
            if dialogue_examples and isinstance(dialogue_examples, list):
                print(f"    - Dialogue examples: {len(dialogue_examples)}")
            else:
                print(f"    - Dialogue examples: 0")
            
        except Exception as e:
            print(f"  ❌ Error creating voice profile: {e}")
            # Add placeholder voice profile
            character['voice_profile'] = {
                "error": str(e),
                "accent": "not analyzed",
                "voice_characteristics": {}
            }
    
    print("\n" + "=" * 80)
    print(f"✅ VOICE PROFILE EXTRACTION COMPLETE")
    print(f"   Profiles created: {sum(1 for c in characters if 'voice_profile' in c and 'error' not in c['voice_profile'])}")
    print("=" * 80 + "\n")
    
    return {"characters_database": characters}
