"""
Phase 4: Utility Functions
Helper functions for screenplay parsing, character/environment extraction,
and storyboard planning.
"""

import re
import json
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path


# ===== FOUNTAIN FORMAT PARSING =====

SCENE_HEADING_PATTERN = r'^(INT\.|EXT\.|INT\./EXT\.)\s+(.+?)\s+-\s+(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER)'
CHARACTER_PATTERN = r'^([A-Z][A-Z\s]+)$'
DIALOGUE_PATTERN = r'^\s{20,}'

# ===== CHARACTER NAME FILTERING =====

# Blacklist of non-character screenplay markers
CHARACTER_NAME_BLACKLIST = {
    # Transitions
    'CUT TO',
    'FADE IN',
    'FADE OUT',
    'FADE TO BLACK',
    'DISSOLVE TO',
    'SMASH CUT TO',
    'MATCH CUT TO',
    'JUMP CUT TO',
    'WIPE TO',
    'IRIS IN',
    'IRIS OUT',
    
    # Scene markers
    'END SCENE',
    'BEGIN SCENE',
    'FLASHBACK',
    'FLASH FORWARD',
    'MONTAGE',
    'END MONTAGE',
    'INTERCUT',
    'END INTERCUT',
    
    # Time markers
    'LATER',
    'MEANWHILE',
    'MOMENTS LATER',
    'SAME TIME',
    'CONTINUOUS',
    'THE NEXT DAY',
    'THE NEXT MORNING',
    
    # Technical
    'TITLE',
    'TITLE CARD',
    'SUPER',
    'INSERT',
    'BACK TO SCENE',
    'CONTINUED',
    'CONT\'D',
    'MORE',
    'THE END',
    
    # Common artifacts
    'END',
    'BEGIN',
    'START',
    'STOP'
}


def is_valid_character_name(name: str) -> bool:
    """
    Validate if a name is a real character (not a screenplay marker).
    
    This function filters out:
    - Screenplay transitions (CUT TO, FADE IN, etc.)
    - Scene markers (END SCENE, etc.)
    - Time markers (LATER, MEANWHILE, etc.)
    - Markdown/code artifacts
    
    Args:
        name: Potential character name (usually in ALL CAPS from Fountain)
        
    Returns:
        True if valid character name, False if it's a marker/artifact
    """
    if not name or not isinstance(name, str):
        return False
    
    # Normalize to uppercase and strip whitespace
    normalized = name.strip().upper()
    
    # Too short or empty
    if len(normalized) < 2:
        return False
    
    # Check blacklist
    if normalized in CHARACTER_NAME_BLACKLIST:
        return False
    
    # Check for transition patterns (ends with " TO")
    if normalized.endswith(' TO'):
        return False
    
    # Check for scene heading patterns (shouldn't happen but be defensive)
    scene_prefixes = ['INT.', 'EXT.', 'INT/EXT.', 'I/E', 'EST.']
    if any(normalized.startswith(prefix) for prefix in scene_prefixes):
        return False
    
    # Check for markdown/code artifacts
    if '```' in normalized or normalized.startswith('#'):
        return False
    
    # Check if it's just a number or single letter
    if normalized.isdigit() or (len(normalized) == 1 and normalized.isalpha()):
        return False
    
    return True


def filter_character_names(character_names: list) -> dict:
    """
    Filter character names, separating valid characters from screenplay markers.
    
    Args:
        character_names: List of potential character names extracted from screenplay
        
    Returns:
        Dictionary with:
        - 'valid': List of valid character names
        - 'filtered': List of filtered-out non-character entries
    """
    valid = []
    filtered = []
    
    for name in character_names:
        if is_valid_character_name(name):
            valid.append(name)
        else:
            filtered.append(name)
    
    # Remove duplicates and sort
    return {
        'valid': sorted(list(set(valid))),
        'filtered': sorted(list(set(filtered)))
    }


