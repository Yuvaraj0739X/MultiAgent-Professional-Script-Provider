import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.append('..')

from ..state import Phase1State
from ..models import ClarificationOutput
from ..utils import retry_with_exponential_backoff, save_state, display_questions



CLARIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a film development consultant specializing in story clarification.

Your job is to generate TARGETED, SPECIFIC questions that help refine vague story ideas into filmable concepts.

QUESTION GENERATION RULES:

1. MAXIMUM 3 QUESTIONS PER ITERATION
   - Never overwhelm the user
   - Prioritize the most critical gaps

2. PRIORITIZATION (ask in this order):
   HIGH PRIORITY (always ask if missing):
   - temporal_boundaries: When does story start/end?
   - protagonist_clarity: Whose story is this?
   - central_conflict: What's the problem/stakes?
   
   MEDIUM PRIORITY (ask if high priority covered):
   - tone_genre: What kind of story?
   - scope_definition: What's the focus within timeframe?
   - perspective: Whose viewpoint?
   
   LOW PRIORITY (ask only if necessary):
   - setting: Where does it take place?
   - emotional_arc: Character journey?

3. QUESTION TYPES:
   - PREFER: multiple_choice (gives user concrete options)
   - USE: binary (for yes/no decisions)
   - AVOID: open_ended (unless necessary)

4. QUESTION QUALITY:
   - Be SPECIFIC with examples in options
   - Show the user options they haven't considered
   - Include context explaining why it matters
   - Make options distinct and clear

5. PROGRESSIVE DISCLOSURE:
   - Start with broadest questions first
   - Get more specific in later iterations
   - Build on previous answers (if any)

CURRENT ITERATION CONTEXT:
You will be told which iteration this is (1-5). Early iterations should ask broader questions.
Later iterations can be more specific.

Return a structured JSON matching ClarificationOutput schema."""),
    
    ("user", """TASK: Generate clarification questions for this story idea.

STORY IDEA: {user_input}

CURRENT CLARITY SCORE: {clarity_score}/100
CLASSIFICATION: {classification}

MISSING ELEMENTS: {missing_elements}

AMBIGUITIES: {ambiguities}

ITERATION NUMBER: {iteration_number} of 5

PREVIOUS QUESTIONS ASKED:
{previous_questions}

Generate 1-3 targeted questions to fill the most critical gaps.
Focus on what's MOST important for making this filmable.""")
])



def get_llm():
    """Initialize OpenAI LLM with structured output"""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.4,  # Slightly higher for creative question generation
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(ClarificationOutput)



@retry_with_exponential_backoff
def generate_clarification_questions(
    user_input: str,
    clarity_score: int,
    classification: str,
    missing_elements: list,
    ambiguities: list,
    iteration_number: int,
    previous_questions: list
) -> ClarificationOutput:
    """
    Generate clarification questions using LLM.
    
    Args:
        user_input: Current story description
        clarity_score: Current clarity score
        classification: Story classification
        missing_elements: List of missing elements
        ambiguities: List of ambiguous aspects
        iteration_number: Current iteration (1-5)
        previous_questions: History of questions already asked
    
    Returns:
        ClarificationOutput with 1-3 questions
    """
    llm = get_llm()
    chain = CLARIFICATION_PROMPT | llm
    
    prev_q_text = "None (first iteration)"
    if previous_questions:
        prev_q_text = "\n".join([
            f"- {q.get('question_text', 'Unknown question')}"
            for q in previous_questions
        ])
    
    result = chain.invoke({
        "user_input": user_input,
        "clarity_score": clarity_score,
        "classification": classification,
        "missing_elements": ", ".join(missing_elements) if missing_elements else "None",
        "ambiguities": ", ".join(ambiguities) if ambiguities else "None",
        "iteration_number": iteration_number,
        "previous_questions": prev_q_text
    })
    
    return result



def clarification_node(state: Phase1State) -> Dict:
    """
    CLARIFICATION_NODE: Generates targeted questions to fill gaps.
    
    Called when story idea is incomplete and needs more information.
    
    Args:
        state: Current Phase1State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("❓ CLARIFICATION_NODE: Generating questions...")
    print("="*70)
    
    current_iteration = state.get("clarification_iteration", 0) + 1
    
    print(f"\n📊 Iteration: {current_iteration}/5")
    print(f"📉 Current clarity: {state['clarity_score']}/100")
    print(f"❌ Missing: {', '.join(state['missing_elements'][:3])}")
    if len(state['missing_elements']) > 3:
        print(f"   ... and {len(state['missing_elements']) - 3} more")
    
    try:
        output = generate_clarification_questions(
            user_input=state["user_input_refined"],
            clarity_score=state["clarity_score"],
            classification=state["classification"],
            missing_elements=state["missing_elements"],
            ambiguities=state["ambiguities"],
            iteration_number=current_iteration,
            previous_questions=state.get("questions_asked", [])
        )
        
        display_questions(output.questions)
        
        questions_dict = [
            {
                "id": q.id,
                "iteration": current_iteration,
                "priority": q.priority,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": [{"label": opt.label, "text": opt.text} for opt in q.options] if q.options else None,
                "context": q.context,
                "user_response": None  # Will be filled by HUMAN_INPUT_NODE
            }
            for q in output.questions
        ]
        
        updates = {
            "current_questions": questions_dict,
            "clarification_iteration": current_iteration,
            "pending_user_response": True,
            "current_step": "clarification_complete"
        }
        
        updated_state = {**state, **updates}
        save_state(updated_state, "clarification")
        
        print(f"\n✅ Generated {len(questions_dict)} question(s)")
        print("⏸️  Workflow paused - waiting for user input...")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ CLARIFICATION_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "clarification_failed",
            "errors": [f"Question generation failed: {str(e)}"]
        }