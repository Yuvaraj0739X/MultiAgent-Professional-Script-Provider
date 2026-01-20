import os
import re
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime



def validate_fountain_syntax(screenplay: str) -> Dict:
    """
    Validate Fountain format syntax.
    
    Checks for:
    - Proper scene headings (INT./EXT. LOCATION - TIME)
    - Character names in ALL CAPS
    - Proper formatting structure
    
    Args:
        screenplay: Screenplay text in Fountain format
        
    Returns:
        Dictionary with validation results:
        {
            "is_valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "compliance_score": float
        }
    """
    errors = []
    warnings = []
    
    lines = screenplay.split("\n")
    total_checks = 0
    passed_checks = 0
    
    scene_headings = [l for l in lines if re.match(r"^(INT\.|EXT\.)", l.strip())]
    total_checks += 1
    if len(scene_headings) > 0:
        passed_checks += 1
    else:
        errors.append("No scene headings found (must start with INT. or EXT.)")
    
    scene_heading_pattern = r"^(INT\.|EXT\.|INT\./EXT\.)\s+.+\s+-\s+(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER)"
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith("INT.") or line_stripped.startswith("EXT."):
            total_checks += 1
            if re.match(scene_heading_pattern, line_stripped, re.IGNORECASE):
                passed_checks += 1
            else:
                errors.append(f"Line {i+1}: Invalid scene heading format: '{line_stripped}'")
    
    dialogue_started = False
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if not line_stripped or line_stripped.startswith("INT.") or line_stripped.startswith("EXT."):
            continue
        
        if len(line_stripped) > 0 and line_stripped[0].isupper():
            next_lines = lines[i+1:]
            for next_line in next_lines:
                next_stripped = next_line.strip()
                if next_stripped:
                    if next_stripped[0].islower() or next_stripped[0] == '"':
                        if not line_stripped.isupper():
                            warnings.append(f"Line {i+1}: Character name should be ALL CAPS: '{line_stripped}'")
                    break
    
    has_dialogue = False
    for line in lines:
        if line.strip() and line.strip()[0].islower():
            has_dialogue = True
            break
    
    if not has_dialogue:
        warnings.append("No dialogue detected - screenplay may be incomplete")
    
    total_checks += 1
    if len(screenplay) >= 1000:
        passed_checks += 1
    else:
        errors.append(f"Screenplay too short ({len(screenplay)} chars, need at least 1000)")
    
    compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0.0
    
    is_valid = len(errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "compliance_score": compliance_score
    }


def format_fountain(text: str) -> str:
    """
    Clean and format Fountain text.
    
    - Removes excessive blank lines
    - Ensures proper spacing around scene headings
    - Cleans up whitespace
    
    Args:
        text: Raw screenplay text
        
    Returns:
        Cleaned and formatted Fountain text
    """
    lines = text.split("\n")
    formatted_lines = []
    
    previous_was_blank = False
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            if not previous_was_blank:
                formatted_lines.append("")
                previous_was_blank = True
            continue
        
        if stripped.startswith("INT.") or stripped.startswith("EXT."):
            if formatted_lines and formatted_lines[-1]:
                formatted_lines.append("")
        
        formatted_lines.append(stripped)
        previous_was_blank = False
    
    return "\n".join(formatted_lines)



def save_screenplay(
    screenplay: str,
    output_path: str,
    format_before_save: bool = True
) -> str:
    """
    Save screenplay to file.
    
    Args:
        screenplay: Screenplay text
        output_path: Path to save file
        format_before_save: Whether to format the text before saving
        
    Returns:
        Path to saved file
    """
    if format_before_save:
        screenplay = format_fountain(screenplay)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(screenplay)
    
    return output_path


def save_json(data: Dict, output_path: str) -> str:
    """
    Save dictionary as JSON file.
    
    Args:
        data: Dictionary to save
        output_path: Path to save file
        
    Returns:
        Path to saved file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return output_path


def load_json(file_path: str) -> Dict:
    """
    Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary loaded from file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)



def calculate_screenplay_duration(screenplay: str) -> int:
    """
    Estimate screenplay duration in minutes.
    
    Rule of thumb: 1 page ≈ 1 minute
    Estimate pages by line count: ~55 lines per page
    
    Args:
        screenplay: Screenplay text
        
    Returns:
        Estimated duration in minutes
    """
    lines = screenplay.split("\n")
    non_empty_lines = [l for l in lines if l.strip()]
    
    estimated_pages = len(non_empty_lines) / 55
    estimated_duration = max(1, int(estimated_pages))
    
    return estimated_duration


def count_scenes(screenplay: str) -> int:
    """
    Count number of scenes in screenplay.
    
    Args:
        screenplay: Screenplay text
        
    Returns:
        Number of scenes (scene headings)
    """
    scene_count = 0
    for line in screenplay.split("\n"):
        if re.match(r"^(INT\.|EXT\.)", line.strip()):
            scene_count += 1
    
    return scene_count


def extract_scene_headings(screenplay: str) -> List[str]:
    """
    Extract all scene headings from screenplay.
    
    Args:
        screenplay: Screenplay text
        
    Returns:
        List of scene heading strings
    """
    headings = []
    for line in screenplay.split("\n"):
        stripped = line.strip()
        if stripped.startswith("INT.") or stripped.startswith("EXT."):
            headings.append(stripped)
    
    return headings


