"""
Phase 4: Generation Strategy Decision Logic
Determines whether frames should be generated individually or as composites
based on character consistency, dialogue requirements, and quality needs.

CRITICAL: This module ensures professional-quality character consistency
by making intelligent decisions about when to use composite grids vs individual generation.
"""

from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict


# ===== CHARACTER DISTANCE CONSTANTS =====

FACE_VISIBILITY = {
    "extreme_close": "fills_frame",      # Face fills entire frame (800+ pixels)
    "close": "clearly_visible",          # Face clear and detailed (400-800 pixels)
    "medium": "recognizable",            # Face visible and recognizable (200-400 pixels)
    "medium_far": "barely_recognizable", # Face barely visible (40-100 pixels)
    "far": "not_recognizable"           # Face tiny or not visible (0-40 pixels)
}

# Distances that require individual generation for quality
HIGH_QUALITY_DISTANCES = ["extreme_close", "close", "medium"]

# Distances safe for composite (characters too far for detail to matter)
COMPOSITE_SAFE_DISTANCES = ["far", "medium_far"]


# ===== GENERATION STRATEGIES =====

class GenerationStrategy:
    """Generation strategy types."""
    INDIVIDUAL = "individual"
    COMPOSITE = "composite_grid"
    HYBRID = "hybrid"  # Scene uses both


# ===== CORE DECISION FUNCTIONS =====

def is_dialogue_frame(frame: Dict) -> bool:
    """
    Check if frame is a dialogue frame requiring high facial detail.
    """
    return (
        frame.get('has_dialogue', False) and
        frame.get('camera_angle') in ['close-up', 'extreme_close-up', 'medium']
    )


def is_extreme_closeup(frame: Dict) -> bool:
    """
    Check if frame is extreme close-up requiring maximum detail.
    """
    return (
        frame.get('camera_angle') == 'extreme_close-up' or
        frame.get('shot_type') in ['insert', 'extreme_close-up'] or
        frame.get('character_distance') == 'extreme_close'
    )


def requires_facial_detail(frame: Dict) -> bool:
    """
    Check if frame requires detailed facial rendering.
    """
    if not frame.get('character_visible', False):
        return False
    
    # Dialogue always needs facial detail
    if is_dialogue_frame(frame):
        return True
    
    # Extreme close-ups always need detail
    if is_extreme_closeup(frame):
        return True
    
    # Close shots of characters need detail
    if frame.get('character_distance') in HIGH_QUALITY_DISTANCES:
        return True
    
    # Reaction shots need facial detail
    if frame.get('shot_type') == 'reaction':
        return True
    
    return False


def get_character_scale_in_frame(frame: Dict) -> Optional[str]:
    """
    Determine the scale/size of character in frame.
    Returns: "tiny", "small", "medium", "large", "very_large"
    """
    distance = frame.get('character_distance')
    
    if not distance:
        return None
    
    scale_map = {
        "far": "tiny",              # 10-40 pixels
        "medium_far": "small",      # 40-100 pixels
        "medium": "medium",         # 200-400 pixels
        "close": "large",           # 400-800 pixels
        "extreme_close": "very_large"  # 800+ pixels
    }
    
    return scale_map.get(distance)


def has_mixed_character_scales(frames: List[Dict], character_name: str) -> bool:
    """
    Check if the same character appears at significantly different scales.
    
    Mixed scales in same composite = consistency problems!
    """
    character_frames = []
    for f in frames:
        char_present = f.get('character_present') or {}
        if isinstance(char_present, dict) and char_present.get('character_name') == character_name:
            character_frames.append(f)
    
    if len(character_frames) <= 1:
        return False
    
    scales = set()
    for frame in character_frames:
        scale = get_character_scale_in_frame(frame)
        if scale:
            scales.add(scale)
    
    # If character appears at more than 2 different scales, it's mixed
    # Example: "tiny" and "very_large" in same composite = BAD
    if len(scales) > 2:
        return True
    
    # If scales include both extremes, it's mixed
    if "tiny" in scales and "very_large" in scales:
        return True
    
    if "small" in scales and "large" in scales:
        return True
    
    return False