def parse_fountain_screenplay(screenplay_text: str) -> Dict[str, Any]:
    """
    Parse Fountain format screenplay into structured data.
    
    FIXES:
    - Removes markdown ``` artifacts from LLM generation
    - Deduplicates consecutive identical scene headings
    - Handles malformed Fountain from LLM output
    
    Returns:
        Dict with scenes, dialogue, action lines, etc.
    """
    lines = screenplay_text.split('\n')
    
    parsed = {
        'title': '',
        'scenes': [],
        'all_dialogue': [],
        'all_action_lines': []
    }
    
    current_scene = None
    current_character = None
    in_dialogue = False
    last_scene_heading = None  # ← NEW: Track to prevent duplicates
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            in_dialogue = False
            current_character = None
            continue
        
        # ← NEW: SKIP MARKDOWN ARTIFACTS
        if stripped == '```' or stripped.startswith('```'):
            continue
        
        # Title page (first non-empty line if not scene heading)
        if not parsed['title'] and not re.match(SCENE_HEADING_PATTERN, stripped):
            parsed['title'] = stripped
            continue
        
        # Scene heading
        scene_match = re.match(SCENE_HEADING_PATTERN, stripped)
        if scene_match:
            # ← NEW: DEDUPLICATE consecutive same headings
            if stripped.upper() == last_scene_heading:
                continue  # Skip this duplicate
            
            # New scene detected
            if current_scene:
                parsed['scenes'].append(current_scene)
            
            last_scene_heading = stripped.upper()  # ← NEW: Remember this heading
            
            current_scene = {
                'heading': stripped,
                'type': scene_match.group(1),
                'location': scene_match.group(2).strip(),
                'time': scene_match.group(3),
                'action_lines': [],
                'dialogue': [],
                'line_start': i
            }
            in_dialogue = False
            current_character = None
            continue
        
        # Character name (all caps)
        if current_scene and re.match(CHARACTER_PATTERN, stripped) and len(stripped) > 1:
            current_character = stripped
            in_dialogue = True
            continue
        
        # Dialogue (indented or following character name)
        if current_scene and in_dialogue and current_character:
            # Parenthetical (actor direction)
            if stripped.startswith('(') and stripped.endswith(')'):
                parenthetical = stripped
            else:
                # Actual dialogue
                dialogue_entry = {
                    'character': current_character,
                    'line': stripped,
                    'scene_heading': current_scene['heading']
                }
                current_scene['dialogue'].append(dialogue_entry)
                parsed['all_dialogue'].append(dialogue_entry)
            continue
        
        # Action line (everything else)
        if current_scene:
            current_scene['action_lines'].append(stripped)
            parsed['all_action_lines'].append({
                'text': stripped,
                'scene_heading': current_scene['heading']
            })
    
    # Add last scene
    if current_scene:
        parsed['scenes'].append(current_scene)
    
    return parsed


def extract_scene_headings(screenplay_text: str) -> List[Dict[str, str]]:
    """Extract all scene headings from screenplay."""
    lines = screenplay_text.split('\n')
    headings = []
    scene_number = 1
    
    for line in lines:
        match = re.match(SCENE_HEADING_PATTERN, line.strip())
        if match:
            headings.append({
                'scene_number': scene_number,
                'heading': line.strip(),
                'type': match.group(1),
                'location': match.group(2).strip(),
                'time': match.group(3)
            })
            scene_number += 1
    
    return headings


def extract_scene_text(screenplay_text: str, scene_number: int) -> str:
    """Extract text for a specific scene."""
    parsed = parse_fountain_screenplay(screenplay_text)
    
    if scene_number <= len(parsed['scenes']):
        scene = parsed['scenes'][scene_number - 1]
        
        # Reconstruct scene text
        text_parts = [scene['heading'], '']
        text_parts.extend(scene['action_lines'])
        
        for dialogue in scene['dialogue']:
            text_parts.append(f"\n{dialogue['character']}")
            text_parts.append(dialogue['line'])
        
        return '\n'.join(text_parts)
    
    return ""


