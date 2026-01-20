"""
Phase 4 - Node 3: Environment Extraction
Extracts all environments/locations with permanent fixtures only.
These create "anchor" images - empty rooms for character compositing.
"""

from langchain_openai import ChatOpenAI
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..state import Phase4State
from ..models import Environment
from ..utils import (
    extract_scene_headings,
    group_locations_by_place,
    extract_location_descriptions,
    extract_time_variations,
    generate_environment_image_prompt
)

# Import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import get_llm_config


def environment_extraction_node(state: Phase4State) -> Dict:
    """
    Extract all environments/locations from screenplay.
    
    Process:
    1. Parse all scene headings (INT./EXT. LOCATION - TIME)
    2. Group duplicate locations (same place, different times)
    3. Extract permanent fixtures from action lines
    4. Determine lighting setup per time of day
    5. Calculate anchor camera position for wide shot
    6. Generate environment image prompt (empty room)
    
    CRITICAL: Extract ONLY permanent fixtures.
    Props, characters, temporary objects are excluded.
    
    Uses:
    - Model: gpt-4o
    - Temperature: 0.3 (factual extraction)
    - Structured output: Environment
    
    Returns:
        Dict with 'environments_database' key
    """
    
    print("=" * 80)
    print("NODE 3: ENVIRONMENT EXTRACTION")
    print("=" * 80)
    
    screenplay_text = state['screenplay_text']
    scene_breakdown = state.get('scene_breakdown', [])
    
    print(f"Analyzing environments from {len(scene_breakdown)} scenes...")
    
    # Parse scene headings
    scene_headings = extract_scene_headings(screenplay_text)
    print(f"✓ Found {len(scene_headings)} scene headings")
    
    # Group by location (ignoring time of day)
    location_groups = group_locations_by_place(scene_headings)
    print(f"✓ Identified {len(location_groups)} unique locations:")
    for location_name in location_groups.keys():
        print(f"  - {location_name}")
    
    llm = ChatOpenAI(**get_llm_config("phase4", "environment_extraction"))
    
    environments_database = []
    
    for idx, (location_name, scenes) in enumerate(location_groups.items(), 1):
        print(f"\n[{idx}/{len(location_groups)}] Processing: {location_name}")
        print(f"  Used in {len(scenes)} scenes: {[s['scene_number'] for s in scenes]}")
        
        # Get all action descriptions for this location
        location_descriptions = extract_location_descriptions(screenplay_text, scenes)
        
        # Get scene identifiers (handle both 'scene_heading' and 'location' keys)
        scene_identifiers = []
        for s in scenes:
            if 'scene_heading' in s:
                scene_identifiers.append(s['scene_heading'])
            elif 'location' in s:
                scene_identifiers.append(s['location'])
            else:
                scene_identifiers.append(f"Scene {s.get('scene_number', '?')}")
        
        extraction_prompt = f"""
Extract permanent environmental fixtures for: {location_name}

LOCATION APPEARS IN THESE SCENES:
{scene_identifiers}

ACTION DESCRIPTIONS FROM ALL SCENES:
{location_descriptions[:2000]}  # First 2000 chars

Extract ONLY PERMANENT fixtures that would be in an EMPTY room/location:

✅ INCLUDE (Permanent):
- Walls, floor, ceiling (materials, color, condition)
- Windows, doors (size, position, style, number)
- Built-in furniture (cabinets, shelves, counters)
- Large furniture that's fixed (beds, desks, wardrobes)
- Architectural fixtures (ceiling fans, light fixtures, built-in lighting)
- Structural elements (beams, columns, stairs, railings)

❌ EXCLUDE (Temporary/Props):
- Characters (will be composited later)
- Props (clock, phone, photograph, papers, books)
- Small objects (cups, pens, small decorations)
- Temporary items (food, clothes on furniture, bags)
- Anything mentioned as being picked up, moved, or used
- Anything that appears mid-scene

Also determine:

1. TYPE AND CATEGORY:
   - type: "interior" or "exterior"
   - category: "residential_private", "residential_shared", "commercial", "outdoor", "vehicle", etc.

2. ROOM DETAILS:
   - name: Full location name
   - description: Overall description of the space
   - walls: Material, color, condition (e.g., "beige walls with peeling paint in corners")
   - floor: Material, condition (e.g., "old wooden floor with worn carpet")
   - ceiling: Material, color, features (e.g., "white ceiling, slightly yellowed")

3. FURNITURE (Permanent):
   - furniture_list: List of permanent furniture pieces
     Examples: "double bed with metal frame", "wooden nightstand", "old wardrobe"

4. FIXTURES:
   - fixtures_list: List of built-in fixtures
     Examples: "ceiling fan with 3 blades", "window with curtains", "door to hallway"

5. LIGHTING:
   - default_lighting: Primary lighting condition
   - light_sources: List of all light sources (natural and artificial)
   - atmosphere: Overall mood/atmosphere (e.g., "claustrophobic, shadows on walls")

6. DIMENSIONS:
   - size: Approximate size (e.g., "12 feet x 10 feet", "large", "cramped")
   - ceiling_height: Height (e.g., "9 feet", "low", "high")
   - layout_description: How furniture/elements are positioned

7. CAMERA SETUP (for anchor image):
   - camera_position: Where camera should be placed (e.g., "corner opposite bed, elevated 7 feet")
   - camera_coverage: What the camera captures (e.g., "entire room - bed, wardrobe, window, door visible")

CRITICAL RULES:
- Describe the space as if it's EMPTY and ready for characters to enter
- Like a stage set before actors arrive
- Only permanent elements that define the space
- No people, no props, no temporary objects
- Think: "What would be in an architectural photograph of this empty space?"

Generate description suitable for AI image generation of empty environment.
"""
        
        print(f"  🤖 Analyzing permanent fixtures...")
        structured_llm = llm.with_structured_output(Environment, method="function_calling")
        
        try:
            environment = structured_llm.invoke(extraction_prompt)
            
            # Generate environment image prompt
            env_prompt = generate_environment_image_prompt(environment, location_name)
            print(f"  ✓ Generated anchor image prompt")
            
            # Track time variations
            time_variations = extract_time_variations(scenes)
            print(f"  ✓ Time variations: {list(time_variations.keys())}")
            
            environment_data = {
                "environment_id": f"env_{idx:03d}",
                "name": location_name,
                "type": environment.type,
                "location_category": environment.category,
                "base_description": environment.description,
                "permanent_elements": {
                    "walls": environment.walls,
                    "floor": environment.floor,
                    "ceiling": environment.ceiling,
                    "furniture": environment.furniture_list,
                    "fixtures": environment.fixtures_list
                },
                "lighting_setup": {
                    "default": environment.default_lighting,
                    "sources": environment.light_sources,
                    "atmosphere": environment.atmosphere
                },
                "dimensions": {
                    "size": environment.size,
                    "ceiling_height": environment.ceiling_height,
                    "layout": environment.layout_description
                },
                "camera_setup": {
                    "anchor_position": environment.camera_position,
                    "coverage": environment.camera_coverage,
                    "style": "elevated wide angle shot - cinematic architectural photography"
                },
                "scenes_used": [s['scene_number'] for s in scenes],
                "time_variations": time_variations,
                "image_generation_prompt": env_prompt
            }
            
            environments_database.append(environment_data)
            print(f"  ✓ Added to database")
            print(f"    - Furniture: {len(environment.furniture_list)} pieces")
            print(f"    - Fixtures: {len(environment.fixtures_list)} items")
            
        except Exception as e:
            print(f"  ❌ Error extracting environment: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ ENVIRONMENT EXTRACTION COMPLETE")
    print(f"   Total environments: {len(environments_database)}")
    print(f"   Ready for anchor image generation")
    print("=" * 80 + "\n")
    
    return {"environments_database": environments_database}