# ===== DIALOGUE SEQUENCE DETECTION =====

def identify_dialogue_sequences(frames: List[Dict]) -> List[List[int]]:
    """
    Identify consecutive dialogue frames that form a sequence.
    
    Returns: List of frame number lists
    Example: [[4, 5, 6, 7, 8], [11, 12, 13, 14]]
    """
    sequences = []
    current_sequence = []
    
    for frame in frames:
        frame_num = frame['frame_number']
        
        # Check if this is a dialogue frame
        if is_dialogue_frame(frame):
            current_sequence.append(frame_num)
        
        # Check if this is a reaction shot (part of dialogue)
        elif (frame.get('shot_type') == 'reaction' and 
              current_sequence and
              frame.get('character_visible')):
            current_sequence.append(frame_num)
        
        # Break sequence
        else:
            if len(current_sequence) >= 2:  # Minimum 2 frames for sequence
                sequences.append(current_sequence)
            current_sequence = []
    
    # Add last sequence
    if len(current_sequence) >= 2:
        sequences.append(current_sequence)
    
    return sequences


# ===== SEQUENCE CONTINUITY =====

def get_action_sequences(frames: List[Dict]) -> Dict[str, List[int]]:
    """
    Group frames by sequence_id (START→MIDDLE→END actions).
    
    Returns: Dict mapping sequence_id to list of frame numbers
    """
    sequences = defaultdict(list)
    
    for frame in frames:
        seq_id = frame.get('sequence_id')
        if seq_id:
            sequences[seq_id].append(frame['frame_number'])
    
    return dict(sequences)


def requires_sequence_continuity(frames: List[Dict], frame_idx: int) -> bool:
    """
    Check if frame must use same strategy as previous frame for continuity.
    """
    if frame_idx == 0:
        return False
    
    current_frame = frames[frame_idx]
    previous_frame = frames[frame_idx - 1]
    
    # Same sequence ID = must maintain continuity
    if (current_frame.get('sequence_id') and 
        current_frame.get('sequence_id') == previous_frame.get('sequence_id')):
        return True
    
    return False


# ===== COMPOSITE GROUPING VALIDATION =====

def can_group_in_composite(frames: List[Dict]) -> Tuple[bool, str]:
    """
    Determine if frames can be safely grouped in a composite grid.
    
    Returns: (can_group: bool, reason: str)
    """
    
    # Rule 1: No dialogue close-ups in composites
    dialogue_frames = [f for f in frames if is_dialogue_frame(f)]
    if dialogue_frames:
        return False, "Contains dialogue close-ups requiring individual generation"
    
    # Rule 2: No extreme close-ups in composites
    extreme_frames = [f for f in frames if is_extreme_closeup(f)]
    if extreme_frames:
        return False, "Contains extreme close-ups requiring individual generation"
    
    # Rule 3: Check for mixed character scales
    characters = set()
    for frame in frames:
        char_present = frame.get('character_present')
        if char_present and isinstance(char_present, dict):
            char_name = char_present.get('character_name')
            if char_name:
                characters.add(char_name)
    
    for character in characters:
        if has_mixed_character_scales(frames, character):
            return False, f"Character {character} appears at mixed scales"
    
    # Rule 4: All frames should have similar context
    contexts = set()
    for frame in frames:
        # Create context signature
        context = (
            frame.get('shot_type'),
            frame.get('camera_angle'),
            frame.get('character_distance')
        )
        contexts.add(context)
    
    # If too many different contexts, don't composite
    if len(contexts) > len(frames) * 0.7:  # More than 70% unique contexts
        return False, "Too many different shot contexts"
    
    # Rule 5: Check lighting consistency
    lightings = set()
    for frame in frames:
        lighting = frame.get('environment', {}).get('specific_lighting', 'unknown')
        lightings.add(lighting)
    
    if len(lightings) > 1:
        return False, "Inconsistent lighting across frames"
    
    return True, "Safe to composite"


# ===== MAIN DECISION LOGIC =====

