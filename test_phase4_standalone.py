"""
Standalone Phase 4 Test Script
===============================
Tests Phase 4 extraction using existing Phase 3 outputs.

Usage:
    python test_phase4_standalone.py

Requirements:
    - Phase 3 outputs in: outputs/session_XXXXXX_XXXXXX/phase3_screenplay/
    - Phase 4 code in: phase4_extraction/
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from phase4_extraction import run_phase4, save_phase4_outputs


def load_phase3_outputs(session_dir: str):
    """
    Load all Phase 3 outputs from a session directory.
    
    Args:
        session_dir: Path to session directory (e.g., "outputs/session_20260121_120346")
    
    Returns:
        Dict containing all Phase 3 data
    """
    session_path = Path(session_dir)
    phase3_dir = session_path / "phase3_screenplay"
    
    if not phase3_dir.exists():
        raise FileNotFoundError(f"Phase 3 directory not found: {phase3_dir}")
    
    print("=" * 80)
    print("LOADING PHASE 3 OUTPUTS")
    print("=" * 80)
    print(f"📂 Session: {session_path.name}")
    print(f"📂 Location: {phase3_dir}")
    
    # Load screenplay text
    screenplay_file = phase3_dir / "screenplay.fountain"
    if not screenplay_file.exists():
        raise FileNotFoundError(f"Screenplay not found: {screenplay_file}")
    
    with open(screenplay_file, 'r', encoding='utf-8') as f:
        screenplay_text = f.read()
    print(f"✓ Loaded screenplay: {len(screenplay_text)} characters")
    
    # Load scene breakdown
    scene_breakdown_file = phase3_dir / "scene_breakdown.json"
    if not scene_breakdown_file.exists():
        raise FileNotFoundError(f"Scene breakdown not found: {scene_breakdown_file}")
    
    with open(scene_breakdown_file, 'r', encoding='utf-8') as f:
        scene_breakdown_data = json.load(f)
    scene_breakdown = scene_breakdown_data.get('scenes', [])
    print(f"✓ Loaded scene breakdown: {len(scene_breakdown)} scenes")
    
    # Load screenplay metadata
    metadata_file = phase3_dir / "screenplay_metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_file}")
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        screenplay_metadata = json.load(f)
    print(f"✓ Loaded metadata:")
    print(f"  - Pages: {screenplay_metadata.get('page_count')}")
    print(f"  - Duration: {screenplay_metadata.get('estimated_duration')} min")
    print(f"  - Scenes in screenplay: {screenplay_metadata.get('scene_count')}")
    print(f"  - Characters: {screenplay_metadata.get('character_count')}")
    
    # Load validation result (optional)
    validation_file = phase3_dir / "validation_result.json"
    validation_result = None
    if validation_file.exists():
        with open(validation_file, 'r', encoding='utf-8') as f:
            validation_result = json.load(f)
        print(f"✓ Loaded validation: {validation_result.get('compliance_score')}% compliance")
    
    print("\n✅ All Phase 3 outputs loaded successfully!\n")
    
    return {
        'screenplay_text': screenplay_text,
        'scene_breakdown': scene_breakdown,
        'screenplay_metadata': screenplay_metadata,
        'validation_result': validation_result,
        'session_path': session_path
    }


def run_phase4_test(session_dir: str, use_checkpointer: bool = False):
    """
    Run Phase 4 using Phase 3 outputs.
    
    Args:
        session_dir: Path to session directory
        use_checkpointer: Whether to use checkpointing (default: False for testing)
    """
    # Load Phase 3 outputs
    phase3_data = load_phase3_outputs(session_dir)
    
    # Create output directory
    output_dir = phase3_data['session_path']
    
    # Extract session ID from directory name
    session_id = phase3_data['session_path'].name
    
    print("=" * 80)
    print("RUNNING PHASE 4: CHARACTER & ENVIRONMENT EXTRACTION")
    print("=" * 80)
    print(f"📋 Session ID: {session_id}")
    print(f"📂 Output Directory: {output_dir}")
    print(f"🎬 Scenes to Process: {len(phase3_data['scene_breakdown'])}")
    print(f"📄 Screenplay Length: {len(phase3_data['screenplay_text'])} chars")
    print()
    
    # Run Phase 4
    try:
        phase4_result = run_phase4(
            screenplay_text=phase3_data['screenplay_text'],
            scene_breakdown=phase3_data['scene_breakdown'],
            screenplay_metadata=phase3_data['screenplay_metadata'],
            session_id=session_id,
            output_directory=str(output_dir),
            # Optional historical data (if you have Phase 2 outputs)
            timeline=None,
            key_figures=None,
            key_locations=None,
            verified_facts=None,
            use_checkpointer=use_checkpointer
        )
        
        # Save outputs
        print("\n" + "=" * 80)
        print("SAVING PHASE 4 OUTPUTS")
        print("=" * 80)
        
        phase4_files = save_phase4_outputs(phase4_result, str(output_dir))
        
        print("\n✅ Phase 4 outputs saved:")
        for filename, filepath in phase4_files.items():
            file_size = Path(filepath).stat().st_size / 1024  # KB
            print(f"  ✓ {filename}: {file_size:.1f} KB")
        
        # Display statistics
        print("\n" + "=" * 80)
        print("PHASE 4 STATISTICS")
        print("=" * 80)
        
        stats = phase4_result.get('extraction_metadata', {}).get('statistics', {})
        print(f"\n📊 Extraction Summary:")
        print(f"  Characters extracted: {stats.get('total_characters', 0)}")
        print(f"  Voice profiles: {stats.get('characters_with_voice_profiles', 0)}")
        print(f"  Environments: {stats.get('total_environments', 0)}")
        print(f"  Scenes analyzed: {stats.get('total_scenes', 0)}")
        print(f"  Storyboards created: {stats.get('scenes_with_storyboards', 0)}")
        print(f"  Total frames planned: {stats.get('total_frames_planned', 0)}")
        print(f"  Total video clips: {stats.get('total_video_clips', 0)}")
        
        # Calculate success rates
        total_scenes = len(phase3_data['scene_breakdown'])
        storyboards_created = stats.get('scenes_with_storyboards', 0)
        success_rate = (storyboards_created / total_scenes * 100) if total_scenes > 0 else 0
        
        print(f"\n📈 Success Rates:")
        print(f"  Scene analysis: {stats.get('total_scenes', 0)}/{total_scenes} ({stats.get('total_scenes', 0)/total_scenes*100:.1f}%)")
        print(f"  Storyboard creation: {storyboards_created}/{total_scenes} ({success_rate:.1f}%)")
        
        # Duration
        duration = phase4_result.get('extraction_metadata', {}).get('duration_seconds', 0)
        print(f"\n⏱️  Total Duration: {duration:.1f}s (~{duration/60:.1f} minutes)")
        
        print("\n" + "=" * 80)
        print("✅ PHASE 4 TEST COMPLETE!")
        print("=" * 80)
        
        # Final output location
        phase4_dir = output_dir / "phase4_extraction"
        print(f"\n📁 Phase 4 outputs saved to:")
        print(f"   {phase4_dir}")
        print(f"\n📄 Key files:")
        print(f"   - characters_database.json")
        print(f"   - environments_database.json")
        print(f"   - scenes_detailed.json")
        print(f"   - storyboard_summary.json")
        print(f"   - phase4_metadata.json")
        
        return phase4_result
        
    except Exception as e:
        print(f"\n❌ Error running Phase 4: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main test function."""
    print("\n" + "=" * 80)
    print("PHASE 4 STANDALONE TEST")
    print("=" * 80)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ========================================
    # CONFIGURATION
    # ========================================
    
    # OPTION 1: Specify session directory directly
    # Uncomment and modify the line below with your session directory
    SESSION_DIR = "outputs/session_20260121_120346"  # ← CHANGE THIS!
    
    # OPTION 2: Find the most recent session automatically
    # Uncomment the code below to auto-detect latest session
    # from pathlib import Path
    # outputs_dir = Path("outputs")
    # sessions = sorted([d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("session_")])
    # if not sessions:
    #     print("❌ No session directories found in outputs/")
    #     return
    # SESSION_DIR = str(sessions[-1])  # Most recent
    # print(f"📂 Auto-detected latest session: {SESSION_DIR}")
    
    # ========================================
    # RUN TEST
    # ========================================
    
    try:
        result = run_phase4_test(
            session_dir=SESSION_DIR,
            use_checkpointer=False  # Set True to enable checkpointing
        )
        
        if result:
            print("\n✅ Test completed successfully!")
            print(f"\n💡 Tip: Check the phase4_extraction/ folder in your session directory")
            print(f"   to see all generated outputs.")
        else:
            print("\n❌ Test failed!")
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Make sure you have Phase 3 outputs in the correct location:")
        print(f"   {SESSION_DIR}/phase3_screenplay/")
        print(f"\n   Required files:")
        print(f"   - screenplay.fountain")
        print(f"   - scene_breakdown.json")
        print(f"   - screenplay_metadata.json")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
