import os
import sys
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import state as phase2_state
import nodes.research_strategy as research_strategy
import nodes.wikipedia_fetch as wikipedia_fetch


def test_research_and_fetch():
    """Test research strategy and Wikipedia fetch together"""
    
    print("\n" + "╔"*70)
    print("PHASE 2: RESEARCH STRATEGY & WIKIPEDIA FETCH TEST")
    print("╚"*70)
    
    mock_phase1_output = {
        "final_brief": """
# WATERLOO: THE FINAL GAMBLE

## LOGLINE
In June 1815, Napoleon Bonaparte wages a desperate final campaign across 
Belgium, facing the combined forces of Wellington and Blücher in a 
multi-perspective war epic culminating in the Battle of Waterloo.

## CLASSIFICATION & METADATA
- Type: real
- Research Required: yes
- Genre: Historical War Epic
- Target Runtime: 25-30 minutes

The story follows Napoleon Bonaparte during the final week of the Hundred 
Days campaign (June 12-18, 1815), alongside the Duke of Wellington and 
Marshal Blücher as they make strategic decisions leading to the decisive 
Battle of Waterloo.
        """,
        "classification": "real",
        "research_required": True,
        "detected_elements": {
            "protagonist": "Napoleon Bonaparte",
            "time_period": "June 1815",
            "event": "Battle of Waterloo",
            "genre": "historical war"
        },
        "user_input_refined": "Story of Napoleon and final Battle of Waterloo",
        "session_id": "test_session_001"
    }
    
    initial_state = phase2_state.create_phase2_initial_state(
        phase1_output=mock_phase1_output,
        session_id="test_session_001"
    )
    
    print("\n" + "┏"*70)
    print("TEST 1: RESEARCH_STRATEGY_NODE")
    print("┗"*70)
    
    strategy_updates = research_strategy.research_strategy_node(initial_state)
    state = {**initial_state, **strategy_updates}
    
    if state.get("current_step") == "research_strategy_failed":
        print("\n❌ Research strategy failed!")
        return
    
    print(f"\n✅ Generated {len(state['research_queries'])} queries")
    
    print("\n" + "┏"*70)
    print("TEST 2: WIKIPEDIA_FETCH_NODE")
    print("┗"*70)
    
    input("\nPress ENTER to fetch Wikipedia articles (this will take ~30 seconds)...\n")
    
    fetch_updates = wikipedia_fetch.wikipedia_fetch_node(state)
    state = {**state, **fetch_updates}
    
    if state.get("current_step") == "wikipedia_fetch_failed":
        print("\n❌ Wikipedia fetch failed!")
        return
    
    print("\n" + "╔"*70)
    print("FINAL RESULTS")
    print("╚"*70)
    
    print(f"\n📊 Research Strategy:")
    print(f"   • Queries generated: {len(state['research_queries'])}")
    print(f"   • Strategy: {state.get('query_strategy', 'N/A')[:100]}...")
    
    print(f"\n📚 Wikipedia Fetch:")
    print(f"   • Articles fetched: {state['fetch_success_count']}")
    print(f"   • Failed queries: {len(state['fetch_failed_queries'])}")
    
    if state.get("wikipedia_articles"):
        print(f"\n📖 Sample Articles:")
        for article in state["wikipedia_articles"][:3]:
            print(f"\n   Title: {article['title']}")
            print(f"   Source Query: {article.get('source_query', 'N/A')}")
            print(f"   Summary: {article['summary'][:200]}...")
    
    print("\n" + "╔"*70)
    print("TEST COMPLETE")
    print("╚"*70 + "\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        sys.exit(1)
    
    try:
        test_research_and_fetch()
        print("✅ All tests passed!\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}\n")
        import traceback
        traceback.print_exc()