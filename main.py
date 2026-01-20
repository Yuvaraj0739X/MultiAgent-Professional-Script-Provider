"""
Main Pipeline Orchestrator
Integrates Phases 1-4 for complete screenplay generation and storyboard planning
"""

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from shared.session import SessionManager, generate_session_id
from phase1_intake.graph import run_phase1_workflow as run_phase1
from phase2_research.graph import run_phase2_workflow as run_phase2
from phase3_screenplay import run_phase3, save_phase3_outputs
from phase4_extraction import run_phase4, save_phase4_outputs


def main(user_input: str = None):
    """
    Complete video production pipeline (Phases 1-4).
    
    Pipeline Flow:
    1. Phase 1: User intake → story brief
    2. Phase 2: Historical research (if needed) → timeline, facts, figures
    3. Phase 3: Screenplay generation → complete Fountain screenplay
    4. Phase 4: Extraction + storyboarding → characters, environments, scenes
    
    Args:
        user_input: User's story concept (optional - will prompt if not provided)
    """
    
    # ===== GET USER INPUT =====
    if not user_input:
        print("\n" + "🎬" * 40)
        print("SCREENPLAY GENERATION PIPELINE")
        print("🎬" * 40 + "\n")
        user_input = input("📝 Describe your story idea: ").strip()
        if not user_input:
            print("❌ No input provided. Exiting.")
            return
    
    # ===== CREATE SESSION =====
    session_id = generate_session_id()
    session = SessionManager(session_id)
    output_dir = str(session.outputs_dir)
    
    print(f"\n{'='*80}")
    print(f"🎬 STARTING PIPELINE")
    print(f"{'='*80}")
    print(f"📋 Session: {session_id}")
    print(f"💡 Concept: {user_input}")
    print(f"📂 Output: {output_dir}\n")
    
    # ===== PHASE 1: STORY DEVELOPMENT =====
    print("=" * 80)
    print("PHASE 1: STORY DEVELOPMENT")
    print("=" * 80)
    
    try:
        phase1_result = run_phase1(user_input, session_id)
        
        brief_text = phase1_result.get('final_brief', '')
        research_required = phase1_result.get('research_required', False)
        
        # Save brief
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        brief_path = f"{output_dir}/phase1_brief.md"
        with open(brief_path, 'w', encoding='utf-8') as f:
            f.write(brief_text)
        
        print(f"\n✅ Phase 1 Complete!")
        print(f"   Brief: {len(brief_text)} characters")
        print(f"   Research required: {research_required}")
        print(f"   Saved: {brief_path}\n")
        
    except Exception as e:
        print(f"\n❌ Phase 1 Failed: {e}")
        raise
    
    # ===== PHASE 2: RESEARCH (if historical) =====
    phase2_result = None
    
    if research_required:
        print("=" * 80)
        print("PHASE 2: HISTORICAL RESEARCH & FACT VERIFICATION")
        print("=" * 80)
        
        try:
            phase2_result = run_phase2(brief_text, session_id, output_dir)
            
            timeline_count = len(phase2_result.get('timeline', []))
            figures_count = len(phase2_result.get('key_figures', []))
            locations_count = len(phase2_result.get('key_locations', []))
            
            print(f"\n✅ Phase 2 Complete!")
            print(f"   Timeline events: {timeline_count}")
            print(f"   Key figures: {figures_count}")
            print(f"   Key locations: {locations_count}")
            print(f"   Verified facts: {len(phase2_result.get('verified_facts', []))}\n")
            
        except Exception as e:
            print(f"\n❌ Phase 2 Failed: {e}")
            print("⚠️  Continuing without research data...\n")
            phase2_result = None
    else:
        print("=" * 80)
        print("⏭️  PHASE 2: SKIPPED (Fictional Story)")
        print("=" * 80 + "\n")
    
    # ===== PHASE 3: SCREENPLAY GENERATION =====
    print("=" * 80)
    print("PHASE 3: SCREENPLAY GENERATION")
    print("=" * 80)
    
    try:
        phase3_result = run_phase3(
            phase1_brief=brief_text,
            user_input=user_input,
            research_required=research_required,
            timeline=phase2_result.get('timeline') if phase2_result else None,
            key_figures=phase2_result.get('key_figures') if phase2_result else None,
            key_locations=phase2_result.get('key_locations') if phase2_result else None,
            verified_facts=phase2_result.get('verified_facts') if phase2_result else None,
            session_id=session_id,
            output_directory=output_dir,
            use_checkpointer=False
        )
        
        # Save Phase 3 outputs
        phase3_files = save_phase3_outputs(phase3_result, output_dir)
        
        # Get metadata
        metadata = phase3_result.get('screenplay_metadata', {})
        scene_breakdown = phase3_result.get('scene_breakdown', [])
        
        print(f"\n✅ Phase 3 Complete!")
        print(f"   Pages: {metadata.get('page_count', 0)}")
        print(f"   Scenes: {len(scene_breakdown)}")
        print(f"   Duration: {metadata.get('estimated_duration', 0)} minutes")
        print(f"   Screenplay: {phase3_files.get('screenplay', 'saved')}\n")
        
    except Exception as e:
        print(f"\n❌ Phase 3 Failed: {e}")
        raise
    
    # ===== PHASE 4: EXTRACTION + STORYBOARD PLANNING =====
    print("=" * 80)
    print("PHASE 4: CHARACTER & ENVIRONMENT EXTRACTION + STORYBOARD PLANNING")
    print("=" * 80)
    
    try:
        phase4_result = run_phase4(
            screenplay_text=phase3_result['screenplay_text'],
            scene_breakdown=phase3_result.get('scene_breakdown', []),
            screenplay_metadata=phase3_result['screenplay_metadata'],
            session_id=session_id,
            output_directory=output_dir,
            # Pass historical data if available
            timeline=phase2_result.get('timeline') if phase2_result else None,
            key_figures=phase2_result.get('key_figures') if phase2_result else None,
            key_locations=phase2_result.get('key_locations') if phase2_result else None,
            verified_facts=phase2_result.get('verified_facts') if phase2_result else None,
            use_checkpointer=False
        )
        
        # Save Phase 4 outputs
        phase4_files = save_phase4_outputs(phase4_result, output_dir)
        
        # Get statistics
        stats = phase4_result.get('extraction_metadata', {}).get('statistics', {})
        
        print(f"\n✅ Phase 4 Complete!")
        print(f"   Characters: {stats.get('total_characters', 0)}")
        print(f"   Voice profiles: {stats.get('characters_with_voice_profiles', 0)}")
        print(f"   Environments: {stats.get('total_environments', 0)}")
        print(f"   Scenes analyzed: {stats.get('total_scenes', 0)}")
        print(f"   Storyboards: {stats.get('scenes_with_storyboards', 0)}")
        print(f"   Total frames: {stats.get('total_frames_planned', 0)}")
        print(f"   Video clips: {stats.get('total_video_clips', 0)}\n")
        
    except Exception as e:
        print(f"\n❌ Phase 4 Failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Pipeline completed through Phase 3")
        print("   Phase 4 outputs may be incomplete\n")
        phase4_files = {}
        phase4_result = {}
    
    # ===== FINAL SUMMARY =====
    print("\n" + "🎬" * 40)
    print("✅ PIPELINE COMPLETE!")
    print("🎬" * 40)
    
    print(f"\n📂 Session Directory: {output_dir}")
    
    print(f"\n📄 Generated Files:")
    print(f"\n   Phase 1: Story Development")
    print(f"   └─ phase1_brief.md")
    
    if phase2_result:
        print(f"\n   Phase 2: Historical Research")
        print(f"   └─ phase2_research/")
        print(f"      ├─ timeline.json")
        print(f"      ├─ key_figures.json")
        print(f"      ├─ key_locations.json")
        print(f"      └─ verified_facts.json")
    
    print(f"\n   Phase 3: Screenplay")
    print(f"   └─ phase3_screenplay/")
    print(f"      ├─ screenplay.fountain ⭐")
    print(f"      ├─ scene_breakdown.json")
    print(f"      └─ screenplay_metadata.json")
    
    if phase4_files:
        print(f"\n   Phase 4: Extraction & Storyboards")
        print(f"   └─ phase4_extraction/")
        print(f"      ├─ characters_database.json ⭐")
        print(f"      ├─ environments_database.json")
        print(f"      ├─ scenes_detailed.json ⭐")
        print(f"      ├─ storyboard_summary.json")
        print(f"      └─ phase4_metadata.json")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Review screenplay: {phase3_files.get('screenplay', output_dir + '/phase3_screenplay/screenplay.fountain')}")
    
    if phase4_files:
        print(f"   2. Review characters: {phase4_files.get('characters', output_dir + '/phase4_extraction/characters_database.json')}")
        print(f"   3. Review storyboards: {phase4_files.get('scenes', output_dir + '/phase4_extraction/scenes_detailed.json')}")
        print(f"   4. Ready for Phase 5: Image & Video Generation")
    else:
        print(f"   2. Check Phase 4 errors and retry if needed")
    
    print(f"\n🎉 SESSION COMPLETE!\n")
    
    # Return summary for programmatic use
    return {
        "session_id": session_id,
        "output_directory": output_dir,
        "phase1_complete": True,
        "phase2_complete": phase2_result is not None,
        "phase3_complete": True,
        "phase4_complete": bool(phase4_files),
        "files": {
            "phase1": {"brief": f"{output_dir}/phase1_brief.md"},
            "phase3": phase3_files,
            "phase4": phase4_files
        },
        "statistics": {
            "screenplay": {
                "pages": metadata.get('page_count', 0),
                "scenes": len(scene_breakdown),
                "duration_minutes": metadata.get('estimated_duration', 0)
            },
            "extraction": stats if phase4_files else {}
        }
    }


