import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.append('..')

from ..state import Phase1State
from ..models import IntegrationOutput
from ..utils import retry_with_exponential_backoff, save_state, format_user_responses



INTEGRATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a story development specialist integrating user clarifications.

Your job is to take a vague story idea and user's answers to clarification questions, 
then create a REFINED, ENRICHED story description that incorporates all the new information.

INTEGRATION RULES:

1. START WITH ORIGINAL IDEA
   - Keep the core concept intact
   - Don't lose any elements from the original input

2. SEAMLESSLY INTEGRATE USER RESPONSES
   - Weave in answers naturally
   - Don't just list them
   - Create a coherent narrative description

3. OUTPUT REQUIREMENTS
   - Single comprehensive paragraph (150-300 words)
   - Incorporate ALL user answers
   - Add specificity without changing intent
   - Maintain natural flow
   - Be detailed but concise

4. WHAT TO INCLUDE
   - Original concept
   - Time period/scope (from answers)
   - Protagonist clarity (from answers)
   - Conflict/stakes (from answers)
   - Genre/tone (from answers)
   - Any other clarifications provided

5. TONE
   - Professional, clear, filmable
   - Read like a compelling pitch
   - Could be handed to a screenwriter directly

Return structured JSON with:
- refined_description: The enriched story paragraph
- changes_made: List of what was added/clarified"""),
    
    ("user", """TASK: Integrate user responses into refined story description.

ORIGINAL STORY IDEA:
{original_input}

USER'S CLARIFICATIONS:
{user_responses}

Create a comprehensive, refined story description that naturally incorporates all clarifications.""")
])



def get_llm():
    """Initialize OpenAI LLM with structured output"""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.5,  # Moderate creativity for synthesis
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(IntegrationOutput)



@retry_with_exponential_backoff
def integrate_user_responses(
    original_input: str,
    user_responses: list
) -> IntegrationOutput:
    """
    Integrate user responses into refined description using LLM.
    
    Args:
        original_input: Original story idea
        user_responses: List of user answer dicts
    
    Returns:
        IntegrationOutput with refined description
    """
    llm = get_llm()
    chain = INTEGRATION_PROMPT | llm
    
    formatted_responses = format_user_responses(user_responses)
    
    result = chain.invoke({
        "original_input": original_input,
        "user_responses": formatted_responses
    })
    
    return result



def integration_node(state: Phase1State) -> Dict:
    """
    INTEGRATION_NODE: Merges user responses into refined story description.
    
    Takes original input and all user responses, creates enriched description
    that will be re-analyzed by RE_INTAKE_NODE.
    
    Args:
        state: Current Phase1State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("🔗 INTEGRATION_NODE: Merging user responses...")
    print("="*70)
    
    user_responses = state.get("user_responses", [])
    
    if not user_responses:
        print("\n⚠️  No user responses to integrate!")
        return {
            "current_step": "integration_skipped"
        }
    
    print(f"\n📝 Integrating {len(user_responses)} response(s)...")
    print(f"📄 Original: {state['user_input_raw'][:100]}...")
    
    try:
        output = integrate_user_responses(
            original_input=state["user_input_raw"],
            user_responses=user_responses
        )
        
        print("\n" + "─"*70)
        print("REFINED DESCRIPTION:")
        print("─"*70)
        print(f"\n{output.refined_description}\n")
        print("─"*70)
        
        if output.changes_made:
            print("\n✨ Changes Made:")
            for change in output.changes_made:
                print(f"  • {change}")
        
        updates = {
            "user_input_refined": output.refined_description,
            "current_step": "integration_complete"
        }
        
        updated_state = {**state, **updates}
        save_state(updated_state, "integration")
        
        print(f"\n✅ Story description refined and ready for re-analysis")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ INTEGRATION_NODE failed: {str(e)}\n")
        
        print("⚠️  Attempting fallback integration...")
        
        fallback_description = state["user_input_raw"]
        for resp in user_responses:
            fallback_description += f" {resp['answer_full_text']}."
        
        return {
            "user_input_refined": fallback_description,
            "current_step": "integration_fallback",
            "errors": [f"Integration failed, used fallback: {str(e)}"]
        }