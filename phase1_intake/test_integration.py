import os
from dotenv import load_dotenv

load_dotenv()

from state import create_initial_state
from nodes.intake import intake_node
from nodes.clarification import clarification_node
from nodes.integration import integration_node
from utils import generate_session_id


def test_integration_with_mock_responses(
    user_input: str,
    mock_responses: list,
    test_name: str
):
    """
    Test INTEGRATION_NODE with pre-defined mock responses.
    
    Args:
        user_input: Original story idea
        mock_responses: List of mock user response dicts
        test_name: Name of this test case
    """
    print("\n" + "█"*70)
    print(f"TEST: {test_name}")
    print("█"*70)
    print(f"\nORIGINAL INPUT: {user_input}\n")
    
    session_id = generate_session_id()
    state = create_initial_state(user_input, session_id)
    
    state["user_responses"] = mock_responses
    state["clarification_iteration"] = 1
    
    print("MOCK USER RESPONSES:")
    print("─"*70)
    for i, resp in enumerate(mock_responses, 1):
        print(f"{i}. Q: {resp['question_text']}")
        print(f"   A: {resp['answer_full_text']}\n")
    print("─"*70)
    
    integration_updates = integration_node(state)
    state = {**state, **integration_updates}
    
    print("\n" + "="*70)
    print("BEFORE vs AFTER INTEGRATION")
    print("="*70)
    print(f"\n📌 BEFORE (Original):")
    print(f"   {user_input}\n")
    print(f"📌 AFTER (Refined):")
    print(f"   {state['user_input_refined']}\n")
    print("="*70 + "\n")
    
    return state


def run_all_tests():
    """Run all integration test cases"""
    
    print("\n" + "╔"*70)
    print("INTEGRATION_NODE TEST SUITE")
    print("╚"*70)
    
    test_integration_with_mock_responses(
        user_input="Write a story about two brothers",
        mock_responses=[
            {
                "question_id": "q1",
                "question_text": "When does the story take place?",
                "answer": "B",
                "answer_full_text": "A single pivotal year in their lives",
                "timestamp": "2025-01-18T12:00:00"
            },
            {
                "question_id": "q2",
                "question_text": "Whose perspective?",
                "answer": "B",
                "answer_full_text": "The younger brother's perspective",
                "timestamp": "2025-01-18T12:01:00"
            },
            {
                "question_id": "q3",
                "question_text": "What's the central conflict?",
                "answer": "C",
                "answer_full_text": "A family secret that challenges their bond",
                "timestamp": "2025-01-18T12:02:00"
            }
        ],
        test_name="TEST 1: Two Brothers - Standard Responses"
    )
    
    test_integration_with_mock_responses(
        user_input="Story of Napoleon and Waterloo",
        mock_responses=[
            {
                "question_id": "q1",
                "question_text": "What time period to cover?",
                "answer": "Custom answer",
                "answer_full_text": "Custom: The final week of the Hundred Days campaign, June 12-18, 1815",
                "timestamp": "2025-01-18T12:00:00"
            },
            {
                "question_id": "q2",
                "question_text": "Perspective?",
                "answer": "C",
                "answer_full_text": "Multi-perspective (Napoleon, Wellington, Blücher)",
                "timestamp": "2025-01-18T12:01:00"
            }
        ],
        test_name="TEST 2: Napoleon - With Custom Response"
    )
    
    test_integration_with_mock_responses(
        user_input="A detective story",
        mock_responses=[
            {
                "question_id": "q1",
                "question_text": "Time period?",
                "answer": "A",
                "answer_full_text": "1940s Los Angeles",
                "timestamp": "2025-01-18T12:00:00"
            },
            {
                "question_id": "q2",
                "question_text": "What case?",
                "answer": "Custom",
                "answer_full_text": "Custom: A missing person case involving a Hollywood actress",
                "timestamp": "2025-01-18T12:01:00"
            },
            {
                "question_id": "q3",
                "question_text": "Tone?",
                "answer": "A",
                "answer_full_text": "Film noir - dark, cynical, atmospheric",
                "timestamp": "2025-01-18T12:02:00"
            }
        ],
        test_name="TEST 3: Detective - Multiple Clarifications"
    )
    
    print("\n" + "╔"*70)
    print("ALL TESTS COMPLETE")
    print("╚"*70 + "\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    print("\n🚀 Starting INTEGRATION_NODE tests...\n")
    
    try:
        run_all_tests()
        print("✅ All tests completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}\n")
        import traceback
        traceback.print_exc()