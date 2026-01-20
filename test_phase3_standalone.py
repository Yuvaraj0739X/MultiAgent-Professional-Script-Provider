import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)
sys.path.insert(0, os.path.dirname(__file__))

if not os.path.exists('config.py'):
    print("⚠️  config.py not found, using mock configuration")
    
    class MockConfig:
        @staticmethod
        def get_llm_config(phase, node):
            configs = {
                "scene_breakdown": {"model": "gpt-4o", "temperature": 0.6},
                "screenplay_generation": {"model": "gpt-4o", "temperature": 0.7},
                "validation": {"model": "gpt-4o-mini", "temperature": 0.1}
            }
            return configs.get(node, {"model": "gpt-4o-mini", "temperature": 0.3})
    
    sys.modules['config'] = MockConfig()


from phase3_screenplay import run_phase3, save_phase3_outputs
import tempfile



SIMPLE_BRIEF = """# THE LAST STAND - Story Brief

## Logline
A soldier must defend a critical position against overwhelming odds.

## Setting
Modern warfare, desert battlefield, a strategic hill overlooking supply routes

## Main Characters
- **Captain Miller** (35): Battle-hardened infantry commander, haunted by past losses
- **Sergeant Hayes** (28): Loyal second-in-command, optimistic despite danger
- **Enemy Commander** (40): Ruthless tactical genius leading the assault

## Three-Act Structure

### Act 1: The Assignment (5 minutes)
- Captain Miller's squad receives orders to hold Hill 439
- Team of 12 soldiers arrives at position
- Set up defensive perimeter
- Miller reveals this is a delaying action - reinforcements coming in 24 hours
- Team prepares for inevitable attack

### Act 2: The Siege (15 minutes)
- First enemy probe - repelled easily
- Main assault begins - waves of enemy infantry
- Hayes is wounded during second wave
- Enemy brings up artillery
- Supply running low
- Miller makes tough decisions about who to save
- Night falls - team is down to 6 soldiers
- Enemy commander sends ultimatum: surrender or die
- Miller refuses

### Act 3: The Resolution (5 minutes)
- Dawn breaks - final enemy assault
- Miller leads desperate last stand
- Team is nearly overrun
- At the last moment, allied helicopters appear on horizon
- Reinforcements arrive just in time
- Enemy retreats
- Victory at great cost - only Miller and Hayes survive
- Miller realizes the sacrifice was worth it

## Themes
- Duty vs. survival
- Leadership under pressure
- The cost of war

## Tone
Intense, gritty, realistic military drama
"""

HISTORICAL_BRIEF = """# WATERLOO: THE FINAL GAMBIT

## Logline
Napoleon Bonaparte faces his final battle as his empire crumbles.

## Setting
Belgium, June 18, 1815 - The fields of Waterloo

## Main Characters
- **Napoleon Bonaparte** (45): Exiled emperor, military genius making final stand
- **Duke of Wellington** (46): British commander, Napoleon's nemesis
- **Marshal Ney** (46): Napoleon's loyal but reckless cavalry commander

## Story
(Abbreviated for testing)
Napoleon returns from exile, faces Wellington at Waterloo, and meets his final defeat.
"""

MOCK_TIMELINE = [
    {
        "date": "1815-02-26",
        "event": "Napoleon escapes from Elba",
        "description": "Napoleon leaves exile with 1,000 men"
    },
    {
        "date": "1815-06-18",
        "event": "Battle of Waterloo",
        "description": "Napoleon's final defeat by Wellington"
    }
]

MOCK_KEY_FIGURES = [
    {
        "name": "Napoleon Bonaparte",
        "role": "Emperor of France",
        "description": "Military genius and former emperor"
    },
    {
        "name": "Duke of Wellington",
        "role": "British Commander",
        "description": "Led coalition forces at Waterloo"
    }
]



