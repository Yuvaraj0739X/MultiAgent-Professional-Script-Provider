"""
Test Script for Phase 4: Character & Environment Extraction + Storyboard Planning

This demonstrates how to run Phase 4 with sample data.
In production, Phase 4 receives data from Phase 3.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from phase4_extraction import run_phase4, save_phase4_outputs


def create_sample_screenplay() -> str:
    """Create a sample screenplay for testing."""
    return """
NAPOLEON'S LAST STAND
Written by AI Screenplay Generator

FADE IN:

INT. ARJUN'S BEDROOM - NIGHT

A modest bedroom in an old apartment. Worn furniture. Digital clock
flashes 2:17 AM.

INSPECTOR ARJUN RAO (mid-40s, rugged features, worn face showing 
years of police work) sprawls on the bed, still in his rumpled 
police uniform.

An old photograph of a woman and child sits on the nightstand.

ARJUN's phone RINGS shrilly. He jolts awake.

                    ARJUN
                (bleary)
        Hello?

BREATHING on the other end. No voice. Just steady, unsettling breathing.

                    ARJUN (CONT'D)
                (warily)
        Who is this?

More breathing. ARJUN sits up, tension building.

                    ARJUN (CONT'D)
        If this is some kind of joke, it's 
        not funny.

The call ends. ARJUN stares at his cracked phone screen, his 
reflection visible in the dark glass.

He looks at the fallen photograph on the floor.

                    ARJUN (CONT'D)
                (softly, to himself)
        What have you gotten yourself into, Arjun?

CUT TO:

EXT. CRIME SCENE - DAY

A grim alley. Police tape flutters. ARJUN, now in fresh uniform, 
examines the scene.

MARSHAL NEY (46, weathered military bearing) approaches.

                    NEY
        Inspector, we have a situation.

                    ARJUN
        Always do.

FADE OUT.
"""


def create_sample_scene_breakdown() -> list:
    """Create sample scene breakdown from Phase 3."""
    return [
        {
            'scene_number': 1,
            'location': 'INT. ARJUN\'S BEDROOM - NIGHT',
            'time': 'NIGHT',
            'characters': ['ARJUN'],
            'key_action': 'Arjun receives mysterious phone call',
            'estimated_duration': 90
        },
        {
            'scene_number': 2,
            'location': 'EXT. CRIME SCENE - DAY',
            'time': 'DAY',
            'characters': ['ARJUN', 'NEY'],
            'key_action': 'Arjun investigates crime scene',
            'estimated_duration': 60
        }
    ]


def create_sample_metadata() -> dict:
    """Create sample metadata from Phase 3."""
    return {
        'page_count': 2,
        'estimated_duration': 2,
        'scene_count': 2,
        'character_count': 2,
        'location_count': 2,
        'characters': ['ARJUN', 'NEY'],
        'locations': ['ARJUN\'S BEDROOM', 'CRIME SCENE'],
        'generation_timestamp': '2026-01-19T10:00:00',
        'historical_accuracy': 'fictional'
    }


def main():
    """Run Phase 4 test."""
    
    print("\n" + "="*80)
    print("PHASE 4 TEST: Character & Environment Extraction + Storyboard Planning")
    print("="*80 + "\n")
    
    # Create sample data
    print("📝 Creating sample data...")
    screenplay_text = create_sample_screenplay()
    scene_breakdown = create_sample_scene_breakdown()
    screenplay_metadata = create_sample_metadata()
    
    session_id = "test_session_phase4"
    output_directory = str(Path(__file__).parent / "outputs" / session_id)
    
    print(f"✓ Sample screenplay: {len(screenplay_text)} characters")
    print(f"✓ Scenes: {len(scene_breakdown)}")
    print(f"✓ Output directory: {output_directory}\n")
    
    # Run Phase 4
    try:
        final_state = run_phase4(
            screenplay_text=screenplay_text,
            scene_breakdown=scene_breakdown,
            screenplay_metadata=screenplay_metadata,
            session_id=session_id,
            output_directory=output_directory,
            timeline=None,  # No historical data for this test
            key_figures=None,
            key_locations=None,
            verified_facts=None,
            use_checkpointer=False
        )
        
        # Save outputs
        output_paths = save_phase4_outputs(final_state, output_directory)
        
        print("\n" + "="*80)
        print("✅ PHASE 4 TEST COMPLETE!")
        print("="*80)
        print("\n📂 Output Files:")
        for output_type, path in output_paths.items():
            print(f"   {output_type}: {path}")
        
        print("\n💡 Next Steps:")
        print("   1. Review the generated JSON files")
        print("   2. Check characters_database.json for character details")
        print("   3. Check environments_database.json for location specs")
        print("   4. Check scenes_detailed.json for complete storyboard plans")
        print("   5. Use this data in Phase 5 for image/video generation\n")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()