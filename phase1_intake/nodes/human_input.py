from typing import Dict
from datetime import datetime

import sys
sys.path.append('..')

from ..state import Phase1State
from ..utils import save_state, validate_user_answer, sanitize_input



def collect_user_responses_cli(questions: list) -> list:
    """
    Collect user responses via command-line interface.
    
    Args:
        questions: List of question dicts from current_questions
    
    Returns:
        List of response dicts
    """
    responses = []
    
    print("\n" + "="*70)
    print("⌨️  PLEASE ANSWER THE FOLLOWING QUESTIONS")
    print("="*70 + "\n")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─'*70}")
        print(f"QUESTION {i} of {len(questions)}")
        print(f"{'─'*70}\n")
        print(f"{question['question_text']}\n")
        
        if question['question_type'] == 'multiple_choice' and question['options']:
            for opt in question['options']:
                print(f"  {opt['label']}) {opt['text']}")
            print(f"  OTHER) Provide your own answer")
            print()
        elif question['question_type'] == 'binary':
            print("  A) Yes")
            print("  B) No")
            print(f"  OTHER) Provide your own answer\n")
        
        if question.get('context'):
            print(f"💡 {question['context']}\n")
        
        answer = None
        attempts = 0
        max_attempts = 3
        
        while answer is None and attempts < max_attempts:
            try:
                user_input = input(f"Your answer: ").strip()
                
                if not user_input:
                    print("⚠️  Please provide an answer.\n")
                    attempts += 1
                    continue
                
                if question['question_type'] == 'multiple_choice':
                    if user_input.upper() == 'OTHER':
                        print("\n💭 Please provide your own answer:")
                        custom_answer = input("Your answer: ").strip()
                        if len(custom_answer) < 3:
                            print("⚠️  Please provide a more detailed answer.\n")
                            attempts += 1
                            continue
                        answer = custom_answer
                        selected_option_text = f"Custom: {custom_answer}"
                        break  # Exit validation loop
                    
                    valid_labels = [opt['label'].upper() for opt in question['options']]
                    if user_input.upper() not in valid_labels:
                        print(f"⚠️  Please choose one of: {', '.join(valid_labels)}, or type 'OTHER'\n")
                        attempts += 1
                        continue
                    answer = user_input.upper()
                
                elif question['question_type'] == 'binary':
                    if user_input.upper() == 'OTHER':
                        print("\n💭 Please provide your own answer:")
                        custom_answer = input("Your answer: ").strip()
                        if len(custom_answer) < 3:
                            print("⚠️  Please provide a more detailed answer.\n")
                            attempts += 1
                            continue
                        answer = custom_answer
                        selected_option_text = f"Custom: {custom_answer}"
                        break  # Exit validation loop
                    
                    if user_input.upper() not in ['A', 'B', 'YES', 'NO']:
                        print("⚠️  Please answer A, B, Yes, No, or type 'OTHER'\n")
                        attempts += 1
                        continue
                    if user_input.upper() in ['YES', 'Y']:
                        answer = 'A'
                    elif user_input.upper() in ['NO', 'N']:
                        answer = 'B'
                    else:
                        answer = user_input.upper()
                
                else:  # open_ended
                    if len(user_input) < 3:
                        print("⚠️  Please provide a more detailed answer.\n")
                        attempts += 1
                        continue
                    answer = sanitize_input(user_input)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Input interrupted. Exiting...")
                raise
            except Exception as e:
                print(f"\n⚠️  Error: {str(e)}\n")
                attempts += 1
        
        if answer is None:
            print(f"\n❌ Max attempts reached. Defaulting to first option.")
            if question['options']:
                answer = question['options'][0]['label']
            else:
                answer = "Not answered"
        
        if answer.upper() != 'OTHER' and not answer.startswith('Custom:'):
            if question['question_type'] == 'multiple_choice' and question['options']:
                for opt in question['options']:
                    if opt['label'].upper() == answer.upper():
                        selected_option_text = opt['text']
                        break
            else:
                selected_option_text = answer
        
        response = {
            "question_id": question['id'],
            "question_text": question['question_text'],
            "answer": answer,
            "answer_full_text": selected_option_text,
            "timestamp": datetime.now().isoformat()
        }
        responses.append(response)
        
        question['user_response'] = response
        
        print(f"\n✓ Recorded: {selected_option_text}\n")
    
    print("="*70)
    print(f"✅ All {len(responses)} question(s) answered!")
    print("="*70 + "\n")
    
    return responses



def human_input_node(state: Phase1State) -> Dict:
    """
    HUMAN_INPUT_NODE: Collects user responses via CLI.
    
    This node implements the interrupt pattern - workflow pauses here
    until user provides input.
    
    Args:
        state: Current Phase1State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("👤 HUMAN_INPUT_NODE: Collecting user responses...")
    print("="*70)
    
    current_questions = state.get("current_questions", [])
    
    if not current_questions:
        print("\n⚠️  No questions to answer!")
        return {
            "current_step": "human_input_skipped",
            "pending_user_response": False
        }
    
    try:
        responses = collect_user_responses_cli(current_questions)
        
        updated_questions = current_questions.copy()
        
        updates = {
            "user_responses": responses,  # Will be added to existing via Annotated[List, add]
            "questions_asked": updated_questions,  # Will be added to existing
            "pending_user_response": False,
            "current_step": "human_input_complete"
        }
        
        updated_state = {**state, **updates}
        save_state(updated_state, "human_input")
        
        print(f"\n✅ Collected {len(responses)} response(s)")
        print("▶️  Resuming workflow...\n")
        print("="*70 + "\n")
        
        return updates
        
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted. Saving current state...\n")
        
        return {
            "current_step": "human_input_interrupted",
            "errors": ["User interrupted input collection"]
        }
    
    except Exception as e:
        print(f"\n❌ HUMAN_INPUT_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "human_input_failed",
            "errors": [f"Input collection failed: {str(e)}"]
        }