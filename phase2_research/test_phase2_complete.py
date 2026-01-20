import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from state import create_phase2_initial_state
from graph import run_phase2_workflow


def create_mock_phase1_output():
    """Create mock Phase 1 output for testing"""
    return {
        "final_brief": """
# WATERLOO: THE FINAL GAMBLE

## LOGLINE
In June 1815, Napoleon Bonaparte wages a desperate final campaign across 
Belgium, facing the combined forces of Wellington and Blücher in a 
multi-perspective war epic culminating in the Battle of Waterloo.

## CLASSIFICATION & METADATA
- **Type:** real
- **Research Required:** yes
- **Genre:** Historical War Epic
- **Tone:** Gritty realism, epic scale with intimate character moments
- **Target Runtime:** 25-30 minutes

## SYNOPSIS
A 25-minute multi-perspective historical war epic covering the final week 
of the Hundred Days campaign (June 12-18, 1815), following Napoleon Bonaparte 
(40% screen time) alongside the Duke of Wellington and Marshal Blücher as 
they make strategic decisions leading to the decisive Battle of Waterloo.

The story explores Napoleon's transformation from confident strategist to 
defeated emperor, Wellington's defensive genius, and Blücher's determined 
pursuit despite injury. The narrative builds to the climactic battle, showing 
the fog of war, critical decisions, and the narrow margins that determined 
European history.

## TIMELINE STRUCTURE
Compressed 3-act structure:
- Act 1: The Gamble (June 12-15) - Napoleon's decision to strike preemptively
- Act 2: The Approach (June 16-17) - Battles of Quatre Bras and Ligny
- Act 3: Waterloo (June 18) - The final battle (50% of runtime)

## THEMES
- The end of greatness
- Leadership under pressure
- Historical inevitability vs individual will
- The human cost of ambition
        """,
        "classification": "real",
        "research_required": True,
        "detected_elements": {
            "protagonist": "Napoleon Bonaparte",
            "supporting_characters": "Duke of Wellington, Marshal Blücher",
            "time_period": "June 1815",
            "central_event": "Battle of Waterloo",
            "genre": "historical war epic",
            "setting": "Belgium"
        },
        "user_input_refined": "Multi-perspective historical war epic following Napoleon Bonaparte during the final week of the Hundred Days campaign (June 12-18, 1815), culminating in the Battle of Waterloo",
        "session_id": "test_phase2_complete"
    }


def save_results(final_state, output_dir="test_outputs"):
    """Save Phase 2 results to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/verified_facts.json", 'w') as f:
        json.dump(final_state.get("verified_facts", []), f, indent=2)
    
    with open(f"{output_dir}/timeline.json", 'w') as f:
        json.dump(final_state.get("timeline", []), f, indent=2)
    
    with open(f"{output_dir}/key_figures.json", 'w') as f:
        json.dump(final_state.get("key_figures", []), f, indent=2)
    
    with open(f"{output_dir}/key_locations.json", 'w') as f:
        json.dump(final_state.get("key_locations", []), f, indent=2)
    
    summary = f"""# PHASE 2 RESEARCH SUMMARY

## Research Queries
Generated {len(final_state.get('research_queries', []))} queries

## Wikipedia Articles
Fetched {final_state.get('fetch_success_count', 0)} articles

## Fact Extraction
- Total facts extracted: {len(final_state.get('extracted_facts', []))}
- Verified facts: {len(final_state.get('verified_facts', []))}
- Disputed facts: {len(final_state.get('disputed_facts', []))}
- Unverified facts: {len(final_state.get('unverified_facts', []))}

## Timeline
- Timeline span: {final_state.get('timeline_metadata', {}).get('timeline_span', 'N/A') if final_state.get('timeline_metadata') else 'N/A'}
- Total events: {len(final_state.get('timeline', []))}
- Key figures: {len(final_state.get('key_figures', []))}
- Key locations: {len(final_state.get('key_locations', []))}