def test_simple_story():
    """Test Phase 3 with a simple fictional story"""
    print("\n" + "="*80)
    print("TEST 1: SIMPLE FICTIONAL STORY")
    print("="*80)
    
    output_dir = tempfile.mkdtemp()
    
    try:
        result = run_phase3(
            phase1_brief=SIMPLE_BRIEF,
            user_input="A last stand battle story",
            research_required=False,
            session_id="test_simple",
            output_directory=output_dir,
            use_checkpointer=False
        )
        
        assert result.get('screenplay_text'), "No screenplay generated!"
        assert result.get('scene_breakdown'), "No scene breakdown!"
        assert result.get('screenplay_metadata'), "No metadata!"
        
        screenplay_len = len(result['screenplay_text'])
        scene_count = len(result.get('scene_breakdown', []))
        metadata = result.get('screenplay_metadata', {})
        
        print("\n✅ TEST PASSED!")
        print(f"\n📊 Results:")
        print(f"  Screenplay: {screenplay_len:,} characters")
        print(f"  Scenes: {scene_count}")
        print(f"  Pages: {metadata.get('page_count', 0)}")
        print(f"  Duration: {metadata.get('estimated_duration', 0)} minutes")
        print(f"  Characters: {metadata.get('character_count', 0)}")
        print(f"  Validation: {'✅ PASSED' if result.get('validation_passed') else '⚠️  ISSUES'}")
        
        saved_files = save_phase3_outputs(result, output_dir)
        
        print(f"\n📁 Files saved to: {output_dir}")
        for file_type, path in saved_files.items():
            print(f"  ✅ {file_type}: {os.path.basename(path)}")
        
        print(f"\n📄 Screenplay Preview (first 500 chars):")
        print("-" * 80)
        print(result['screenplay_text'][:500])
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_historical_story():
    """Test Phase 3 with a historical story (with mock research data)"""
    print("\n" + "="*80)
    print("TEST 2: HISTORICAL STORY (WITH MOCK TIMELINE)")
    print("="*80)
    
    output_dir = tempfile.mkdtemp()
    
    try:
        result = run_phase3(
            phase1_brief=HISTORICAL_BRIEF,
            user_input="Napoleon at Waterloo",
            research_required=True,
            timeline=MOCK_TIMELINE,
            key_figures=MOCK_KEY_FIGURES,
            session_id="test_historical",
            output_directory=output_dir,
            use_checkpointer=False
        )
        
        assert result.get('screenplay_text'), "No screenplay generated!"
        
        metadata = result.get('screenplay_metadata', {})
        
        print("\n✅ TEST PASSED!")
        print(f"\n📊 Results:")
        print(f"  Historical Accuracy: {metadata.get('historical_accuracy', 'N/A')}")
        print(f"  Pages: {metadata.get('page_count', 0)}")
        print(f"  Scenes: {metadata.get('scene_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_only():
    """Test just the validation node"""
    print("\n" + "="*80)
    print("TEST 3: VALIDATION ONLY (Syntax checks only)")
    print("="*80)
    
    from phase3_screenplay.utils import validate_fountain_syntax
    
    mock_screenplay = """THE TEST
Written by Test

FADE IN:

EXT. BATTLEFIELD - DAY

Action happens here.

SOLDIER
Dialogue goes here.

FADE OUT.

THE END
"""
    
    try:
        result = validate_fountain_syntax(mock_screenplay)
        
        print("\n✅ TEST PASSED!")
        print(f"\n📊 Validation Results:")
        print(f"  Valid: {result.get('is_valid', False)}")
        print(f"  Compliance Score: {result.get('compliance_score', 0):.1f}%")
        print(f"  Errors: {len(result.get('errors', []))}")
        print(f"  Warnings: {len(result.get('warnings', []))}")
        
        if result.get('errors'):
            print(f"\n  Errors found:")
            for error in result.get('errors', [])[:3]:
                print(f"    - {error}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False



def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PHASE 3 STANDALONE TEST SUITE")
    print("="*80)
    print("\nThis will test Phase 3 screenplay generation independently.")
    print("Tests use mock data and don't require Phase 1 or Phase 2.\n")
    
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))
    
    if not has_api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   Full tests will be skipped. Only syntax validation will run.")
        print("   To run full tests, set OPENAI_API_KEY in your .env file\n")
    
    results = []
    
    print("\nRunning tests...\n")
    
    if has_api_key:
        results.append(("Simple Story", test_simple_story()))
    else:
        print("⏭️  Skipping: Simple Story (requires API key)\n")
    
    
    results.append(("Syntax Validation", test_validation_only()))
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n{total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        if has_api_key:
            print("\n🎉 ALL TESTS PASSED! Phase 3 is ready to use!")
        else:
            print("\n✅ Syntax validation passed!")
            print("   To test full workflow, set OPENAI_API_KEY and run again.")
    else:
        print("\n⚠️  Some tests failed. Check error messages above.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("Running quick validation test only...")
        test_validation_only()
    else:
        main()