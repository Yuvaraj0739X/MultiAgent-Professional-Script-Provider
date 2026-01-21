"""
Test script for Phase 3 dialogue detection fix
WITH FORCED MODULE RELOAD to avoid caching issues
"""

import sys
import os
import importlib

# FORCE RELOAD if already imported
if 'phase3_screenplay' in sys.modules:
    print("⚠️  Reloading phase3_screenplay modules to get latest code...")
    # Remove all phase3_screenplay modules from cache
    mods_to_remove = [k for k in sys.modules.keys() if k.startswith('phase3_screenplay')]
    for mod in mods_to_remove:
        del sys.modules[mod]

# NOW import fresh
from phase3_screenplay.utils import validate_fountain_syntax

# Test screenplays
TEST_SCREENPLAY_WITH_DIALOGUE = """
NAPOLEON'S LAST STAND

FADE IN:

EXT. WATERLOO BATTLEFIELD - DAY

Mud and chaos. Cannons roar.

NAPOLEON BONAPARTE, 45, weathered, surveys the battlefield from horseback.

NAPOLEON
(to officers)
The time has come.

MARSHAL NEY approaches, frantic.

NEY
Sire, the Prussians!

NAPOLEON
Then we attack now.

FADE OUT.

THE END
"""

TEST_SCREENPLAY_NO_DIALOGUE = """
SILENT FILM

FADE IN:

EXT. DESERT - DAY

A lone figure walks across endless sand dunes.

The sun beats down mercilessly.

Wind whips sand into swirling patterns.

FADE OUT.

THE END
"""

TEST_SCREENPLAY_COMPLEX = """
INT. BEDROOM - NIGHT

ARJUN lies in bed, exhausted.

Phone RINGS.

ARJUN
(bleary)
Hello?

Silence. Heavy breathing.

ARJUN (CONT'D)
(warily)
Who is this?

More silence.

ARJUN (CONT'D)
(low, commanding)
If this is some kind of joke, it's not funny.

The line goes dead.

FADE OUT.
"""


def test_dialogue_detection():
    """Test the fixed validate_fountain_syntax function"""
    
    print("="*80)
    print("TESTING PHASE 3 DIALOGUE DETECTION FIX (WITH RELOAD)")
    print("="*80)
    
    # Test 1: Screenplay WITH dialogue
    print("\nTest 1: Screenplay WITH dialogue")
    print("-" * 40)
    result1 = validate_fountain_syntax(TEST_SCREENPLAY_WITH_DIALOGUE)
    
    warnings1 = result1['warnings']
    has_dialogue_warning = any('dialogue' in w.lower() for w in warnings1)
    
    print(f"Warnings: {warnings1}")
    print(f"Has 'No dialogue' warning: {has_dialogue_warning}")
    
    if has_dialogue_warning:
        print("❌ FAILED: False positive - dialogue exists but warning triggered!")
    else:
        print("✅ PASSED: No false dialogue warning")
    
    # Test 2: Screenplay WITHOUT dialogue
    print("\nTest 2: Screenplay WITHOUT dialogue")
    print("-" * 40)
    result2 = validate_fountain_syntax(TEST_SCREENPLAY_NO_DIALOGUE)
    
    warnings2 = result2['warnings']
    has_dialogue_warning = any('dialogue' in w.lower() for w in warnings2)
    
    print(f"Warnings: {warnings2}")
    print(f"Has 'No dialogue' warning: {has_dialogue_warning}")
    
    if has_dialogue_warning:
        print("✅ PASSED: Correctly detected no dialogue")
    else:
        print("❌ FAILED: Should warn about missing dialogue!")
        print("\n🔍 DEBUGGING:")
        print(f"   Full result: {result2}")
        print(f"   Warnings type: {type(warnings2)}")
        print(f"   Warnings length: {len(warnings2)}")
    
    # Test 3: Complex dialogue
    print("\nTest 3: Complex dialogue with parentheticals")
    print("-" * 40)
    result3 = validate_fountain_syntax(TEST_SCREENPLAY_COMPLEX)
    
    warnings3 = result3['warnings']
    has_dialogue_warning = any('dialogue' in w.lower() for w in warnings3)
    
    print(f"Warnings: {warnings3}")
    print(f"Has 'No dialogue' warning: {has_dialogue_warning}")
    
    if has_dialogue_warning:
        print("❌ FAILED: False positive on complex dialogue!")
    else:
        print("✅ PASSED: Correctly detected dialogue")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    test1_pass = not any('dialogue' in w.lower() for w in result1['warnings'])
    test2_pass = any('dialogue' in w.lower() for w in result2['warnings'])
    test3_pass = not any('dialogue' in w.lower() for w in result3['warnings'])
    
    total_passed = sum([test1_pass, test2_pass, test3_pass])
    
    print(f"Test 1 (Has dialogue): {'PASS ✅' if test1_pass else 'FAIL ❌'}")
    print(f"Test 2 (No dialogue): {'PASS ✅' if test2_pass else 'FAIL ❌'}")
    print(f"Test 3 (Complex dialogue): {'PASS ✅' if test3_pass else 'FAIL ❌'}")
    print(f"\nTotal: {total_passed}/3 tests passed")
    
    if total_passed == 3:
        print("\n🎉 ALL TESTS PASSED - Fix is working correctly!")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        if not test2_pass:
            print("\n💡 TIP: If Test 2 fails, the module might not be updated.")
            print("   Try:")
            print("   1. Close Python completely")
            print("   2. Delete any __pycache__ folders in phase3_screenplay/")
            print("   3. Run this test again")
        return False


if __name__ == "__main__":
    try:
        success = test_dialogue_detection()
        sys.exit(0 if success else 1)
    except ImportError as e:
        print(f"\n❌ ERROR: Could not import phase3_screenplay.utils")
        print(f"   Make sure you've updated the file with the fix!")
        print(f"   Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)