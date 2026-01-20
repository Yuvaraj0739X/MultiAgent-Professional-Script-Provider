"""
Character Enhancement Module
Automatically infers missing physical details for photorealistic image generation.
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from config import get_llm_config


def enhance_character_description(character: Dict[str, Any], screenplay_text: str) -> Dict[str, Any]:
    """
    Enhance character with inferred physical details.
    
    Uses AI to intelligently infer missing details based on:
    - Name (ethnicity/cultural background)
    - Age (aging characteristics)
    - Gender (typical features)
    - Profession (physical impact)
    - Context from screenplay
    
    Args:
        character: Basic character data from extraction
        screenplay_text: Full screenplay for context
    
    Returns:
        Enhanced character data with complete physical specifications
    """
    
    llm = ChatOpenAI(**get_llm_config("phase4", "character_extraction"))
    
    # Extract profession from context
    profession = extract_profession_from_name_or_description(character)
    
    enhancement_prompt = f"""
You are enhancing a character description for PHOTOREALISTIC image generation.

CHARACTER INFO:
Name: {character.get('name', 'Unknown')} ({character.get('full_name', 'Unknown')})
Age: {character.get('age', 'Unknown')}
Gender: {character.get('gender', 'Unknown')}
Current Description: {character.get('base_physical_description', 'No description')}
Profession/Role: {profession}

TASK: Infer COMPLETE, SPECIFIC physical details for image generation.

Based on the name, age, profession, and context, provide:

1. HEIGHT:
   - Realistic height with measurement
   - Consider: gender, ethnicity (inferred from name), profession
   - Example: "5'9\" (175 cm) - average height for Indian male, mid-40s"
   - Be SPECIFIC with numbers

2. BUILD:
   - Detailed body type description
   - Consider: age, profession, lifestyle
   - Example: "average to stocky build - physically fit from police training, but showing signs of middle age with slight weight around midsection from years of desk work and stress"
   - Describe muscle tone, weight distribution

3. EYES:
   - Specific color (culturally appropriate for ethnicity)
   - Eye shape, expression, distinctive features
   - Example: "dark brown, almost black - deep-set eyes with slight bags underneath from irregular sleep patterns, piercing gaze that comes from years of interrogations, subtle crow's feet at corners"
   - Include emotional/expressive qualities

4. HAIR:
   - Style, length, texture, color
   - Age-appropriate (graying pattern, thinning, etc.)
   - Example: "black hair, short-cropped in professional style (about 1-2 inches long), beginning to gray at the temples and scattered gray throughout, slightly thinning at the crown - typical for mid-40s Indian male"
   - Be SPECIFIC about length, style, condition

5. FACE DETAILS:
   - Specific facial structure: nose shape, jaw, cheekbones, chin
   - Skin texture and condition
   - Aging signs appropriate for stated age
   - Example: "angular face with prominent cheekbones, strong jawline, slightly weathered skin with visible pores and texture from years of sun exposure and late nights, deep nasolabial folds, crow's feet around eyes"
   - Paint a DETAILED picture

6. DISTINCTIVE MARKS:
   - Scars, wrinkles, or marks based on profession/age/lifestyle
   - Example: "faint scar on left eyebrow from old injury, slight stubble suggesting long work hours without time for grooming, calloused hands from years of fieldwork, overall appearance of someone who's seen too much"
   - Make it character-specific

7. OVERALL IMPRESSION:
   - How these features combine
   - The "look" or "vibe" of the character
   - Example: "Overall appearance: experienced, world-weary professional who maintains dignity despite obvious fatigue. The kind of face that has seen hardship but retained humanity."

CRITICAL RULES:
✓ Make REALISTIC inferences based on profession, age, cultural background
✓ Be SPECIFIC - vague descriptions don't work for AI image generation
✓ Use cultural awareness for ethnicity-appropriate features (inferred from name)
✓ Include aging signs appropriate for stated age
✓ Consider profession's impact on appearance (police = fit but weathered, desk job = softer, etc.)
✓ Use photographic/artistic terminology
✓ Provide measurements where applicable (height, hair length, etc.)
✓ Make inferences that help an artist/AI create a consistent, realistic character

