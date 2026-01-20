"""
Phase 4 - Node 5: Storyboard Planning
The most complex node - creates intelligent frame-by-frame storyboard plans
with adaptive frame counts, camera angles, and video generation specifications.
"""

from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..state import Phase4State
from ..models import StoryboardPlan
from ..utils import (
    calculate_optimal_frame_count,
    determine_storyboard_format,
    calculate_grid_position,
    determine_face_visibility,
    find_character_by_name,
    get_voice_reference,
    plan_video_clips,
    format_action_beats,
    format_dialogue,
    identify_dialogue_sequences,
    calculate_sequence_frames
)
from ..generation_strategy import (
    analyze_scene_generation_strategy,
    GenerationStrategy
)

# Import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import get_llm_config


def storyboard_planning_node(state: Phase4State) -> Dict:
    """
    Plan storyboard frames for each scene.
    
    This is the most complex node. It makes intelligent decisions about:
    - How many frames per scene (based on complexity)
    - What format (3x3, 4x1, custom)
    - What camera angle per frame
    - Which frames need start+end (for 8-sec video generation)
    - How to chunk into video clips
    - Character positioning and poses
    
    Process:
    1. For each scene
    2. Analyze complexity, duration, action beats
    3. Determine optimal frame count
    4. Select storyboard format
    5. Map action beats to frames
    6. Assign camera angles intelligently
    7. Plan start+end frames for actions
    8. Break into 8-second video clips
    9. Add character pose notes
    10. Link dialogue to frames
    
    Uses:
    - Model: gpt-4o
    - Temperature: 0.5 (creative but structured)
    - Structured output: StoryboardPlan per scene
    
    Returns:
        Dict updating 'scenes' with storyboard plans
    """
    
    print("=" * 80)
    print("NODE 5: STORYBOARD PLANNING")
    print("=" * 80)
    
    scenes = state['scenes']
    characters_db = state['characters_database']
    environments_db = state['environments_database']
    
    print(f"Planning storyboards for {len(scenes)} scenes...")
    print("This is the most complex node - may take a few minutes...\n")
    
    llm = ChatOpenAI(**get_llm_config("phase4", "storyboard_planning"))
    
    updated_scenes = []
    scenes_with_storyboards = 0  # Initialize counter
    total_frames_planned = 0
    total_video_clips = 0
    
    for idx, scene in enumerate(scenes, 1):
        scene_number = scene['scene_number']
        scene_heading = scene['scene_heading']
        
        print(f"[{idx}/{len(scenes)}] Scene {scene_number}: {scene_heading}")
        
        # Determine frame count based on scene complexity
        frame_count = calculate_optimal_frame_count(scene)
        print(f"  ✓ Calculated optimal frames: {frame_count}")
        
        # Determine storyboard format
        storyboard_format = determine_storyboard_format(
            scene['complexity'],
            scene['duration_estimate'],
            scene['scene_type'],
            frame_count
        )
        print(f"  ✓ Selected format: {storyboard_format}")
        
        planning_prompt = f"""
Create comprehensive storyboard plan for Scene {scene['scene_number']}.

SCENE INFO:
- Heading: {scene['scene_heading']}
- Duration: {scene['duration_estimate']} seconds
- Complexity: {scene['complexity']}
- Type: {scene['scene_type']}
- Required frames: {frame_count}
- Format: {storyboard_format}

ACTION BEATS:
{format_action_beats(scene['action_beats'])}

DIALOGUE:
{format_dialogue(scene['dialogue_segments'])}

ENVIRONMENT: {scene['environment']['name']}
CHARACTERS: {[c['name'] for c in scene['characters_present']]}
PROPS: {[p['name'] for p in scene['props']]}

🎬 CRITICAL REQUIREMENT: ALL FRAMES MUST BE 16:9 ASPECT RATIO (1920x1080)
Every single frame will be generated as a 16:9 widescreen image for video production.
Frame composition must fill the entire 16:9 rectangle - NO letterboxing, NO pillarboxing.
Think widescreen cinematic format for EVERY shot.

TASK: Create exactly {frame_count} storyboard frames in {storyboard_format} format.

For each frame (Frame 1 through Frame {frame_count}), specify:

1. SHOT TYPE (choose one):
   - "establishing": Wide shot showing entire location (usually Frame 1)
   - "character_intro": First appearance of character in scene
   - "action": Physical movement or activity
   - "dialogue": Character speaking (use for dialogue)
   - "reaction": Character reacting/listening
   - "insert": Close-up of object/prop (for important props)
   - "transition": Moving between states
   - "ending": Final frame of scene

2. CAMERA ANGLE (choose one):
   - "wide": Entire room/location visible, all characters in frame
   - "medium": Waist-up, or multiple people
   - "close-up": Head and shoulders, face clear
   - "extreme_close-up": Face details or object details
   - "over-shoulder": Over one person's shoulder looking at another
   - "insert": Prop/object detail shot

3. CAMERA MOVEMENT (choose one):
   - "static": No camera movement
   - "slow_push_in": Gradual zoom/move closer
   - "slow_pull_out": Gradual zoom/move away
   - "pan_left": Horizontal sweep left
   - "pan_right": Horizontal sweep right
   - "tilt_up": Vertical sweep up
   - "tilt_down": Vertical sweep down
   - "handheld": Slight shake for urgency/realism

4. CHARACTER DISTANCE (if character visible):
   - "far": 20+ feet away (face not clearly visible in 3x3 format - avoid in 3x3!)
   - "medium_far": 10-20 feet (face barely visible)
   - "medium": 5-10 feet (face visible and clear)
   - "close": 2-4 feet (face fills good portion of frame)
   - "extreme_close": 0-2 feet (face fills entire frame)

5. FRAME DESCRIPTION:
   - Detailed description of what's in this frame
   - What's happening
   - Visual composition
   - Mood/atmosphere

6. FOCUS ELEMENTS:
   - List what the viewer's attention should be on
   - Examples: ["character face", "phone ringing", "door opening"]

7. ACTION BEAT REFERENCE:
   - Which action beat number this frame represents (1, 2, 3, etc.)

8. CHARACTER DETAILS (if visible):
   - character_visible: true/false
   - character_name: Name of character
   - character_pose: Specific body position (e.g., "lying on bed", "standing", "reaching")
   - facial_expression: Expression (e.g., "confused", "determined", "tired")
   - body_language: Body language notes (e.g., "tense posture", "relaxed")

9. SEQUENCE TYPE (for continuous actions):
   - sequence_type: "standalone", "start", "middle", or "end"
   - Use "standalone" for single frames (static moments, inserts)
   - Use "start"/"middle"/"end" for continuous actions longer than 8 seconds
   - Examples:
     * Simple action (≤8s): Frame N (start) → Frame N+1 (end)
     * Medium action (8-16s): Frame N (start) → Frame N+1 (middle) → Frame N+2 (end)
     * Long action (16-24s): Frame N (start) → Frame N+1 (middle) → Frame N+2 (middle) → Frame N+3 (end)
   - sequence_position: Position in sequence (1, 2, 3, etc.)
   - sequence_total: Total frames in this sequence
   - If "start", provide start_frame_details
   - If "end", provide end_frame_details  
   - If "middle", provide both (interpolation points)

10. START + END FRAME SYSTEM (for actions with state change):
   - has_end_frame: true if this is a START frame that needs END frame
   - Use for: reaching→grasping, sitting→standing, walking, turning
   - Max 8 seconds between start and end
   - start_frame_details:
     * character_position: Starting position
     * character_pose: Starting pose
     * description: What's happening at start
   - end_frame_details:
     * character_position: Ending position  
     * character_pose: Ending pose
     * description: What's happening at end
     * state_change: What changed from start to end

11. DIALOGUE (if present):
    - has_dialogue: true/false
    - If true, list dialogue_lines:
      * character: Who speaks
      * line_text: The dialogue
      * timestamp: When in the scene
      * delivery_notes: How to deliver
      * emotional_state: Emotion

12. VIDEO GENERATION:
    - estimated_duration: Seconds for this frame/moment
    - video_type: "static" (no movement), "animated" (subtle motion), "interpolated" (start→end)
    - video_generation_note: Technical notes for video generation

13. COMPOSITION AND IMAGE NOTES:
    - composition_notes: Visual composition, framing, what's in focus
      * REMEMBER: 16:9 widescreen format - use horizontal space effectively
      * Wide shots: Make use of full widescreen width
      * Close-ups: Position subject appropriately in 16:9 frame (rule of thirds)
      * Consider left/right composition for dialogue scenes
    - image_generation_note: Specific notes for AI image generation
      * MUST include: "16:9 aspect ratio, 1920x1080, widescreen cinematic frame"
      * Describe exact framing within 16:9 rectangle
      * NO vertical/portrait orientations - ONLY horizontal 16:9

CRITICAL RULES:
- Frame 1 MUST be establishing shot (wide angle showing location)
- Last frame should be ending/transition moment
- Dialogue frames: use "close-up" or "medium" angle for clear faces
- Action frames: use "medium" or "wide" to show movement
- Insert shots: use "extreme_close-up" for props
- If character is "far" in wide shot, follow with closer shot
- 3x3 format: AVOID far character distances (faces too small)
- 4x1 format: Good for dialogue scenes (all close-ups possible)
- Distribute frames evenly across action beats
- Important moments get more frames
- Each frame should advance the story
- Consider visual variety - don't repeat same angles
- ALL FRAMES ARE 16:9 WIDESCREEN - compose accordingly

FRAME DISTRIBUTION GUIDANCE:
- {frame_count} frames for {len(scene['action_beats'])} action beats
- Roughly {frame_count // len(scene['action_beats']) if scene['action_beats'] else 1} frames per beat
- Give more frames to complex/important beats
- Give fewer frames to simple transitions

Return exactly {frame_count} frames.
"""
        
        print(f"  🤖 Planning {frame_count} frames...")
        structured_llm = llm.with_structured_output(StoryboardPlan, method="function_calling")
        
        try:
            storyboard_plan = structured_llm.invoke(planning_prompt)
            
            print(f"  ✓ Storyboard plan created with {len(storyboard_plan.frames)} frames")
            
            # Post-process: add IDs, enhance notes, link to data
            frames = []
            
            # First pass: Create frame data with sequence information
            sequence_counter = 0
            current_sequence_id = None
            
            for frame_idx, frame in enumerate(storyboard_plan.frames, 1):
                # Determine sequence information
                if frame.sequence_type == "start":
                    sequence_counter += 1
                    current_sequence_id = f"seq_{sequence_counter:03d}"
                
                frame_data = {
                    "frame_number": frame_idx,
                    "grid_position": calculate_grid_position(frame_idx, storyboard_format),
                    "size": "standard",
                    
                    # CRITICAL: 16:9 aspect ratio for video production
                    "aspect_ratio": "16:9",
                    "resolution": "1920x1080",
                    "widescreen": True,
                    
                    "shot_type": frame.shot_type,
                    "camera_angle": frame.camera_angle,
                    "camera_movement": frame.camera_movement,
                    "character_distance": frame.character_distance,
                    "face_visibility": determine_face_visibility(frame.character_distance),
                    "description": frame.description,
                    "focus_elements": frame.focus_elements,
                    "action_beat_ref": frame.action_beat_number,
                    
                    # Sequence metadata
                    "sequence_type": frame.sequence_type,
                    "sequence_id": current_sequence_id if frame.sequence_type != "standalone" else None,
                    "sequence_position": frame.sequence_position,
                    "sequence_total": frame.sequence_total,
                    
                    "character_present": None,
                    "has_end_frame": frame.has_end_frame,
                    "start_frame": frame.start_frame_details.dict() if frame.start_frame_details else None,
                    "end_frame": frame.end_frame_details.dict() if frame.end_frame_details else None,
                    
                    "has_dialogue": frame.has_dialogue,
                    
                    "video_clip": {
                        "duration": frame.estimated_duration,
                        "type": frame.video_type,
                        "has_end_frame": frame.has_end_frame,
                        "generation_note": frame.video_generation_note
                    },
                    
                    "composition": frame.composition_notes,
                    "image_generation_note": frame.image_generation_note,
                    
                    # Time of day (for lighting consistency checks)
                    "time_of_day": scene.get('time_of_day', 'unknown')
                }
                
                # Add interpolation link if in sequence
                if frame.sequence_type in ['start', 'middle'] and frame_idx < len(storyboard_plan.frames):
                    frame_data["video_clip"]["interpolate_to_frame"] = frame_idx + 1
                
                # Add character info if present
                if frame.character_visible and frame.character_name:
                    character = find_character_by_name(characters_db, frame.character_name)
                    
                    if character:
                        frame_data["character_present"] = {
                            "character_id": character['character_id'],
                            "character_name": character['name'],
                            "costume_ref": character['costumes_by_scene'].get(str(scene_number)),
                            "pose": frame.character_pose,
                            "facial_expression": frame.facial_expression,
                            "body_language": frame.body_language
                        }
                        frame_data["character_visible"] = True
                        frame_data["character_name"] = character['name']
                    else:
                        frame_data["character_visible"] = False
                else:
                    frame_data["character_visible"] = False
                
                # Add dialogue if present
                if frame.has_dialogue and frame.dialogue_lines:
                    frame_data["dialogue"] = []
                    
                    for dialogue in frame.dialogue_lines:
                        # Skip if dialogue is None or invalid
                        if not dialogue:
                            continue
                        
                        character = find_character_by_name(characters_db, dialogue.character)
                        voice_ref = None
                        
                        if character and character.get('voice_profile'):
                            voice_ref = get_voice_reference(character, dialogue.emotional_state)
                        
                        # Safely get dialogue text (handle both line_text and text fields)
                        line_text = getattr(dialogue, 'line_text', None) or getattr(dialogue, 'text', '')
                        
                        frame_data["dialogue"].append({
                            "character": dialogue.character if hasattr(dialogue, 'character') else "Unknown",
                            "line": line_text,
                            "timestamp": getattr(dialogue, 'timestamp', '0:00'),
                            "delivery": getattr(dialogue, 'delivery_notes', ''),
                            "emotional_state": getattr(dialogue, 'emotional_state', 'neutral'),
                            "voice_reference": voice_ref
                        })
                
                frames.append(frame_data)
            
            print(f"  ✓ Created {len(frames)} frames")
            
            # COMPREHENSIVE GENERATION STRATEGY ANALYSIS
            print(f"\n  🎯 Analyzing generation strategy (character consistency)...")
            
            # Create scene dict for analysis
            scene_for_analysis = {
                'scene_number': scene_number,
                'scene_type': scene['scene_type'],
                'storyboard': {'frames': frames}
            }
            
            # Run complete analysis
            strategy_analysis = analyze_scene_generation_strategy(scene_for_analysis)
            
            # Apply strategies to frames
            frame_strategies = strategy_analysis['frame_strategies']
            composite_groups = strategy_analysis['composite_groups']
            statistics = strategy_analysis['statistics']
            
            for frame in frames:
                frame_num = frame['frame_number']
                if frame_num in frame_strategies:
                    strategy_info = frame_strategies[frame_num]
                    frame['generation_strategy'] = strategy_info['strategy']
                    frame['generation_reason'] = strategy_info['reason']
                    frame['composite_group_id'] = strategy_info.get('composite_group_id')
            
            # Display results
            print(f"\n  ✅ Generation Strategy Results:")
            print(f"    • Individual frames: {statistics['individual_frames']}")
            print(f"    • Composite grids: {statistics['composite_grids']}")
            print(f"    • Frames in composites: {statistics['frames_in_composites']}")
            print(f"    • Total API calls: {statistics['total_api_calls']}")
            print(f"    • Estimated cost: ${statistics['estimated_cost']:.2f}")
            print(f"    • Cost per frame: ${statistics['cost_per_frame']:.3f}")
            
            # Show dialogue sequences
            if strategy_analysis['dialogue_sequences']:
                print(f"\n  💬 Dialogue Sequences (all individual):")
                for i, seq in enumerate(strategy_analysis['dialogue_sequences'], 1):
                    print(f"    • Sequence {i}: Frames {seq}")
            
            # Show composite groups
            if composite_groups:
                print(f"\n  📦 Composite Groups:")
                for group_id, frame_nums in composite_groups.items():
                    print(f"    • {group_id}: Frames {frame_nums}")
            
            # Show recommendations
            if strategy_analysis['recommendations']:
                print(f"\n  💡 Recommendations:")
                for rec in strategy_analysis['recommendations']:
                    print(f"    - {rec}")
            
            # Plan video clips (8-second chunks) with error handling
            try:
                video_clips = plan_video_clips(frames, scene['duration_estimate'])
                print(f"  ✓ Video assembly: {len(video_clips)} clips")
            except Exception as e:
                print(f"  ⚠️ Video clips planning skipped: {e}")
                video_clips = []  # Empty clips list as fallback
            
            # Add storyboard to scene
            scene['storyboard'] = {
                "format": storyboard_format,
                "total_frames": frame_count,
                "layout_reason": storyboard_plan.format_reasoning if hasattr(storyboard_plan, 'format_reasoning') else "Auto-selected based on frame count",
                "frames": frames,
                "video_assembly": {
                    "total_clips": len(video_clips),
                    "total_runtime": scene['duration_estimate'],
                    "clips": video_clips
                } if video_clips else {
                    "total_clips": 0,
                    "total_runtime": scene['duration_estimate'],
                    "clips": [],
                    "note": "Video clips planning was skipped"
                }
            }
            
            print(f"  ✅ Storyboard complete")
            print(f"     Format: {storyboard_format}")
            print(f"     Frames: {frame_count}")
            print(f"     Video clips: {len(video_clips)}")
            print(f"     Duration: {scene['duration_estimate']}s")
            
            # Update counters
            scenes_with_storyboards += 1
            total_frames_planned += frame_count
            total_video_clips += len(video_clips)
            
        except Exception as e:
            print(f"  ❌ Error creating storyboard: {e}")
            import traceback
            traceback.print_exc()
            
            # Add minimal storyboard
            scene['storyboard'] = {
                "format": "error",
                "total_frames": 0,
                "error": str(e)
            }
        
        updated_scenes.append(scene)
    
    print("\n" + "=" * 80)
    print(f"✅ STORYBOARD PLANNING COMPLETE")
    successful = sum(1 for s in updated_scenes if s.get('storyboard', {}).get('format') != 'error')
    print(f"   Storyboards created: {successful}/{len(scenes)}")
    total_frames = sum(s.get('storyboard', {}).get('total_frames', 0) for s in updated_scenes)
    print(f"   Total frames planned: {total_frames}")
    total_clips = sum(len(s.get('storyboard', {}).get('video_assembly', {}).get('clips', [])) for s in updated_scenes)
    print(f"   Total video clips: {total_clips}")
    print("=" * 80 + "\n")
    
    return {"scenes": updated_scenes}