# ==============================================================================
# COMMAND-LINE INTERFACE
# ==============================================================================

if __name__ == "__main__":
    import sys
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Use command-line input
        concept = " ".join(sys.argv[1:])
        main(concept)
    else:
        # Interactive mode
        main()


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

"""
USAGE:

1. Interactive Mode:
   python main.py
   → Prompts user for story concept
   → Runs complete pipeline

2. Command-Line Mode (Fictional):
   python main.py "A detective receives a mysterious phone call at 2 AM"
   → Phase 1: Creates story brief
   → Phase 2: Skipped (fictional)
   → Phase 3: Generates screenplay
   → Phase 4: Extracts characters, environments, creates storyboards

3. Command-Line Mode (Historical):
   python main.py "Napoleon Bonaparte and the Battle of Waterloo"
   → Phase 1: Creates story brief, detects historical content
   → Phase 2: Researches timeline, key figures, locations
   → Phase 3: Generates historically accurate screenplay
   → Phase 4: Extracts characters (with historical data), creates storyboards

4. Programmatic Use:
   from main import main
   
   result = main("A robot learns to love")
   
   print(f"Session: {result['session_id']}")
   print(f"Screenplay: {result['files']['phase3']['screenplay']}")
   print(f"Characters: {result['files']['phase4']['characters']}")

OUTPUTS:

All outputs saved to: outputs/session_YYYYMMDD_HHMMSS/

├─ phase1_brief.md
├─ phase2_research/ (if historical)
│  ├─ timeline.json
│  ├─ key_figures.json
│  ├─ key_locations.json
│  └─ verified_facts.json
├─ phase3_screenplay/
│  ├─ screenplay.fountain
│  ├─ scene_breakdown.json
│  └─ screenplay_metadata.json
└─ phase4_extraction/
   ├─ characters_database.json
   ├─ environments_database.json
   ├─ scenes_detailed.json
   ├─ storyboard_summary.json
   └─ phase4_metadata.json

NEXT: Use Phase 4 outputs for Phase 5 (Image & Video Generation)
"""