def determine_frame_generation_strategy(
    frames: List[Dict],
    dialogue_sequences: List[List[int]],
    action_sequences: Dict[str, List[int]]
) -> Dict[int, Dict]:
    """
    Determine generation strategy for each frame.
    
    Returns: Dict mapping frame_number to strategy info
    {
        frame_number: {
            'strategy': 'individual' or 'composite_grid',
            'reason': 'explanation',
            'composite_group_id': 'group_001' (if composite),
            'priority': 'high' or 'normal'
        }
    }
    """
    strategies = {}
    
    # Step 1: Mark all dialogue sequences as INDIVIDUAL
    dialogue_frame_nums = set()
    for seq in dialogue_sequences:
        for frame_num in seq:
            dialogue_frame_nums.add(frame_num)
    
    for frame_num in dialogue_frame_nums:
        strategies[frame_num] = {
            'strategy': GenerationStrategy.INDIVIDUAL,
            'reason': 'Part of dialogue sequence requiring facial detail',
            'priority': 'high'
        }
    
    # Step 2: Mark all extreme close-ups as INDIVIDUAL
    for frame in frames:
        frame_num = frame['frame_number']
        if frame_num in strategies:
            continue
        
        if is_extreme_closeup(frame):
            strategies[frame_num] = {
                'strategy': GenerationStrategy.INDIVIDUAL,
                'reason': 'Extreme close-up requiring maximum detail',
                'priority': 'high'
            }
    
    # Step 3: Check action sequences for continuity
    for seq_id, frame_nums in action_sequences.items():
        # If any frame in sequence is already individual, all must be
        has_individual = any(
            strategies.get(num, {}).get('strategy') == GenerationStrategy.INDIVIDUAL
            for num in frame_nums
        )
        
        if has_individual:
            for frame_num in frame_nums:
                if frame_num not in strategies:
                    strategies[frame_num] = {
                        'strategy': GenerationStrategy.INDIVIDUAL,
                        'reason': f'Sequence continuity with individual frames (seq {seq_id})',
                        'priority': 'normal'
                    }
    
    # Step 4: Mark frames requiring facial detail as INDIVIDUAL
    for frame in frames:
        frame_num = frame['frame_number']
        if frame_num in strategies:
            continue
        
        if requires_facial_detail(frame):
            strategies[frame_num] = {
                'strategy': GenerationStrategy.INDIVIDUAL,
                'reason': 'Requires facial detail for character consistency',
                'priority': 'normal'
            }
    
    # Step 5: Remaining frames can potentially be composite
    for frame in frames:
        frame_num = frame['frame_number']
        if frame_num not in strategies:
            strategies[frame_num] = {
                'strategy': GenerationStrategy.COMPOSITE,
                'reason': 'Wide/far shot suitable for composite generation',
                'priority': 'normal'
            }
    
    return strategies


def group_composite_frames(frames: List[Dict], strategies: Dict) -> Dict[str, List[int]]:
    """
    Group frames marked as composite into actual composite grids.
    
    Returns: Dict mapping composite_group_id to list of frame numbers
    """
    # Get all composite frames
    composite_frames = [
        f for f in frames 
        if strategies.get(f['frame_number'], {}).get('strategy') == GenerationStrategy.COMPOSITE
    ]
    
    if not composite_frames:
        return {}
    
    groups = {}
    group_id_counter = 1
    current_group = []
    
    for frame in composite_frames:
        current_group.append(frame)
        
        # Check if current group can be composited
        if len(current_group) >= 9:  # Max 3×3 grid
            can_group, reason = can_group_in_composite(current_group)
            
            if can_group:
                group_id = f"composite_{group_id_counter:03d}"
                groups[group_id] = [f['frame_number'] for f in current_group]
                group_id_counter += 1
                current_group = []
            else:
                # Can't group - try smaller group
                if len(current_group) > 4:
                    # Try first 4
                    can_group_4, _ = can_group_in_composite(current_group[:4])
                    if can_group_4:
                        group_id = f"composite_{group_id_counter:03d}"
                        groups[group_id] = [f['frame_number'] for f in current_group[:4]]
                        group_id_counter += 1
                        current_group = current_group[4:]
                    else:
                        # Can't group, mark as individual
                        for f in current_group:
                            strategies[f['frame_number']]['strategy'] = GenerationStrategy.INDIVIDUAL
                            strategies[f['frame_number']]['reason'] = "Cannot group safely in composite"
                        current_group = []
    
    # Handle remaining frames
    if current_group:
        can_group, reason = can_group_in_composite(current_group)
        if can_group and len(current_group) >= 2:
            group_id = f"composite_{group_id_counter:03d}"
            groups[group_id] = [f['frame_number'] for f in current_group]
        else:
            # Mark as individual
            for f in current_group:
                strategies[f['frame_number']]['strategy'] = GenerationStrategy.INDIVIDUAL
                strategies[f['frame_number']]['reason'] = "Remaining frames, generate individually"
    
    return groups