## Verification Rate
{final_state.get('validation_summary', {}).get('verification_rate', 0) * 100:.1f}% of facts verified
"""
    
    with open(f"{output_dir}/research_summary.md", 'w') as f:
        f.write(summary)
    
    print(f"\n💾 Results saved to: {output_dir}/")


def test_complete_phase2():
    """Run complete Phase 2 workflow test"""
    
    print("\n" + "╔"*70)
    print("PHASE 2: COMPLETE WORKFLOW TEST")
    print("╚"*70)
    
    print("\n📋 This will test the entire Phase 2 pipeline:")
    print("   1. Research Strategy (generate Wikipedia queries)")
    print("   2. Wikipedia Fetch (retrieve articles)")
    print("   3. Fact Extraction (extract facts from articles)")
    print("   4. Fact Validation (cross-reference sources)")
    print("   5. Timeline Build (create chronological timeline)")
    
    print("\n⏱️  Estimated time: 2-3 minutes")
    print("💰 Using: gpt-4o-mini (cost-effective)")
    
    input("\n▶️  Press ENTER to start the test...\n")
    
    mock_phase1 = create_mock_phase1_output()
    initial_state = create_phase2_initial_state(
        phase1_output=mock_phase1,
        session_id="test_phase2_complete"
    )
    
    print("\n" + "="*70)
    print("STARTING PHASE 2 WORKFLOW")
    print("="*70)
    
    try:
        final_state = run_phase2_workflow(initial_state)
        
        print("\n" + "╔"*70)
        print("PHASE 2 WORKFLOW COMPLETE!")
        print("╚"*70)
        
        print("\n" + "="*70)
        print("FINAL RESULTS SUMMARY")
        print("="*70)
        
        queries = final_state.get("research_queries", [])
        print(f"\n📊 Research Queries: {len(queries)}")
        if queries:
            print("   Sample queries:")
            for q in queries[:3]:
                print(f"   • {q['query']}")
        
        articles = final_state.get("wikipedia_articles", [])
        print(f"\n📚 Wikipedia Articles: {len(articles)}")
        if articles:
            print("   Sample articles:")
            for a in articles[:3]:
                print(f"   • {a['title']}")
        
        extracted = final_state.get("extracted_facts", [])
        verified = final_state.get("verified_facts", [])
        disputed = final_state.get("disputed_facts", [])
        unverified = final_state.get("unverified_facts", [])
        
        print(f"\n🔍 Fact Extraction:")
        print(f"   • Extracted: {len(extracted)}")
        print(f"   • Verified (2+ sources): {len(verified)}")
        print(f"   • Disputed (conflicts): {len(disputed)}")
        print(f"   • Unverified (1 source): {len(unverified)}")
        
        validation = final_state.get("validation_summary", {})
        if validation:
            print(f"   • Verification rate: {validation.get('verification_rate', 0)*100:.1f}%")
        
        timeline = final_state.get("timeline", [])
        figures = final_state.get("key_figures", [])
        locations = final_state.get("key_locations", [])
        
        print(f"\n📅 Timeline Construction:")
        print(f"   • Events: {len(timeline)}")
        print(f"   • Key figures: {len(figures)}")
        print(f"   • Key locations: {len(locations)}")
        
        metadata = final_state.get("timeline_metadata", {})
        if metadata:
            span = metadata.get('timeline_span', 'N/A') if metadata else 'N/A'
            print(f"   • Timeline span: {span}")
        
        if timeline:
            print(f"\n📅 Sample Timeline Events:")
            for event in timeline[:3]:
                print(f"\n   {event['date']} - {event['event_title']}")
                print(f"   {event['event_description'][:100]}...")
        
        if figures:
            print(f"\n👥 Key Figures:")
            for fig in figures[:3]:
                print(f"   • {fig['name']} - {fig['role']}")
        
        if locations:
            print(f"\n📍 Key Locations:")
            for loc in locations[:2]:
                print(f"   • {loc['name']} ({loc['location_type']})")
        
        print("\n" + "="*70)
        save_results(final_state)
        
        print("\n✅ Workflow Status:")
        print(f"   Current step: {final_state.get('current_step', 'unknown')}")
        print(f"   Workflow complete: {final_state.get('workflow_complete', False)}")
        
        errors = final_state.get("errors", [])
        if errors:
            print(f"\n⚠️  Errors encountered: {len(errors)}")
            for error in errors:
                print(f"   • {error}")
        else:
            print("\n✅ No errors - all nodes completed successfully!")
        
        print("\n" + "╔"*70)
        print("TEST COMPLETE - PHASE 2 WORKING!")
        print("╚"*70 + "\n")
        
        return final_state
        
    except Exception as e:
        print(f"\n\n❌ Phase 2 workflow failed!")
        print(f"Error: {str(e)}\n")
        
        import traceback
        print("Full error trace:")
        print("─"*70)
        traceback.print_exc()
        print("─"*70 + "\n")
        
        return None


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        sys.exit(1)
    
    print("\n🚀 Starting Phase 2 complete workflow test...")
    print("💡 Using gpt-4o-mini for all nodes (cost-effective)\n")
    
    final_state = test_complete_phase2()
    
    if final_state:
        print("✅ Phase 2 test completed successfully!")
        print("\n📁 Check test_outputs/ folder for detailed results\n")
    else:
        print("❌ Phase 2 test failed - check errors above\n")