import os
from dotenv import load_dotenv

load_dotenv()

from state import create_initial_state
from nodes.intake import intake_node
from utils import generate_session_id


def test_intake_with_input(user_input: str, test_name: str):
    """
    Test INTAKE_NODE with a specific input.
    
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
    
    updates = intake_node(state)
    
    final_state = {**state, **updates}
    
    print("\n" + "─"*70)
    print("RESULTS:")
    print("─"*70)
    print(f"Clarity Score: {final_state['clarity_score']}/100")
    print(f"Is Complete: {final_state['is_complete']}")
    print(f"Classification: {final_state['classification']}")
    print(f"Research Required: {final_state['research_required']}")
    print(f"Missing Elements: {final_state['missing_elements']}")
    print(f"Detected Elements: {final_state['detected_elements']}")
    print("─"*70 + "\n")
    
    return final_state


def run_all_tests():
    """Run all test cases"""
    
    print("\n" + "╔"*70)
    print("INTAKE_NODE TEST SUITE")
    print("╚"*70)
    
    test_intake_with_input(
        user_input="Write a story about two brothers",
        test_name="TEST 1: Very Vague Input"
    )
    
    test_intake_with_input(
        user_input="The story of Napoleon and his final battle of Waterloo",
        test_name="TEST 2: Historical Event (Moderate Specificity)"
    )
    
    test_intake_with_input(
        user_input="""A 25-minute multi-perspective historical war epic following 
        Napoleon Bonaparte during the final week of the Hundred Days campaign 
        (June 12-18, 1815), culminating in the Battle of Waterloo. Story follows 
        Napoleon (40% screen time), Duke of Wellington, and Marshal Blücher as 
        they make strategic decisions leading to the decisive battle. Historically 
        grounded with dramatized dialogue, hybrid epic visual style balancing 
        spectacle and intimate character moments.""",
        test_name="TEST 3: Highly Specific Input"
    )
    
    test_intake_with_input(
        user_input="""A small girl and her dog Tommy, where Tommy can speak to 
        other dogs. Dogs and cats are rival teams fighting a territorial war over 
        the neighborhood. The cats build mind-control helmets to enslave humans, 
        and the dogs must destroy the machine over a week-long escalating conflict. 
        The girl doesn't know animals can talk.""",
        test_name="TEST 4: Fictional with Clear Scope"
    )
    
    test_intake_with_input(
        user_input="A story about a rescue mission in a cave",
        test_name="TEST 5: Ambiguous Input"
    )
    
    print("\n" + "╔"*70)
    print("ALL TESTS COMPLETE")
    print("╚"*70 + "\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("   Please create a .env file with your OpenAI API key")
        exit(1)
    
    print("\n🚀 Starting INTAKE_NODE tests...\n")
    
    try:
        run_all_tests()
        print("✅ All tests completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}\n")
        import traceback
        traceback.print_exc()