def extract_scene_text_by_heading(screenplay_text: str, scene_heading: str) -> str:
    """
    Extract text for a specific scene by matching the scene heading.
    
    Uses ultra-flexible matching to handle:
    - Exact heading matches
    - Partial matches (ignoring time)
    - Location-only matches (ignoring INT/EXT and time)
    
    Args:
        screenplay_text: Full screenplay text
        scene_heading: Scene heading to match (e.g., "INT. HITLER'S COMMAND TENT - DAY")
    
    Returns:
        Scene text if found, empty string otherwise
    """
    parsed = parse_fountain_screenplay(screenplay_text)
    
    # Normalize heading for comparison (remove extra spaces, case-insensitive)
    target_heading = scene_heading.strip().upper()
    
    # Find scene by heading match
    for scene in parsed['scenes']:
        scene_head = scene['heading'].strip().upper()
        
        # Try exact match first
        if scene_head == target_heading:
            # Reconstruct scene text
            text_parts = [scene['heading'], '']
            text_parts.extend(scene['action_lines'])
            
            for dialogue in scene['dialogue']:
                text_parts.append(f"\n{dialogue['character']}")
                text_parts.append(dialogue['line'])
            
            return '\n'.join(text_parts)
        
        # Try partial match (in case of slight variations)
        # Extract the core location part (e.g., "INT. HITLER'S COMMAND TENT")
        target_core = target_heading.rsplit(' - ', 1)[0] if ' - ' in target_heading else target_heading
        scene_core = scene_head.rsplit(' - ', 1)[0] if ' - ' in scene_head else scene_head
        
        if target_core == scene_core:
            # Found a match with same location
            text_parts = [scene['heading'], '']
            text_parts.extend(scene['action_lines'])
            
            for dialogue in scene['dialogue']:
                text_parts.append(f"\n{dialogue['character']}")
                text_parts.append(dialogue['line'])
            
            return '\n'.join(text_parts)
    
    # ← NEW: ULTRA FLEXIBLE MATCHING (for scenes with time variations)
    # Extract just the location name, ignoring INT/EXT and time
    # e.g., "EXT. FRENCH COUNTRYSIDE - DAY" → "FRENCH COUNTRYSIDE"
    
    target_location = target_heading
    # Remove INT./EXT. prefix
    if target_location.startswith('INT.'):
        target_location = target_location[4:].strip()
    elif target_location.startswith('EXT.'):
        target_location = target_location[4:].strip()
    elif target_location.startswith('INT/EXT.'):
        target_location = target_location[8:].strip()
    
    # Remove time of day (everything after last hyphen)
    if ' - ' in target_location:
        target_location = target_location.rsplit(' - ', 1)[0].strip()
    
    # Try to find ANY scene with this location (ignore time differences)
    best_match = None
    best_match_length = 0
    
    for scene in parsed['scenes']:
        scene_head = scene['heading'].strip().upper()
        scene_location = scene_head
        
        # Remove INT./EXT. prefix
        if scene_location.startswith('INT.'):
            scene_location = scene_location[4:].strip()
        elif scene_location.startswith('EXT.'):
            scene_location = scene_location[4:].strip()
        elif scene_location.startswith('INT/EXT.'):
            scene_location = scene_location[8:].strip()
        
        # Remove time of day
        if ' - ' in scene_location:
            scene_location = scene_location.rsplit(' - ', 1)[0].strip()
        
        # Check if locations match
        if target_location == scene_location:
            # Reconstruct scene text
            text_parts = [scene['heading'], '']
            text_parts.extend(scene['action_lines'])
            
            for dialogue in scene['dialogue']:
                text_parts.append(f"\n{dialogue['character']}")
                text_parts.append(dialogue['line'])
            
            scene_text = '\n'.join(text_parts)
            
            # Keep track of longest match (in case multiple instances)
            if len(scene_text) > best_match_length:
                best_match = scene_text
                best_match_length = len(scene_text)
    
    # Return best match if found
    if best_match:
        return best_match
    
    return ""

# ===== CHARACTER EXTRACTION HELPERS =====

def extract_character_names_from_dialogue(parsed_screenplay: Dict) -> List[str]:
    """Extract unique character names from dialogue."""
    characters = set()
    
    for dialogue in parsed_screenplay['all_dialogue']:
        characters.add(dialogue['character'])
    
    return sorted(list(characters))


def extract_character_dialogue(screenplay_text: str, character_name: str) -> List[Dict]:
    """Extract all dialogue for a specific character."""
    parsed = parse_fountain_screenplay(screenplay_text)
    
    character_dialogue = []
    for dialogue in parsed['all_dialogue']:
        if dialogue['character'] == character_name:
            character_dialogue.append(dialogue)
    
    return character_dialogue


def extract_costume_for_scene(screenplay_text: str, character_name: str, scene_number: int) -> Optional[Dict]:
    """Extract costume description for character in specific scene."""
    scene_text = extract_scene_text(screenplay_text, scene_number)
    
    # Look for clothing mentions in action lines
    # This is a simplified version - could be enhanced with LLM
    clothing_keywords = ['wearing', 'dressed in', 'uniform', 'suit', 'clothes']
    
    for line in scene_text.split('\n'):
        if character_name.lower() in line.lower():
            for keyword in clothing_keywords:
                if keyword in line.lower():
                    return {
                        'clothing': line.strip(),
                        'condition': 'as described',
                        'scene_number': scene_number
                    }
    
    return None


# ===== ENVIRONMENT EXTRACTION HELPERS =====

def group_locations_by_place(scene_headings: List[Dict]) -> Dict[str, List[Dict]]:
    """Group scene headings by location (ignoring time of day)."""
    locations = {}
    
    for heading in scene_headings:
        location_key = f"{heading['type']} {heading['location']}"
        
        if location_key not in locations:
            locations[location_key] = []
        
        locations[location_key].append(heading)
    
    return locations


