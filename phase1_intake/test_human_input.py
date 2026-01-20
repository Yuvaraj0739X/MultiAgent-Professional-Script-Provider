import os
from dotenv import load_dotenv

load_dotenv()

from state import create_initial_state
from nodes.intake import intake_node
from nodes.clarification import clarification_node
from nodes.human_input import human_input_node
from utils import generate_session_id


def test_full_flow_with_human_input(user_input: str, test_name: str):
    """
    Test complete flow: INTAKE → CLARIFICATION → HUMAN_INPUT
    
    Args:
        user_input: Story idea to test
        test_name: Name of this test case
    """
    print("\n" + "█"*70)
    print(f"TEST: {test_name}")
    print("█"*70)
    print(f"\nSTARTING INPUT: {user_input}\n")
    
    session_id = generate_session_id()
    state = create_initial_state(user_input, session_id)
    
    print("\n" + "┏"*70)
    print("STEP 1: INTAKE_NODE")
    print("┗"*70)
    
    intake_updates = intake_node(state)
    state = {**state, **intake_updates}
    
    if state["is_complete"]:
        print("\n✅ Story is complete - no clarification needed!")
        return state
    
    print("\n" + "┏"*70)
    print("STEP 2: CLARIFICATION_NODE")
    print("┗"*70)
    
    clarification_updates = clarification_node(state)
    state = {**state, **clarification_updates}
    
    print("\n" + "┏"*70)
    print("STEP 3: HUMAN_INPUT_NODE (INTERACTIVE)")
    print("┗"*70)
    
    input("\nPress ENTER when ready to answer questions...\n")
    
    human_input_updates = human_input_node(state)
    state = {**state, **human_input_updates}
    
    print("\n" + "─"*70)
    print("FINAL STATE AFTER HUMAN INPUT:")
    print("─"*70)
    
    print(f"\n✓ Questions answered: {len(state.get('user_responses', []))}")
    print(f"✓ Iteration: {state['clarification_iteration']}/5")
    print(f"✓ Pending response: {state['pending_user_response']}")
    
    if state.get('user_responses'):
        print(f"\n📝 YOUR RESPONSES:")
        for i, resp in enumerate(state['user_responses'], 1):
            print(f"\n{i}. Q: {resp['question_text']}")
            print(f"   A: {resp['answer_full_text']}")
    
    print("\n" + "─"*70 + "\n")
    
    return state


def run_interactive_test():
    """
    Run a single interactive test.
    User will be prompted to answer questions.
    """
    
    print("\n" + "╔"*70)
    print("HUMAN_INPUT_NODE INTERACTIVE TEST")
    print("╚"*70)
    
    print("\n📌 This test will ask you to answer clarification questions.")
    print("📌 Answer each question by typing the letter (A, B, C, etc.)")
    print("📌 Press Ctrl+C at any time to cancel.\n")
    
    input("Press ENTER to start the test...\n")
    
    test_full_flow_with_human_input(
        user_input="Write a story about two brothers",
        test_name="Interactive Test - Two Brothers Story"
    )
    
    print("\n" + "╔"*70)
    print("TEST COMPLETE")
    print("╚"*70 + "\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    print("\n🚀 Starting HUMAN_INPUT_NODE interactive test...\n")
    
    try:
        run_interactive_test()
        print("✅ Interactive test completed successfully!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user.\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()