def calculate_generation_costs(strategies: Dict, composite_groups: Dict) -> Dict:
    """
    Calculate API call costs for generation strategy.
    """
    individual_count = sum(
        1 for s in strategies.values() 
        if s['strategy'] == GenerationStrategy.INDIVIDUAL
    )
    
    composite_count = len(composite_groups)
    
    total_api_calls = individual_count + composite_count
    
    # Cost per call (approximate)
    cost_per_call = 0.04  # $0.04 for DALL-E 3
    
    return {
        'individual_frames': individual_count,
        'composite_grids': composite_count,
        'total_api_calls': total_api_calls,
        'estimated_cost': total_api_calls * cost_per_call,
        'frames_in_composites': sum(len(frames) for frames in composite_groups.values()),
        'cost_per_frame': (total_api_calls * cost_per_call) / len(strategies) if strategies else 0
    }


# ===== MAIN ENTRY POINT =====

def analyze_scene_generation_strategy(scene: Dict) -> Dict:
    """
    Complete analysis of scene to determine generation strategy.
    
    Args:
        scene: Scene dict with frames and metadata
    
    Returns:
        Dict with:
        - frame_strategies: Strategy per frame
        - composite_groups: Groupings for composite generation
        - statistics: Cost and quality metrics
        - recommendations: Generation guidance
    """
    frames = scene.get('storyboard', {}).get('frames', [])
    
    if not frames:
        return {
            'frame_strategies': {},
            'composite_groups': {},
            'statistics': {},
            'recommendations': []
        }
    
    # Step 1: Identify sequences
    dialogue_sequences = identify_dialogue_sequences(frames)
    action_sequences = get_action_sequences(frames)
    
    # Step 2: Determine strategy per frame
    strategies = determine_frame_generation_strategy(
        frames,
        dialogue_sequences,
        action_sequences
    )
    
    # Step 3: Group composite frames
    composite_groups = group_composite_frames(frames, strategies)
    
    # Step 4: Calculate costs
    statistics = calculate_generation_costs(strategies, composite_groups)
    
    # Step 5: Add composite group IDs to strategies
    for group_id, frame_nums in composite_groups.items():
        for frame_num in frame_nums:
            if frame_num in strategies:
                strategies[frame_num]['composite_group_id'] = group_id
    
    # Step 6: Generate recommendations
    recommendations = []
    
    if statistics['individual_frames'] > len(frames) * 0.8:
        recommendations.append(
            "Scene is mostly individual frames (dialogue/close-ups). "
            "Consider if some frames can be simplified to reduce cost."
        )
    
    if statistics['composite_grids'] == 0:
        recommendations.append(
            "No composite grids possible. All frames require individual generation "
            "for character consistency and quality."
        )
    
    if len(dialogue_sequences) > 3:
        recommendations.append(
            f"Scene has {len(dialogue_sequences)} dialogue sequences. "
            "Ensure character reference images are high quality for consistency."
        )
    
    return {
        'frame_strategies': strategies,
        'composite_groups': composite_groups,
        'dialogue_sequences': dialogue_sequences,
        'action_sequences': action_sequences,
        'statistics': statistics,
        'recommendations': recommendations
    }