def extract_location_descriptions(screenplay_text: str, scenes: List[Dict]) -> str:
    """Extract all action descriptions for a location across multiple scenes."""
    descriptions = []
    
    for scene in scenes:
        scene_text = extract_scene_text(screenplay_text, scene['scene_number'])
        
        # Get action lines (non-dialogue)
        lines = scene_text.split('\n')
        for line in lines:
            if line.strip() and not re.match(CHARACTER_PATTERN, line.strip()):
                if not re.match(SCENE_HEADING_PATTERN, line.strip()):
                    descriptions.append(line.strip())
    
    return '\n'.join(descriptions)


def extract_time_from_heading(heading: str) -> str:
    """Extract time of day from scene heading."""
    match = re.match(SCENE_HEADING_PATTERN, heading)
    if match:
        return match.group(3)
    return "UNKNOWN"


def extract_time_variations(scenes: List[Dict]) -> Dict[str, Any]:
    """Extract all time variations for a location."""
    variations = {}
    
    for scene in scenes:
        time = scene['time'].lower()
        
        if time not in variations:
            variations[time] = {
                'scene_numbers': [],
                'lighting': '',
                'atmosphere': '',
                'notes': ''
            }
        
        variations[time]['scene_numbers'].append(scene['scene_number'])
    
    return variations


# ===== STORYBOARD PLANNING HELPERS =====

def calculate_optimal_frame_count(scene: Dict) -> int:
    """
    Determine optimal number of frames for a scene.
    
    Factors:
    - Duration (longer = more frames)
    - Complexity (more action beats = more frames)
    - Dialogue (heavy dialogue = fewer frames)
    - Scene type
    """
    duration = scene.get('duration_estimate', 60)
    beat_count = len(scene.get('action_beats', []))
    dialogue_count = len(scene.get('dialogue_segments', []))
    scene_type = scene.get('scene_type', 'medium')
    
    # Base calculation
    if duration <= 30 and beat_count <= 4:
        base_frames = 4
    elif duration <= 60 and beat_count <= 9:
        base_frames = 9
    elif duration > 60:
        base_frames = 16
    else:
        base_frames = 6
    
    # Adjust for dialogue
    if dialogue_count > 5:
        # Dialogue-heavy, can use fewer frames (static shots)
        base_frames = min(base_frames, 6)
    
    # Adjust for action
    if 'action' in scene_type and beat_count > 10:
        # Action-heavy, needs more frames
        base_frames = max(base_frames, 9)
    
    return base_frames


def determine_storyboard_format(complexity: str, duration: int, 
                                 scene_type: str, frame_count: int) -> str:
    """
    Determine optimal storyboard grid format.
    
    Returns: "4x1", "2x3", "3x3", "2x4", "4x4", "3x3+4x1", "custom"
    """
    if frame_count == 4:
        return "4x1"
    elif frame_count <= 6:
        return "2x3"
    elif frame_count <= 9:
        return "3x3"
    elif frame_count <= 8:
        return "2x4"
    elif frame_count <= 16:
        return "4x4"
    elif "dialogue" in scene_type and frame_count > 9:
        return "3x3+4x1"  # Complex with dialogue
    else:
        return "custom"


def calculate_grid_position(frame_number: int, format: str) -> Tuple[int, int]:
    """Calculate grid position (row, col) for frame number."""
    format_grids = {
        "4x1": (4, 1),
        "2x3": (2, 3),
        "3x3": (3, 3),
        "2x4": (2, 4),
        "4x4": (4, 4)
    }
    
    if format in format_grids:
        rows, cols = format_grids[format]
        row = (frame_number - 1) // cols
        col = (frame_number - 1) % cols
        return (row, col)
    
    return (0, 0)


def determine_face_visibility(character_distance: Optional[str]) -> str:
    """Determine if face is visible based on character distance."""
    if not character_distance:
        return "not_applicable"
    
    visibility_map = {
        "far": "not_visible",
        "medium_far": "barely_visible",
        "medium": "visible",
        "close": "clearly_visible",
        "extreme_close": "fills_frame"
    }
    
    return visibility_map.get(character_distance, "visible")


def analyze_shot_distance(shot_type: str, camera_angle: str) -> str:
    """Determine character distance based on shot type and camera angle."""
    if shot_type == "establishing" or camera_angle == "wide":
        return "far"
    elif camera_angle == "medium":
        return "medium"
    elif camera_angle == "close-up":
        return "close"
    elif camera_angle == "extreme_close-up":
        return "extreme_close"
    else:
        return "medium"


