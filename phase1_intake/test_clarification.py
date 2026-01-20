import os
from dotenv import load_dotenv

load_dotenv()

from state import create_initial_state
from nodes.intake import intake_node
from nodes.clarification import clarification_node
from utils import generate_session_id


def test_full_intake_to_clarification(user_input: str, test_name: str):
    """
    Test complete flow: INTAKE → CLARIFICATION
    
    Args:
        user_input: Story idea to test
        test_name: Name of this test case
    """
    print("\n" + "█"*70)
    print(f"TEST: {test_name}")
    print("█"*70)
    print(f"\nINPUT: {user_input}\n")
    
    session_id = generate_session_id()
    state = create_initial_state(user_input, session_id)
    
    print("\n" + "─"*70)
    print("STEP 1: Running INTAKE_NODE")
    print("─"*70)
    
    intake_updates = intake_node(state)
    state = {**state, **intake_updates}
    
    if state["is_complete"]:
        print("\n✅ Story is complete - no clarification needed!")
        return state
    
    print("\n" + "─"*70)
    print("STEP 2: Running CLARIFICATION_NODE")
    print("─"*70)
    
    clarification_updates = clarification_node(state)
    state = {**state, **clarification_updates}
    
    print("\n" + "─"*70)
    print("GENERATED QUESTIONS:")
    print("─"*70)
    
    for i, q in enumerate(state["current_questions"], 1):
        print(f"\n{i}. [{q['priority'].upper()}] {q['question_text']}")
        print(f"   Type: {q['question_type']}")
        if q['options']:
            print(f"   Options: {len(q['options'])} choices")
    
    print("\n" + "─"*70)
    print(f"Iteration: {state['clarification_iteration']}/5")
    print(f"Pending response: {state['pending_user_response']}")
    print("─"*70 + "\n")
    
    return state


def run_all_tests():
    """Run all clarification test cases"""
    
    print("\n" + "╔"*70)
    print("CLARIFICATION_NODE TEST SUITE")
    print("╚"*70)
    
    test_full_intake_to_clarification(
        user_input="Write a story about two brothers",
        test_name="TEST 1: Very Vague - Expect Broad Questions"
    )
    
    test_full_intake_to_clarification(
        user_input="The story of Napoleon and his final battle of Waterloo",
        test_name="TEST 2: Historical Event - Expect Scope Questions"
    )
    
    test_full_intake_to_clarification(
        user_input="A rescue mission in a cave",
        test_name="TEST 3: Ambiguous - Expect Classification Questions"
    )
    
    test_full_intake_to_clarification(
        user_input="A detective in 1940s Los Angeles",
        test_name="TEST 4: Missing Conflict - Expect Problem/Stakes Questions"
    )
    
    print("\n" + "╔"*70)
    print("ALL TESTS COMPLETE")
    print("╚"*70 + "\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    print("\n🚀 Starting CLARIFICATION_NODE tests...\n")
    
    try:
        run_all_tests()
        print("✅ All tests completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}\n")
        import traceback
        traceback.print_exc()