import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.append('..')

from ..state import Phase1State
from ..utils import retry_with_exponential_backoff, save_state, display_final_brief, format_user_responses



SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a professional film treatment writer creating comprehensive story briefs.

Your job is to generate a COMPLETE, PRODUCTION-READY story brief that can be handed 
directly to a screenwriting team.

STORY BRIEF FORMAT (use markdown):

# [WORKING TITLE]

## LOGLINE
[One compelling sentence that captures the essence]

## CLASSIFICATION & METADATA
- **Type:** [real/fictional/mixed]
- **Research Required:** [yes/no]
- **Genre:** [primary genre + sub-genre]
- **Tone:** [describe the emotional/stylistic approach]
- **Target Runtime:** [15-30 minutes for short film]

## SYNOPSIS
[2-3 paragraph overview of the complete story]

## TIMELINE STRUCTURE
[How the story unfolds - chronological, flashbacks, compressed time, etc.]

## CHARACTERS
### [Character Name - Role]
- **Age/Description:** 
- **Personality:** 
- **Arc:** [transformation or journey]
- **Key Relationships:**

[Repeat for all main characters - minimum 2, maximum 6]

## SETTING
- **Time Period:**
- **Location(s):**
- **Atmosphere:**
- **Visual Style:**

## VISUAL APPROACH
- **Cinematography:**
- **Color Palette:**
- **Key Visual Motifs:**

## THEMES
- **Primary Theme:**
- **Secondary Themes:**
- **Emotional Core:**

## KEY DRAMATIC MOMENTS
[5-8 critical beats that define the story structure]

1. **[Beat Name]:** Description
2. **[Beat Name]:** Description
[etc.]

## PRODUCTION NOTES
- **Scale:** [intimate/medium/epic]
- **Comparable Films:** [reference 2-3 similar works]

---

REQUIREMENTS:
- Be specific and detailed
- Every section must be filled
- Use concrete language
- Make it production-ready
- Total length: 800-1500 words

TONE: Professional, clear, inspiring"""),
    
    ("user", """Generate a comprehensive story brief for the following:

FINAL REFINED STORY DESCRIPTION:
{refined_description}

CLASSIFICATION: {classification}
RESEARCH REQUIRED: {research_required}

DETECTED ELEMENTS:
{detected_elements}

USER'S CLARIFICATIONS (for context):
{user_clarifications}

Create a complete, professional story brief following the template.""")
])



def get_llm():
    """Initialize OpenAI LLM for summary generation"""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.6,  # Creative but controlled
        api_key=os.getenv("OPENAI_API_KEY")
    )



@retry_with_exponential_backoff
def generate_story_brief(
    refined_description: str,
    classification: str,
    research_required: bool,
    detected_elements: dict,
    user_responses: list
) -> str:
    """
    Generate comprehensive story brief using LLM.
    
    Args:
        refined_description: Final refined story description
        classification: Story type (real/fictional/mixed)
        research_required: Whether research is needed
        detected_elements: Elements detected in analysis
        user_responses: All user clarifications
    
    Returns:
        Complete story brief as markdown string
    """
    llm = get_llm()
    chain = SUMMARY_PROMPT | llm
    
    elements_text = "\n".join([f"- {k}: {v}" for k, v in detected_elements.items()])
    if not elements_text:
        elements_text = "None explicitly detected"
    
    clarifications_text = format_user_responses(user_responses)
    if not clarifications_text or clarifications_text == "No previous responses.":
        clarifications_text = "No additional clarifications needed (story was sufficiently detailed)"
    
    result = chain.invoke({
        "refined_description": refined_description,
        "classification": classification,
        "research_required": "Yes" if research_required else "No",
        "detected_elements": elements_text,
        "user_clarifications": clarifications_text
    })
    
    if hasattr(result, 'content'):
        return result.content
    return str(result)



def summary_node(state: Phase1State) -> Dict:
    """
    SUMMARY_NODE: Generates final comprehensive story brief.
    
    This is the terminal node of Phase 1 workflow. It synthesizes
    all information gathered and produces a production-ready brief.
    
    Args:
        state: Current Phase1State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("📋 SUMMARY_NODE: Generating final story brief...")
    print("="*70)
    
    print(f"\n📊 Final clarity score: {state.get('clarity_score', 0)}/100")
    print(f"🔄 Total iterations: {state.get('clarification_iteration', 0)}")
    print(f"💬 Total responses collected: {len(state.get('user_responses', []))}")
    
    try:
        print("\n🤖 Generating comprehensive brief (this may take 10-20 seconds)...\n")
        
        brief = generate_story_brief(
            refined_description=state.get("user_input_refined", state["user_input_raw"]),
            classification=state.get("classification", "unknown"),
            research_required=state.get("research_required", False),
            detected_elements=state.get("detected_elements", {}),
            user_responses=state.get("user_responses", [])
        )
        
        display_final_brief(brief)
        
        word_count = len(brief.split())
        
        metadata = {
            "word_count": word_count,
            "clarity_score": state.get("clarity_score", 0),
            "iterations": state.get("clarification_iteration", 0),
            "classification": state.get("classification", "unknown"),
            "research_required": state.get("research_required", False)
        }
        
        updates = {
            "final_brief": brief,
            "brief_metadata": metadata,
            "workflow_complete": True,
            "current_step": "summary_complete"
        }
        
        updated_state = {**state, **updates}
        save_state(updated_state, "summary_FINAL")
        
        print("\n" + "="*70)
        print("✅ PHASE 1 COMPLETE!")
        print("="*70)
        print(f"\n📄 Brief generated: {word_count} words")
        print(f"📁 Saved to: checkpoints/")
        print(f"🎯 Classification: {metadata['classification']}")
        print(f"🔍 Research needed: {metadata['research_required']}")
        print("\n" + "="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ SUMMARY_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "summary_failed",
            "errors": [f"Summary generation failed: {str(e)}"],
            "workflow_complete": True  # Mark as complete even if failed
        }