def classify_scene_type(scene_analysis: Any) -> str:
    """Classify scene type based on analysis."""
    dialogue_count = len(scene_analysis.dialogue_segments)
    action_count = len(scene_analysis.action_beats)
    
    if dialogue_count > action_count * 2:
        return "dialogue_heavy"
    elif action_count > dialogue_count * 2:
        return "action_heavy"
    elif dialogue_count > 0 and action_count > 0:
        return "dialogue_with_action"
    else:
        return "mixed"


# ===== IMAGE PROMPT GENERATION =====

def generate_character_image_prompt(character: Any) -> str:
    """
    Generate photorealistic portrait prompt for AI image generation.
    
    CRITICAL: Output must be 16:9 aspect ratio (1920x1080) for video production.
    
    Format: "Photorealistic portrait, [ethnicity] [gender] [age], 
    [face features], [hair], [eyes], [build], [distinctive marks], 
    [expression], neutral background, studio lighting, 16:9 aspect ratio, 8K quality"
    """
    prompt_parts = [
        "Photorealistic portrait",
        f"{character.ethnicity} {character.gender}" if character.ethnicity else character.gender,
        character.age,
        character.face_description,
        character.hair,
        character.eyes,
        character.build,
    ]
    
    if character.distinctive_marks:
        prompt_parts.append(character.distinctive_marks)
    
    prompt_parts.extend([
        character.typical_expression if character.typical_expression else "neutral expression",
        "neutral grey background",
        "soft studio lighting from 45 degrees",
        "16:9 aspect ratio",  # CRITICAL for video production
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
    
    return ", ".join(prompt_parts)


def generate_environment_image_prompt(environment: Any, name: str) -> str:
    """
    Generate anchor image prompt for empty environment.
    
    CRITICAL: Output must be 16:9 aspect ratio (1920x1080) for video production.
    
    Format: "Wide-angle photograph of [location], empty room,
    [permanent fixtures], [lighting], [atmosphere],
    elevated wide angle shot, 16:9 aspect ratio, 8K quality"
    """
    prompt_parts = [
        "Wide-angle architectural photograph of",
        name.lower(),
        "empty room",
    ]
    
    # Add permanent fixtures
    for furniture in environment.furniture_list:
        prompt_parts.append(furniture)
    
    for fixture in environment.fixtures_list:
        prompt_parts.append(fixture)
    
    # Add materials
    prompt_parts.extend([
        environment.walls,
        environment.floor,
        environment.ceiling
    ])
    
    # Add lighting
    prompt_parts.append(environment.default_lighting)
    prompt_parts.append(environment.atmosphere)
    
    # Critical modifiers
    prompt_parts.extend([
        "permanent fixtures only",
        "no people",
        "no temporary objects",
        "no props",
        f"elevated wide angle shot from {environment.camera_position}",
        "capturing entire space layout",
        "professional architectural photography",
        "clean cinematic composition",
        "16:9 aspect ratio",  # CRITICAL for video production
        "1920x1080 resolution",
        "widescreen cinematic frame",
        "NO letterboxing",
        "NO pillarboxing",
        "NO security camera UI",
        "NO overlays",
        "NO timestamps",
        "fills entire 16:9 rectangle",
        "8K quality",
        "architectural interior photography",
        "hyperrealistic"
    ])
    
    return ", ".join(prompt_parts)


# ===== VIDEO PLANNING HELPERS =====

def plan_video_clips(frames: List[Dict], total_duration: int) -> List[Dict]:
    """
    Break frames into 8-second video clips.
    
    Video AI limitation: 8 seconds max per generation.
    Group frames intelligently into clips.
    """
    clips = []
    current_clip_frames = []
    current_clip_duration = 0
    clip_number = 1
    
    for frame in frames:
        # Safely get frame duration
        video_clip_data = frame.get('video_clip', {})
        if isinstance(video_clip_data, dict):
            frame_duration = video_clip_data.get('duration', 3)  # Default 3 seconds
        else:
            frame_duration = 3  # Default fallback
        
        # If adding this frame exceeds 8 seconds, start new clip
        if current_clip_duration + frame_duration > 8 and current_clip_frames:
            clips.append({
                "clip_number": clip_number,
                "source_frames": [f.get('frame_number', i+1) for i, f in enumerate(current_clip_frames)],
                "duration": current_clip_duration,
                "audio": extract_audio_for_frames(current_clip_frames),
                "transition_to_next": "cut"
            })
            clip_number += 1
            current_clip_frames = []
            current_clip_duration = 0
        
        current_clip_frames.append(frame)
        current_clip_duration += frame_duration
    
    # Add final clip
    if current_clip_frames:
        clips.append({
            "clip_number": clip_number,
            "source_frames": [f.get('frame_number', i+1) for i, f in enumerate(current_clip_frames)],
            "duration": current_clip_duration,
            "audio": extract_audio_for_frames(current_clip_frames),
            "transition_to_next": "end"
        })
    
    return clips


def extract_audio_for_frames(frames: List[Dict]) -> Dict[str, Any]:
    """Extract audio information from frames (dialogue, sfx)."""
    audio = {
        "dialogue": [],
        "sfx": [],
        "ambient": []
    }
    
    for frame in frames:
        # Safely get dialogue
        dialogue_lines = frame.get('dialogue')
        if not dialogue_lines:
            continue
        
        # Handle both list and dict types
        if not isinstance(dialogue_lines, list):
            continue
            
        for line in dialogue_lines:
            if not line or not isinstance(line, dict):
                continue
            
            # Get text from various possible field names
            text = (
                line.get('line') or 
                line.get('line_text') or 
                line.get('text') or 
                ''
            )
            
            # Skip empty lines
            if not text:
                continue
            
            audio['dialogue'].append({
                'character': line.get('character', 'Unknown'),
                'text': text,
                'timestamp': line.get('timestamp', '0:00')
            })
    
    return audio


# ===== FORMATTING HELPERS =====

def format_action_beats(action_beats: List[Dict]) -> str:
    """Format action beats for LLM prompt."""
    formatted = []
    for i, beat in enumerate(action_beats, 1):
        formatted.append(f"Beat {i}: {beat['description']} ({beat['duration']}s)")
    return '\n'.join(formatted)


def format_dialogue(dialogue_segments: List[Dict]) -> str:
    """Format dialogue segments for LLM prompt."""
    formatted = []
    for seg in dialogue_segments:
        formatted.append(f"{seg['character']}: \"{seg['line']}\" [{seg['emotional_state']}]")
    return '\n'.join(formatted)


def format_dialogue_for_analysis(dialogue_list: List[Dict]) -> str:
    """Format dialogue with context for voice analysis."""
    formatted = []
    for d in dialogue_list:
        formatted.append(f"Scene: {d['scene_heading']}")
        formatted.append(f"Line: {d['line']}")
        formatted.append("")
    return '\n'.join(formatted)


def format_historical_context_for_prompt(timeline: Optional[List[Dict]], 
                                         figures: Optional[List[Dict]], 
                                         locations: Optional[List[Dict]]) -> str:
    """Format historical context for LLM prompts."""
    if not any([timeline, figures, locations]):
        return ""
    
    parts = ["HISTORICAL CONTEXT:"]
    
    if timeline:
        parts.append("\nTimeline:")
        for event in timeline[:5]:  # Top 5 events
            parts.append(f"- {event.get('date', '')}: {event.get('event', '')}")
    
    if figures:
        parts.append("\nKey Figures:")
        for fig in figures[:5]:
            parts.append(f"- {fig.get('name', '')}: {fig.get('role', '')}")
    
    if locations:
        parts.append("\nKey Locations:")
        for loc in locations[:5]:
            parts.append(f"- {loc.get('name', '')}: {loc.get('description', '')}")
    
    return '\n'.join(parts)


# ===== FILE I/O HELPERS =====

def save_json(data: Any, filepath: Path) -> Path:
    """Save data as JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath


def load_json(filepath: Path) -> Any:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ===== CHARACTER/ENVIRONMENT LOOKUP =====

def find_character_by_name(characters_db: List[Dict], character_name: str) -> Optional[Dict]:
    """Find character in database by name."""
    for char in characters_db:
        if char['name'] == character_name or char['full_name'] == character_name:
            return char
    return None


def find_environment_for_scene(environments_db: List[Dict], scene_heading: str) -> Optional[Dict]:
    """Find matching environment for scene heading."""
    # Extract location from heading
    match = re.match(SCENE_HEADING_PATTERN, scene_heading)
    if not match:
        return None
    
    location = match.group(2).strip()
    
    # Find matching environment
    for env in environments_db:
        if location.lower() in env['name'].lower() or env['name'].lower() in location.lower():
            return env
    
    return None


def find_characters_in_scene(characters_db: List[Dict], scene_number: int) -> List[Dict]:
    """Find all characters appearing in a scene."""
    characters_in_scene = []
    
    for char in characters_db:
        if scene_number in char.get('scenes_appeared', []):
            characters_in_scene.append(char)
    
    return characters_in_scene


def get_voice_reference(character: Dict, emotional_state: str) -> Optional[Dict]:
    """Get voice reference for character in specific emotional state."""
    voice_profile = character.get('voice_profile', {})
    
    if not voice_profile:
        return None
    
    emotional_variations = voice_profile.get('emotional_variations', {})
    
    return emotional_variations.get(emotional_state.lower(), 
                                    emotional_variations.get('calm', {}))


# ===== SEQUENCE ANALYSIS =====

def calculate_sequence_frames(action_duration: int, max_clip_duration: int = 8) -> Dict[str, Any]:
    """
    Calculate how many frames needed for continuous action.
    
    Args:
        action_duration: Duration of action in seconds
        max_clip_duration: Maximum video clip duration (default 8s)
    
    Returns:
        Dict with frame count, sequence types, and clip breakdown
    """
    import math
    
    if action_duration <= max_clip_duration:
        # Simple: START → END
        return {
            "total_frames": 2,
            "frame_types": ["start", "end"],
            "num_clips": 1,
            "clip_durations": [action_duration]
        }
    
    else:
        # Need middle frames
        num_clips = math.ceil(action_duration / max_clip_duration)
        num_frames = num_clips + 1  # N clips need N+1 frames
        
        frame_types = ["start"]
        for i in range(1, num_frames - 1):
            frame_types.append(f"middle")
        frame_types.append("end")
        
        # Calculate clip durations
        clip_duration = action_duration / num_clips
        clip_durations = [clip_duration] * num_clips
        
        return {
            "total_frames": num_frames,
            "frame_types": frame_types,
            "num_clips": num_clips,
            "clip_durations": clip_durations
        }


def identify_dialogue_sequences(frames: List[Dict]) -> List[List[int]]:
    """
    Identify consecutive dialogue frames that form sequences.
    
    Args:
        frames: List of frame dictionaries
    
    Returns:
        List of frame number lists, each representing a dialogue sequence
    """
    sequences = []
    current_sequence = []
    
    for i, frame in enumerate(frames):
        is_dialogue = (
            frame.get('has_dialogue', False) and 
            frame.get('camera_angle') in ['close-up', 'extreme_close-up', 'medium']
        )
        
        if is_dialogue:
            current_sequence.append(i)
        else:
            # Check if it's a reaction shot in dialogue context
            is_reaction = frame.get('shot_type') == 'reaction'
            prev_was_dialogue = current_sequence and frames[current_sequence[-1]].get('has_dialogue')
            
            if is_reaction and prev_was_dialogue:
                current_sequence.append(i)
            else:
                # End of dialogue sequence
                if len(current_sequence) >= 2:  # At least 2 frames
                    sequences.append(current_sequence)
                current_sequence = []
    
    # Add last sequence
    if len(current_sequence) >= 2:
        sequences.append(current_sequence)
    
    return sequences


def check_character_scale_consistency(frames: List[Dict], character_name: str) -> bool:
    """
    Check if a character appears at consistent scale across frames.
    
    Args:
        frames: List of frame dictionaries
        character_name: Character to check
    
    Returns:
        True if consistent scale, False if mixed scales
    """
    distances = []
    
    for frame in frames:
        if frame.get('character_visible') and frame.get('character_name') == character_name:
            distance = frame.get('character_distance')
            if distance:
                distances.append(distance)
    
    if not distances:
        return True  # No character, no issue
    
    # Check if all distances are in same category
    distance_categories = {
        'far': ['far'],
        'medium': ['medium_far', 'medium'],
        'close': ['close', 'extreme_close']
    }
    
    frame_categories = set()
    for dist in distances:
        for category, dist_list in distance_categories.items():
            if dist in dist_list:
                frame_categories.add(category)
                break
    
    # If more than one category, scales are inconsistent
    return len(frame_categories) <= 1


def determine_generation_strategy(frame: Dict, context: Dict) -> tuple:
    """
    Determine if frame should be generated individually or in composite.
    
    Args:
        frame: Frame dictionary
        context: Context dict with:
            - scene_type: Type of scene
            - previous_frames: List of previous frames
            - dialogue_sequence: If frame is in dialogue sequence
    
    Returns:
        Tuple of (strategy, reason)
        strategy: 'individual' or 'composite_grid'
        reason: Explanation string
    """
    
    # Rule 1: Dialogue close-ups ALWAYS individual
    if frame.get('has_dialogue') and frame.get('camera_angle') in ['close-up', 'extreme_close-up']:
        return ('individual', 'dialogue_closeup_facial_detail')
    
    # Rule 2: Extreme close-ups ALWAYS individual
    if frame.get('camera_angle') == 'extreme_close-up':
        return ('individual', 'extreme_closeup_detail_required')
    
    # Rule 3: Character close-up (any) ALWAYS individual
    if frame.get('character_visible') and frame.get('camera_angle') == 'close-up':
        return ('individual', 'character_closeup_consistency')
    
    # Rule 4: In dialogue sequence → Individual
    if context.get('dialogue_sequence'):
        return ('individual', 'part_of_dialogue_sequence')
    
    # Rule 5: Sequence continuity - if previous was individual, this should be too
    previous_frames = context.get('previous_frames', [])
    if previous_frames:
        prev_frame = previous_frames[-1]
        same_sequence = (
            prev_frame.get('sequence_id') == frame.get('sequence_id') and
            frame.get('sequence_id') is not None
        )
        
        if same_sequence and prev_frame.get('generation_strategy') == 'individual':
            return ('individual', 'sequence_continuity_with_previous')
    
    # Rule 6: Character at medium distance with visible face → Individual
    if (frame.get('character_visible') and 
        frame.get('character_distance') == 'medium' and
        frame.get('camera_angle') in ['medium', 'medium_close-up']):
        return ('individual', 'character_medium_shot_quality')
    
    # Rule 7: No character or character very far → Can composite
    if (not frame.get('character_visible') or 
        frame.get('character_distance') in ['far', 'medium_far']):
        return ('composite_grid', 'no_character_detail_needed')
    
    # Rule 8: Insert shots (props, no characters) → Can composite
    if frame.get('shot_type') == 'insert' and not frame.get('character_visible'):
        return ('composite_grid', 'insert_shot_no_character')
    
    # Rule 9: Wide establishing (no character focus) → Can composite
    if frame.get('camera_angle') == 'wide' and frame.get('character_distance') == 'far':
        return ('composite_grid', 'wide_establishing_shot')
    
    # Default: Individual for safety
    return ('individual', 'default_quality_priority')


def group_frames_for_composites(frames: List[Dict]) -> Dict[str, List[int]]:
    """
    Group frames that can safely be generated in same composite.
    
    Args:
        frames: List of frame dictionaries with generation_strategy set
    
    Returns:
        Dict mapping composite_group_id to list of frame indices
    """
    composite_frames = [
        (i, f) for i, f in enumerate(frames) 
        if f.get('generation_strategy') == 'composite_grid'
    ]
    
    if not composite_frames:
        return {}
    
    groups = {}
    current_group_id = None
    current_group = []
    
    for idx, frame in composite_frames:
        # Check if this frame can join current group
        if current_group:
            last_frame = frames[current_group[-1]]
            
            # Can group if:
            # 1. No character faces (both)
            # 2. OR same character at same distance
            # 3. AND same lighting/time
            
            can_group = can_group_frames_together(last_frame, frame, frames)
            
            if can_group:
                current_group.append(idx)
            else:
                # Save current group and start new one
                if current_group:
                    current_group_id = f"composite_{len(groups) + 1:03d}"
                    groups[current_group_id] = current_group
                current_group = [idx]
        else:
            current_group = [idx]
    
    # Save last group
    if current_group:
        current_group_id = f"composite_{len(groups) + 1:03d}"
        groups[current_group_id] = current_group
    
    return groups


def can_group_frames_together(frame1: Dict, frame2: Dict, all_frames: List[Dict]) -> bool:
    """
    Check if two frames can be in same composite grid.
    
    Args:
        frame1: First frame
        frame2: Second frame
        all_frames: All frames (for context)
    
    Returns:
        True if can group, False otherwise
    """
    
    # Both have no character → OK
    if not frame1.get('character_visible') and not frame2.get('character_visible'):
        return True
    
    # One has character, other doesn't → NO
    if frame1.get('character_visible') != frame2.get('character_visible'):
        return False
    
    # Both have characters
    char1 = frame1.get('character_name')
    char2 = frame2.get('character_name')
    
    # Different characters at different positions → Maybe OK if both far
    if char1 != char2:
        # Both must be far distance
        if (frame1.get('character_distance') == 'far' and 
            frame2.get('character_distance') == 'far'):
            return True
        return False
    
    # Same character
    # Must be at same distance
    if frame1.get('character_distance') != frame2.get('character_distance'):
        return False
    
    # Must have same camera angle category
    angle1_cat = categorize_camera_angle(frame1.get('camera_angle'))
    angle2_cat = categorize_camera_angle(frame2.get('camera_angle'))
    
    if angle1_cat != angle2_cat:
        return False
    
    # Check lighting/time consistency
    time1 = frame1.get('time_of_day', 'unknown')
    time2 = frame2.get('time_of_day', 'unknown')
    
    if time1 != time2:
        return False
    
    return True


def categorize_camera_angle(angle: str) -> str:
    """Categorize camera angles into groups."""
    if angle in ['wide']:
        return 'wide'
    elif angle in ['medium']:
        return 'medium'
    elif angle in ['close-up', 'extreme_close-up']:
        return 'close'
    else:
        return 'other'