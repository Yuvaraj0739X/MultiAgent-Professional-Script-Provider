from typing import Dict

import sys
sys.path.append('..')

from ..state import Phase1State
from .intake import intake_node



def re_intake_node(state: Phase1State) -> Dict:
    """
    RE_INTAKE_NODE: Re-analyzes story after integrating user responses.
    
    This is the loop-back point in the workflow. After collecting user
    responses and integrating them, we re-analyze to see if the story
    is now complete or needs more clarification.
    
    Args:
        state: Current Phase1State (with refined input)
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("🔄 RE_INTAKE_NODE: Re-analyzing refined story...")
    print("="*70)
    
    current_iteration = state.get("clarification_iteration", 0)
    print(f"\n📊 Clarification iteration: {current_iteration}/5")
    print(f"📝 Analyzing refined description...\n")
    
    intake_updates = intake_node(state)
    
    updates = {
        **intake_updates,
        "current_step": "re_intake_complete"
    }
    
    new_clarity = updates.get("clarity_score", state.get("clarity_score", 0))
    is_complete = updates.get("is_complete", False)
    
    print("\n" + "─"*70)
    print("RE-ANALYSIS RESULTS:")
    print("─"*70)
    print(f"Clarity Score: {new_clarity}/100")
    print(f"Is Complete: {is_complete}")
    
    if is_complete:
        print("\n✅ Story is now sufficiently detailed!")
        print("▶️  Proceeding to final summary generation...")
    elif current_iteration >= 5:
        print("\n⚠️  Maximum iterations reached (5/5)")
        print("▶️  Proceeding to summary with current information...")
    else:
        missing = updates.get("missing_elements", [])
        print(f"\n⚠️  Still needs clarification")
        print(f"Missing: {', '.join(missing[:3])}")
        if len(missing) > 3:
            print(f"... and {len(missing) - 3} more")
        print(f"▶️  Generating more questions (iteration {current_iteration + 1}/5)...")
    
    print("─"*70 + "\n")
    
    return updates