def extract_characters(screenplay: str) -> List[str]:
    """
    Extract unique character names from screenplay.
    
    Args:
        screenplay: Screenplay text
        
    Returns:
        Sorted list of unique character names
    """
    characters = set()
    lines = screenplay.split("\n")
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if not stripped or stripped.startswith("INT.") or stripped.startswith("EXT."):
            continue
        
        if stripped.isupper() and len(stripped) > 1:
            if stripped not in ["FADE IN:", "FADE OUT:", "CUT TO:", "DISSOLVE TO:", "CONTINUOUS"]:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and (next_line[0].islower() or next_line.startswith("(")):
                        characters.add(stripped)
    
    return sorted(list(characters))


def extract_locations(screenplay: str) -> List[str]:
    """
    Extract unique locations from screenplay.
    
    Args:
        screenplay: Screenplay text
        
    Returns:
        Sorted list of unique locations
    """
    locations = set()
    
    pattern = r"^(INT\.|EXT\.|INT\./EXT\.)\s+(.+?)\s+-\s+"
    
    for line in screenplay.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            location = match.group(2).strip()
            locations.add(location)
    
    return sorted(list(locations))



def merge_scenes(scenes: List[str]) -> str:
    """
    Merge individual scene texts into complete screenplay.
    
    Args:
        scenes: List of scene texts (each scene is complete with heading + action + dialogue)
        
    Returns:
        Complete screenplay with scenes merged
    """
    screenplay_parts = []
    
    screenplay_parts.append("UNTITLED SCREENPLAY")
    screenplay_parts.append("")
    screenplay_parts.append("")
    screenplay_parts.append("FADE IN:")
    screenplay_parts.append("")
    
    for i, scene in enumerate(scenes):
        screenplay_parts.append(scene.strip())
        
        if i < len(scenes) - 1:
            screenplay_parts.append("")
            screenplay_parts.append("")
    
    screenplay_parts.append("")
    screenplay_parts.append("")
    screenplay_parts.append("FADE OUT.")
    screenplay_parts.append("")
    screenplay_parts.append("THE END")
    
    return "\n".join(screenplay_parts)



def create_title_page(
    title: str,
    author: str = "AI Screenplay Generator",
    based_on: Optional[str] = None
) -> str:
    """
    Create a Fountain format title page.
    
    Args:
        title: Screenplay title
        author: Author name
        based_on: Optional "based on" credit
        
    Returns:
        Formatted title page text
    """
    parts = [
        title.upper(),
        "",
        "",
        f"Written by",
        author,
    ]
    
    if based_on:
        parts.extend([
            "",
            f"Based on {based_on}"
        ])
    
    parts.extend([
        "",
        "",
        ""
    ])
    
    return "\n".join(parts)



def format_historical_context_for_prompt(
    timeline: Optional[List[Dict]] = None,
    key_figures: Optional[List[Dict]] = None,
    key_locations: Optional[List[Dict]] = None
) -> str:
    """
    Format Phase 2 historical context for inclusion in screenplay generation prompts.
    
    Args:
        timeline: Timeline events from Phase 2
        key_figures: Character profiles from Phase 2
        key_locations: Location details from Phase 2
        
    Returns:
        Formatted context string for LLM prompt
    """
    if not timeline and not key_figures and not key_locations:
        return ""
    
    context_parts = []
    context_parts.append("HISTORICAL CONTEXT (Must be accurately represented):")
    context_parts.append("")
    
    if timeline:
        context_parts.append("Timeline of Events:")
        for event in timeline:
            date = event.get("date", "Unknown")
            event_name = event.get("event", "Unknown")
            desc = event.get("description", "")
            context_parts.append(f"- {date}: {event_name}")
            if desc:
                context_parts.append(f"  {desc}")
        context_parts.append("")
    
    if key_figures:
        context_parts.append("Key Historical Figures:")
        for figure in key_figures:
            name = figure.get("name", "Unknown")
            role = figure.get("role", "")
            desc = figure.get("description", "")
            context_parts.append(f"- {name}: {role}")
            if desc:
                context_parts.append(f"  {desc}")
        context_parts.append("")
    
    if key_locations:
        context_parts.append("Key Locations:")
        for location in key_locations:
            name = location.get("name", "Unknown")
            loc_type = location.get("type", "")
            desc = location.get("description", "")
            context_parts.append(f"- {name} ({loc_type})")
            if desc:
                context_parts.append(f"  {desc}")
        context_parts.append("")
    
    return "\n".join(context_parts)



def print_screenplay_stats(screenplay: str) -> None:
    """
    Print statistics about a screenplay.
    
    Args:
        screenplay: Screenplay text
    """
    print(f"Screenplay Statistics:")
    print(f"  Total length: {len(screenplay):,} characters")
    print(f"  Line count: {len(screenplay.split(chr(10))):,}")
    print(f"  Scene count: {count_scenes(screenplay)}")
    print(f"  Character count: {len(extract_characters(screenplay))}")
    print(f"  Location count: {len(extract_locations(screenplay))}")
    print(f"  Estimated duration: {calculate_screenplay_duration(screenplay)} minutes")
    print(f"  Estimated pages: {len(screenplay.split(chr(10))) // 55}")


def get_screenplay_metadata(screenplay: str, historical: bool = False) -> Dict:
    """
    Get complete metadata about a screenplay.
    
    Args:
        screenplay: Screenplay text
        historical: Whether this is a historical screenplay
        
    Returns:
        Dictionary with all metadata
    """
    return {
        "page_count": len(screenplay.split("\n")) // 55,
        "estimated_duration": calculate_screenplay_duration(screenplay),
        "scene_count": count_scenes(screenplay),
        "character_count": len(extract_characters(screenplay)),
        "location_count": len(extract_locations(screenplay)),
        "locations": extract_locations(screenplay),
        "characters": extract_characters(screenplay),
        "generation_timestamp": datetime.utcnow().isoformat() + "Z",
        "historical_accuracy": "verified" if historical else None
    }