Output format:
Return a JSON object with these exact keys:
{{
    "height": "specific height with measurement and context",
    "build": "detailed body type description",
    "eyes": "specific color and characteristics",
    "hair": "complete hair description",
    "face_detailed": "detailed facial features",
    "distinctive_marks": "specific marks, scars, or characteristics",
    "overall_impression": "how features combine into coherent character",
    "enhancement_notes": "brief note on inference reasoning"
}}
"""
    
    try:
        # Get enhancement from LLM
        response = llm.invoke(enhancement_prompt)
        
        # Parse response (LLM should return JSON-like structure)
        import json
        import re
        
        # Extract JSON from response
        content = response.content
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            enhanced_data = json.loads(json_match.group())
        else:
            # Fallback: create basic structure
            enhanced_data = {
                "height": "average height for gender and ethnicity",
                "build": "average build appropriate for age and profession",
                "eyes": "color appropriate for ethnicity",
                "hair": "style appropriate for age and profession",
                "face_detailed": content[:200] if content else "detailed facial features",
                "distinctive_marks": "age-appropriate characteristics",
                "overall_impression": "professional appearance",
                "enhancement_notes": "basic inference from available data"
            }
        
        # Create enhanced image prompt
        enhanced_prompt = generate_enhanced_image_prompt(character, enhanced_data)
        
        return {
            "enhanced_features": enhanced_data,
            "enhanced_image_prompt": enhanced_prompt,
            "enhancement_method": "ai_inferred",
            "enhancement_confidence": "high" if json_match else "medium"
        }
        
    except Exception as e:
        print(f"    ⚠️ Enhancement failed: {e}")
        return {
            "enhanced_features": None,
            "enhanced_image_prompt": None,
            "enhancement_method": "failed",
            "enhancement_error": str(e)
        }


def extract_profession_from_name_or_description(character: Dict[str, Any]) -> str:
    """Extract profession from character name or description."""
    full_name = character.get('full_name', '').lower()
    name = character.get('name', '').lower()
    description = character.get('base_physical_description', '').lower()
    
    # Common profession indicators
    professions = {
        'inspector': 'police inspector',
        'detective': 'detective',
        'marshal': 'military marshal',
        'general': 'military general',
        'captain': 'military captain',
        'doctor': 'medical doctor',
        'professor': 'professor/academic',
        'officer': 'military officer',
        'sergeant': 'police/military sergeant',
        'emperor': 'emperor/ruler',
        'king': 'king/ruler',
        'queen': 'queen/ruler'
    }
    
    # Check full name
    for key, profession in professions.items():
        if key in full_name:
            return profession
    
    # Check name
    for key, profession in professions.items():
        if key in name:
            return profession
    
    # Check description
    for key, profession in professions.items():
        if key in description:
            return profession
    
    return "unknown profession"


def generate_enhanced_image_prompt(character: Dict[str, Any], enhanced_data: Dict[str, Any]) -> str:
    """
    Generate enhanced image prompt with complete physical specifications.
    
    Args:
        character: Basic character data
        enhanced_data: Enhanced physical features
    
    Returns:
        Complete photorealistic image prompt
    """
    
    parts = [
        "Photorealistic portrait",
        character.get('gender', 'person'),
        character.get('age', 'adult'),
        enhanced_data.get('height', 'average height'),
        enhanced_data.get('build', 'average build'),
        enhanced_data.get('face_detailed', 'neutral face'),
        enhanced_data.get('eyes', 'expressive eyes'),
        enhanced_data.get('hair', 'neat hair'),
        enhanced_data.get('distinctive_marks', ''),
        character.get('base_physical_description', ''),
        enhanced_data.get('overall_impression', 'professional appearance'),
    ]
    
    # Filter empty parts
    parts = [p for p in parts if p and p.strip()]
    
    # Add technical specifications
    parts.extend([
        "neutral grey background",
        "soft studio lighting from 45 degrees",
        "16:9 aspect ratio",
        "1920x1080 resolution",
        "widescreen cinematic frame",
        "8K quality",
        "hyperrealistic",
        "professional photography",
        "front-facing headshot",
        "shoulders visible in frame",
        "NO letterboxing",
        "NO pillarboxing",
        "fills entire 16:9 rectangle"
    ])
    
    return ", ".join(parts)


def should_enhance_character(character: Dict[str, Any]) -> bool:
    """
    Determine if character needs enhancement.
    
    Returns True if character has missing or generic features.
    """
    features = character.get('permanent_features', {})
    
    # Check for missing or generic values
    missing_or_generic = [
        not features.get('height'),
        features.get('build') in [None, 'not specified', ''],
        features.get('eyes') in [None, 'not specified', ''],
        features.get('hair') in [None, 'not specified', ''],
        not features.get('face'),
        not features.get('distinctive_marks')
    ]
    
    # Enhance if 3 or more features are missing
    return sum(missing_or_generic) >= 3
