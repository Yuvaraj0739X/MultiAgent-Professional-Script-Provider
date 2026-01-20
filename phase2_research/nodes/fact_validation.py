import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import get_llm_config

from ..state import Phase2State
from ..models import FactValidationOutput



FACT_VALIDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a fact verification specialist for historical research.

Your job is to cross-reference facts and determine which are VERIFIED, DISPUTED, or UNVERIFIED.

VALIDATION CRITERIA:

1. VERIFIED (confirmed):
   - Fact appears in 2+ different source articles
   - Details match across sources
   - No contradictions
   - Assign status: "confirmed"

2. DISPUTED (conflicting):
   - Fact has conflicting versions in different sources
   - Dates or details don't match
   - Contradictory information
   - Assign status: "disputed"
   - Note the discrepancy

3. UNVERIFIED (single source):
   - Fact appears in only 1 source article
   - Cannot cross-reference
   - Assign status: "unverified"

PROCESS:
1. Group similar facts together
2. Compare details across sources
3. Identify agreements and conflicts
4. Categorize each fact

IMPORTANT:
- Be strict: 2+ sources required for "confirmed"
- Flag any inconsistencies
- Preserve original fact text
- Note which sources support each fact

Return structured JSON matching FactValidationOutput schema."""),
    
    ("user", """Validate these extracted facts by cross-referencing sources:

FACTS TO VALIDATE:
{facts_text}

Cross-reference and categorize each fact as:
- VERIFIED (2+ sources confirm)
- DISPUTED (sources conflict)
- UNVERIFIED (single source only)

Return validation results.""")
])



def get_llm():
    """Initialize OpenAI LLM with centralized config"""
    config = get_llm_config("phase2", "fact_validation")  # Replace NODENAME
    return ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(FactValidationOutput)  # Keep the output model


def validate_facts(extracted_facts: List[Dict]) -> FactValidationOutput:
    """
    Validate facts by cross-referencing sources.
    
    Args:
        extracted_facts: List of extracted fact dicts
    
    Returns:
        FactValidationOutput with validation results
    """
    llm = get_llm()
    chain = FACT_VALIDATION_PROMPT | llm
    
    facts_text = ""
    
    for i, fact in enumerate(extracted_facts, 1):
        facts_text += f"\n{i}. [{fact['fact_type'].upper()}] {fact['fact_text']}\n"
        facts_text += f"   Source: {fact['source_article']}\n"
        facts_text += f"   Confidence: {fact['confidence']}\n"
        facts_text += f"   ID: {fact['fact_id']}\n"
    
    result = chain.invoke({
        "facts_text": facts_text
    })
    
    return result



def fact_validation_node(state: Phase2State) -> Dict:
    """
    FACT_VALIDATION_NODE: Validates facts through cross-referencing.
    
    Args:
        state: Current Phase2State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("✅ FACT_VALIDATION_NODE: Cross-referencing facts...")
    print("="*70)
    
    extracted_facts = state.get("extracted_facts", [])
    
    if not extracted_facts:
        print("\n⚠️  No facts to validate!")
        return {
            "current_step": "fact_validation_skipped",
            "errors": ["No extracted facts available"]
        }
    
    print(f"\n📊 Validating {len(extracted_facts)} extracted facts")
    print(f"🔍 Cross-referencing sources...\n")
    
    try:
        output = validate_facts(extracted_facts)
        
        print("─"*70)
        print("VALIDATION RESULTS:")
        print("─"*70)
        print(f"✅ Verified facts (2+ sources): {len(output.verified_facts)}")
        print(f"⚠️  Disputed facts (conflicts): {len(output.disputed_facts)}")
        print(f"❓ Unverified facts (1 source): {len(output.unverified_facts)}")
        print(f"\n📊 Verification rate: {output.verification_rate*100:.1f}%")
        
        if output.verified_facts:
            print(f"\n✓ Sample verified facts:")
            for fact in output.verified_facts[:3]:
                print(f"\n   • {fact.fact_text}")
                print(f"     Sources: {', '.join(fact.supporting_sources)}")
        
        if output.disputed_facts:
            print(f"\n⚠️  Disputed facts:")
            for fact in output.disputed_facts[:2]:
                print(f"\n   • {fact.fact_text}")
                if fact.notes:
                    print(f"     Note: {fact.notes}")
        
        verified_dict = [
            {
                "fact_id": fact.fact_id,
                "fact_text": fact.fact_text,
                "fact_type": fact.fact_type,
                "supporting_sources": fact.supporting_sources,
                "verification_status": fact.verification_status,
                "notes": fact.notes
            }
            for fact in output.verified_facts
        ]
        
        disputed_dict = [
            {
                "fact_id": fact.fact_id,
                "fact_text": fact.fact_text,
                "fact_type": fact.fact_type,
                "supporting_sources": fact.supporting_sources,
                "verification_status": fact.verification_status,
                "notes": fact.notes
            }
            for fact in output.disputed_facts
        ]
        
        unverified_dict = [
            {
                "fact_id": fact.fact_id,
                "fact_text": fact.fact_text,
                "fact_type": fact.fact_type,
                "supporting_sources": fact.supporting_sources,
                "verification_status": fact.verification_status,
                "notes": fact.notes
            }
            for fact in output.unverified_facts
        ]
        
        updates = {
            "verified_facts": verified_dict,
            "disputed_facts": disputed_dict,
            "unverified_facts": unverified_dict,
            "validation_summary": {
                "total_facts": len(extracted_facts),
                "verified_count": len(verified_dict),
                "disputed_count": len(disputed_dict),
                "unverified_count": len(unverified_dict),
                "verification_rate": output.verification_rate,
                "summary": output.validation_summary
            },
            "current_step": "fact_validation_complete"
        }
        
        print(f"\n✅ Fact validation complete")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ FACT_VALIDATION_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "fact_validation_failed",
            "errors": [f"Fact validation failed: {str(e)}"]
        }