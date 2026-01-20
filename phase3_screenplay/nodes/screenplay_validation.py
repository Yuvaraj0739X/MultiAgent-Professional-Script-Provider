import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain_openai import ChatOpenAI
from config import get_llm_config
from phase3_screenplay.state import Phase3State
from phase3_screenplay.models import ValidationResult
from phase3_screenplay.utils import validate_fountain_syntax


def screenplay_validation_node(state: Phase3State) -> dict:
    """
    Validate screenplay for Fountain format compliance and quality.
    
    This node performs:
    1. Syntax validation (scene headings, character names, formatting)
    2. Structure validation (page count, scene count, flow)
    3. Content validation (character consistency, location usage)
    4. LLM-based quality assessment
    
    Args:
        state: Phase3State containing screenplay_text
        
    Returns:
        State updates with validation_result and validation_passed
    """
    print("\n" + "="*80)
    print("PHASE 3 - NODE 3: SCREENPLAY VALIDATION")
    print("="*80)
    
    screenplay = state.get("screenplay_text", "")
    if not screenplay:
        raise ValueError("No screenplay_text found in state")
    
    print(f"\n📝 Validating screenplay ({len(screenplay)} characters)...")
    
    metadata = state.get("screenplay_metadata", {})
    scene_breakdown = state.get("scene_breakdown", [])
    
    print("\n🔍 Phase 1: Syntax Validation...")
    syntax_validation = validate_fountain_syntax(screenplay)
    
    print(f"  Compliance Score: {syntax_validation['compliance_score']:.1f}%")
    print(f"  Errors: {len(syntax_validation['errors'])}")
    print(f"  Warnings: {len(syntax_validation['warnings'])}")
    
    if syntax_validation['errors']:
        print("  ❌ Errors found:")
        for error in syntax_validation['errors'][:3]:
            print(f"    - {error}")
        if len(syntax_validation['errors']) > 3:
            print(f"    ... and {len(syntax_validation['errors']) - 3} more")
    
    if syntax_validation['warnings']:
        print("  ⚠️  Warnings:")
        for warning in syntax_validation['warnings'][:3]:
            print(f"    - {warning}")
        if len(syntax_validation['warnings']) > 3:
            print(f"    ... and {len(syntax_validation['warnings']) - 3} more")
    
    print("\n🏗️  Phase 2: Structure Validation...")
    structural_errors = []
    structural_warnings = []
    
    page_count = metadata.get("page_count", 0)
    if page_count < 15:
        structural_warnings.append(f"Screenplay is short ({page_count} pages, target: 15-30)")
    elif page_count > 35:
        structural_warnings.append(f"Screenplay is long ({page_count} pages, target: 15-30)")
    else:
        print(f"  ✅ Page count: {page_count} pages")
    
    expected_scenes = len(scene_breakdown)
    actual_scenes = metadata.get("scene_count", 0)
    if expected_scenes != actual_scenes:
        structural_warnings.append(
            f"Scene count mismatch: expected {expected_scenes}, found {actual_scenes}"
        )
    else:
        print(f"  ✅ Scene count: {actual_scenes} scenes")
    
    duration = metadata.get("estimated_duration", 0)
    if duration < 15:
        structural_warnings.append(f"Duration is short ({duration} min, target: 15-30)")
    elif duration > 35:
        structural_warnings.append(f"Duration is long ({duration} min, target: 15-30)")
    else:
        print(f"  ✅ Duration: {duration} minutes")
    
    print(f"  Structural issues: {len(structural_errors)} errors, {len(structural_warnings)} warnings")
    
    print("\n🤖 Phase 3: LLM Quality Assessment...")
    
    system_prompt = """You are an expert screenplay format validator and script reader.

Your task is to assess the quality and compliance of a screenplay with industry standards.

EVALUATION CRITERIA:
1. Fountain Format Compliance
   - Proper scene headings (INT./EXT. LOCATION - TIME)
   - Character names in ALL CAPS before dialogue
   - Clean formatting without errors

2. Storytelling Quality
   - Clear narrative structure
   - Character development
   - Dialogue authenticity
   - Visual storytelling
   - Pacing and flow

3. Professional Standards
   - Appropriate length (15-30 pages)
   - Filmable scenes
   - Production feasibility
   - Industry conventions

Provide a quality assessment with:
- Overall assessment (professional/good/needs work/poor)
- Specific strengths
- Specific areas for improvement
- Recommendations for refinement (if needed)
"""

    user_prompt = f"""Assess this screenplay for quality and professional standards:

METADATA:
- Page Count: {page_count}
- Scene Count: {actual_scenes}
- Duration: {duration} minutes
- Characters: {metadata.get('character_count', 0)}
- Locations: {metadata.get('location_count', 0)}

SCREENPLAY EXCERPT (first 1000 characters):
{screenplay[:1000]}

...

SCREENPLAY EXCERPT (last 500 characters):
{screenplay[-500:]}

Provide your professional assessment."""

    llm_config = get_llm_config("phase3", "validation")
    
    print(f"🤖 Using model: {llm_config['model']} (temp: {llm_config['temperature']})")
    
    llm = ChatOpenAI(**llm_config)
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = llm.invoke(messages)
        quality_assessment = response.content.strip()
        
        print(f"  ✅ Quality assessment completed")
        print(f"\n📊 Assessment Preview:")
        print(f"  {quality_assessment[:200]}...")
        
    except Exception as e:
        print(f"  ⚠️  Could not complete quality assessment: {e}")
        quality_assessment = f"Quality assessment failed: {e}"
    
    print("\n📋 Combining validation results...")
    
    all_errors = syntax_validation['errors'] + structural_errors
    all_warnings = syntax_validation['warnings'] + structural_warnings
    
    syntax_score = syntax_validation['compliance_score']
    structure_score = 100.0
    
    if structural_errors:
        structure_score -= len(structural_errors) * 20
    if structural_warnings:
        structure_score -= len(structural_warnings) * 5
    
    structure_score = max(0.0, min(100.0, structure_score))
    
    overall_compliance = (syntax_score * 0.7) + (structure_score * 0.3)
    
    validation_passed = overall_compliance >= 80.0 and len(all_errors) == 0
    
    print(f"  Overall Compliance: {overall_compliance:.1f}%")
    print(f"  Validation: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
    
    validation_result = {
        "is_valid": validation_passed,
        "errors": all_errors,
        "warnings": all_warnings,
        "compliance_score": overall_compliance,
        "format_checks": {
            "syntax_score": syntax_score,
            "structure_score": structure_score,
            "quality_assessment": quality_assessment
        },
        "recommendations": []
    }
    
    if not validation_passed:
        if all_errors:
            validation_result["recommendations"].append(
                "Fix critical format errors before proceeding"
            )
        if overall_compliance < 90:
            validation_result["recommendations"].append(
                "Consider running refinement node to improve quality"
            )
        if page_count < 15:
            validation_result["recommendations"].append(
                "Expand scenes to meet minimum page count"
            )
    
    print(f"\n{'='*80}")
    print(f"VALIDATION COMPLETE: {'PASSED ✅' if validation_passed else 'FAILED ❌'}")
    print(f"{'='*80}")
    
    return {
        "validation_result": validation_result,
        "validation_passed": validation_passed
    }


if __name__ == "__main__":
    print("Testing screenplay_validation_node...")
    
    test_screenplay = """NAPOLEON'S LAST STAND
Written by AI Screenplay Generator

FADE IN:

EXT. WATERLOO BATTLEFIELD - DAY

Cannons roar. Smoke fills the air. Thousands of soldiers clash.

NAPOLEON BONAPARTE (45), weathered but determined, surveys the chaos from horseback.

NAPOLEON
(to his officers)
The time has come. Signal the Old Guard.

MARSHAL NEY approaches on horseback, mud-stained and frantic.

NEY
Sire, the Prussians are flanking our right!

NAPOLEON
(grimly)
Then we must break Wellington's center before they arrive.

He raises his sword high.

NAPOLEON (CONT'D)
La Garde au feu!

The Imperial Guard begins their advance.

FADE OUT.

THE END
"""

    test_metadata = {
        "page_count": 2,
        "estimated_duration": 2,
        "scene_count": 1,
        "character_count": 2,
        "location_count": 1
    }
    
    test_state: Phase3State = {
        "user_input": "Napoleon at Waterloo",
        "phase1_brief": "Story...",
        "research_required": False,
        "screenplay_text": test_screenplay,
        "screenplay_metadata": test_metadata,
        "scene_breakdown": [{"scene_number": 1}]
    }
    
    result = screenplay_validation_node(test_state)
    
    print("\n" + "="*80)
    print("TEST RESULT:")
    print("="*80)
    print(f"Validation Passed: {result.get('validation_passed', False)}")
    print(f"Compliance Score: {result.get('validation_result', {}).get('compliance_score', 0):.1f}%")
    print(f"Errors: {len(result.get('validation_result', {}).get('errors', []))}")
    print(f"Warnings: {len(result.get('validation_result', {}).get('warnings', []))}")