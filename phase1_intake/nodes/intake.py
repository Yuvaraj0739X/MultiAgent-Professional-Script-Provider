import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import get_llm_config

from ..state import Phase1State
from ..models import IntakeAnalysisOutput
from ..utils import retry_with_exponential_backoff, save_state, display_analysis



INTAKE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a professional film development analyst specializing in story intake and evaluation.

Your job is to analyze story ideas for completeness, clarity, and filmability.

EVALUATION CRITERIA:

1. SPECIFICITY (0-100 scale):
   - 0-30: Extremely vague ("write a story")
   - 31-60: Core idea present but missing details
   - 61-85: Most elements defined, minor gaps
   - 86-100: Fully detailed, ready for production

2. MISSING ELEMENTS TO CHECK:
   - temporal_boundaries: Start/end timeframe defined?
   - protagonist_clarity: Whose story is this?
   - central_conflict: What's the problem/stakes?
   - tone_genre: What kind of story (drama, comedy, etc.)?
   - setting: Where does it take place?
   - perspective: POV or narrative approach?
   - scope_definition: Is scope manageable for short film?
   - emotional_arc: What's the character/audience journey?

3. DETECTED ELEMENTS:
   Identify what IS present (genre hints, characters mentioned, settings, time periods, etc.)

4. AMBIGUITIES:
   What aspects could be interpreted multiple ways?

5. CLASSIFICATION:
   - "real": References real people, events, documented history
   - "fictional": Imaginary characters and scenarios
   - "mixed": Real person in fictional scenario, or vice versa

6. RESEARCH REQUIRED:
   True if story references verifiable real events/people

COMPLETION THRESHOLD:
- is_complete = true ONLY if clarity_score >= 70 AND all critical elements present
- Critical elements: temporal_boundaries, protagonist_clarity, central_conflict

Be STRICT in your evaluation. Better to ask for clarification than assume.

Return your analysis as a structured JSON object matching the IntakeAnalysisOutput schema."""),
    
    ("user", """Analyze this story idea for a short film (15-30 minutes):

STORY IDEA: {user_input}

Provide a thorough analysis.""")
])



def get_llm():
    """Initialize OpenAI LLM with structured output"""
    config = get_llm_config("phase1", "intake")
    return ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(IntakeAnalysisOutput)


@retry_with_exponential_backoff
def analyze_story_input(user_input: str) -> IntakeAnalysisOutput:
    """
    Analyze user's story input using LLM.
    
    Args:
        user_input: User's story idea (raw or refined)
    
    Returns:
        IntakeAnalysisOutput with analysis results
    
    Raises:
        Exception: If LLM call fails after retries
    """
    llm = get_llm()
    chain = INTAKE_ANALYSIS_PROMPT | llm
    
    result = chain.invoke({"user_input": user_input})
    
    return result



def intake_node(state: Phase1State) -> Dict:
    """
    INTAKE_NODE: Analyzes user input for completeness.
    
    This is the entry point of Phase 1 workflow.
    Can also be called during RE_INTAKE after user responses.
    
    Args:
        state: Current Phase1State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("🔍 INTAKE_NODE: Analyzing story input...")
    print("="*70)
    
    input_to_analyze = state.get("user_input_refined") or state["user_input_raw"]
    
    print(f"\n📝 Input being analyzed:")
    print(f"   {input_to_analyze[:200]}{'...' if len(input_to_analyze) > 200 else ''}\n")
    
    try:
        analysis = analyze_story_input(input_to_analyze)
        
        display_analysis(analysis)
        
        detected_elements_dict = {
            elem.key: elem.value 
            for elem in analysis.detected_elements
        }
        
        updates = {
            "clarity_score": analysis.clarity_score,
            "is_complete": analysis.is_complete,
            "missing_elements": analysis.missing_elements,
            "detected_elements": detected_elements_dict,
            "ambiguities": analysis.ambiguities,
            "classification": analysis.classification,
            "research_required": analysis.research_required,
            "current_step": "intake_complete"
        }
        
        updated_state = {**state, **updates}
        save_state(updated_state, "intake")
        
        if analysis.is_complete:
            print("✅ Story idea is sufficiently detailed. Proceeding to summary.")
        else:
            print(f"⚠️  Story needs clarification (score: {analysis.clarity_score}/100)")
            print(f"   Missing: {', '.join(analysis.missing_elements[:3])}")
            if len(analysis.missing_elements) > 3:
                print(f"   ... and {len(analysis.missing_elements) - 3} more")
        
        print("\n" + "="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ INTAKE_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "intake_failed",
            "errors": [f"Intake analysis failed: {str(e)}"]
        }