import json
import time
import os
from pathlib import Path
from typing import Callable, TypeVar, Any
from datetime import datetime
from functools import wraps

from .state import Phase1State

T = TypeVar('T')



def retry_with_exponential_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0
) -> Callable[..., T]:
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential backoff
        max_delay: Maximum delay between retries
    
    Returns:
        Wrapped function with retry logic
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    print(f"❌ Failed after {max_retries} retries: {str(e)}")
                    raise
                
                print(f"⚠️  Attempt {attempt + 1} failed: {str(e)}")
                print(f"   Retrying in {delay:.1f} seconds...")
                
                time.sleep(delay)
                delay = min(delay * exponential_base, max_delay)
        
        raise last_exception
    
    return wrapper



def get_checkpoint_dir() -> Path:
    """Get or create checkpoint directory"""
    checkpoint_dir = Path("checkpoints")
    checkpoint_dir.mkdir(exist_ok=True)
    return checkpoint_dir


def save_state(state: Phase1State, node_name: str) -> str:
    """
    Save state to JSON file after each node execution.
    
    Args:
        state: Current state object
        node_name: Name of node that just executed
    
    Returns:
        Path to saved checkpoint file
    """
    checkpoint_dir = get_checkpoint_dir()
    session_id = state["session_id"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"{session_id}_{node_name}_{timestamp}.json"
    filepath = checkpoint_dir / filename
    
    state_dict = dict(state)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(state_dict, f, indent=2, ensure_ascii=False)
    
    print(f"💾 State saved: {filepath}")
    return str(filepath)


def load_latest_checkpoint(session_id: str) -> Phase1State:
    """
    Load the most recent checkpoint for a session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Loaded state object
    
    Raises:
        FileNotFoundError: If no checkpoint exists
    """
    checkpoint_dir = get_checkpoint_dir()
    
    checkpoints = list(checkpoint_dir.glob(f"{session_id}_*.json"))
    
    if not checkpoints:
        raise FileNotFoundError(f"No checkpoints found for session: {session_id}")
    
    latest = max(checkpoints, key=os.path.getctime)
    
    with open(latest, 'r', encoding='utf-8') as f:
        state_dict = json.load(f)
    
    print(f"📂 Loaded checkpoint: {latest}")
    return Phase1State(**state_dict)


def list_checkpoints(session_id: str) -> list:
    """
    List all checkpoints for a session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        List of checkpoint file paths
    """
    checkpoint_dir = get_checkpoint_dir()
    checkpoints = list(checkpoint_dir.glob(f"{session_id}_*.json"))
    return sorted(checkpoints, key=os.path.getctime)



def display_analysis(analysis: Any) -> None:
    """
    Pretty-print intake analysis results.
    
    Args:
        analysis: IntakeAnalysisOutput object
    """
    print("\n" + "="*70)
    print("📊 INTAKE ANALYSIS")
    print("="*70)
    print(f"\n🎯 Clarity Score: {analysis.clarity_score}/100")
    print(f"✅ Complete: {analysis.is_complete}")
    print(f"🏷️  Classification: {analysis.classification}")
    print(f"🔍 Research Required: {analysis.research_required}")
    
    if analysis.detected_elements:
        print(f"\n✓ Detected Elements:")
        for elem in analysis.detected_elements:
            print(f"  • {elem.key}: {elem.value}")
    
    if analysis.missing_elements:
        print(f"\n✗ Missing Elements:")
        for elem in analysis.missing_elements:
            print(f"  • {elem}")
    
    if analysis.ambiguities:
        print(f"\n⚠️  Ambiguities:")
        for amb in analysis.ambiguities:
            print(f"  • {amb}")
    
    print(f"\n💭 Reasoning: {analysis.reasoning}")
    print("="*70 + "\n")


def display_questions(questions: list) -> None:
    """
    Display clarification questions in readable format.
    
    Args:
        questions: List of ClarificationQuestion objects
    """
    print("\n" + "="*70)
    print("❓ CLARIFICATION NEEDED")
    print("="*70)
    
    for i, q in enumerate(questions, 1):
        print(f"\n{'─'*70}")
        print(f"QUESTION {i} of {len(questions)} [{q.priority.upper()} PRIORITY]")
        print(f"{'─'*70}")
        print(f"\n{q.question_text}\n")
        
        if q.question_type == "multiple_choice" and q.options:
            for opt in q.options:
                print(f"  {opt.label}) {opt.text}")
        elif q.question_type == "binary":
            print("  A) Yes")
            print("  B) No")
        else:
            print("  (Open-ended response)")
        
        print(f"\n💡 {q.context}")
    
    print("\n" + "="*70 + "\n")


def display_final_brief(brief: str) -> None:
    """
    Display final story brief.
    
    Args:
        brief: Markdown formatted story brief
    """
    print("\n" + "="*70)
    print("📋 FINAL STORY BRIEF")
    print("="*70 + "\n")
    print(brief)
    print("\n" + "="*70 + "\n")



def format_user_responses(responses: list) -> str:
    """
    Format user responses for prompt inclusion.
    
    Args:
        responses: List of user response dicts
    
    Returns:
        Formatted string of Q&A pairs
    """
    if not responses:
        return "No previous responses."
    
    formatted = []
    for i, resp in enumerate(responses, 1):
        formatted.append(f"{i}. Q: {resp['question_text']}")
        formatted.append(f"   A: {resp['answer']}")
    
    return "\n".join(formatted)


def generate_session_id() -> str:
    """
    Generate unique session identifier.
    
    Returns:
        Session ID string
    """
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"



def validate_user_answer(answer: str, question: Any) -> bool:
    """
    Validate user's answer matches question type.
    
    Args:
        answer: User's input
        question: ClarificationQuestion object
    
    Returns:
        True if valid, False otherwise
    """
    if question.question_type == "multiple_choice":
        if not question.options:
            return True
        valid_labels = [opt.label for opt in question.options]
        return answer.upper() in valid_labels
    
    elif question.question_type == "binary":
        return answer.upper() in ['A', 'B', 'YES', 'NO']
    
    else:  # open_ended
        return len(answer.strip()) > 0


def sanitize_input(text: str) -> str:
    """
    Sanitize user input.
    
    Args:
        text: Raw input text
    
    Returns:
        Cleaned text
    """
    return text.strip()