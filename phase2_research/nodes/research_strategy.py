import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import get_llm_config


from ..state import Phase2State
from ..models import ResearchStrategyOutput



RESEARCH_STRATEGY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a research strategist specializing in historical fact verification.

Your job is to generate targeted Wikipedia search queries to gather factual information 
for a historical story.

QUERY GENERATION RULES:

1. NUMBER OF QUERIES: Generate 5-10 queries (no more, no less)

2. QUERY TYPES (mix of these):
   - BIOGRAPHICAL: Main people involved
   - EVENT-SPECIFIC: The central event/battle/incident
   - TIMELINE: Chronological context
   - CONTEXTUAL: Historical period, location, political situation
   - PRIMARY SOURCES: Letters, documents, speeches (if documented on Wikipedia)

3. QUERY QUALITY:
   - Be SPECIFIC: "Battle of Waterloo" not "Napoleon battles"
   - Use EXACT NAMES: "Napoleon Bonaparte" not "French emperor"
   - Include TIME PERIODS when relevant: "World War 1 1914-1918"
   - NO interpretive queries: Avoid "analysis of" or "meaning of"

4. PRIORITIZATION:
   - HIGH: Core people and central event (must have)
   - MEDIUM: Supporting figures and contextual information
   - LOW: Background details

5. AVOID:
   - Opinion pieces or analyses
   - Modern interpretations
   - Fictional adaptations
   - Pop culture references

STRATEGY:
Your queries should cover:
- Who was involved (people)
- What happened (events)
- When it happened (timeline)
- Where it happened (locations)
- Context (historical background)

Return structured JSON matching ResearchStrategyOutput schema."""),
    
    ("user", """Generate Wikipedia research queries for this story:

STORY BRIEF:
{story_brief}

DETECTED ENTITIES:
{detected_entities}

CLASSIFICATION: {classification}

Generate 5-10 targeted Wikipedia queries to gather factual information.""")
])



def get_llm():
    """Initialize OpenAI LLM with centralized config"""
    config = get_llm_config("phase2", "research_strategy")  # Replace NODENAME
    return ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(ResearchStrategyOutput)  # Keep the output model



def generate_research_queries(
    story_brief: str,
    detected_entities: dict,
    classification: str
) -> ResearchStrategyOutput:
    """
    Generate Wikipedia research queries using LLM.
    
    Args:
        story_brief: Complete story brief from Phase 1
        detected_entities: Entities detected in Phase 1
        classification: Story classification
    
    Returns:
        ResearchStrategyOutput with queries
    """
    llm = get_llm()
    chain = RESEARCH_STRATEGY_PROMPT | llm
    
    entities_text = "\n".join([f"- {k}: {v}" for k, v in detected_entities.items()])
    if not entities_text:
        entities_text = "None explicitly detected"
    
    result = chain.invoke({
        "story_brief": story_brief[:3000],  # Limit length for prompt
        "detected_entities": entities_text,
        "classification": classification
    })
    
    return result



def research_strategy_node(state: Phase2State) -> Dict:
    """
    RESEARCH_STRATEGY_NODE: Generates Wikipedia search queries.
    
    Args:
        state: Current Phase2State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("🎯 RESEARCH_STRATEGY_NODE: Generating Wikipedia queries...")
    print("="*70)
    
    print(f"\n📊 Story classification: {state['classification']}")
    print(f"📝 Story brief length: {len(state['phase1_brief'])} characters")
    
    try:
        output = generate_research_queries(
            story_brief=state["phase1_brief"],
            detected_entities=state["detected_entities"],
            classification=state["classification"]
        )
        
        print(f"\n✓ Generated {len(output.queries)} research queries:\n")
        print("─"*70)
        
        for i, query in enumerate(output.queries, 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            emoji = priority_emoji.get(query.priority, "⚪")
            
            print(f"{i}. {emoji} [{query.priority.upper()}] {query.query}")
            print(f"   Type: {query.data_type}")
            print(f"   Why: {query.rationale}\n")
        
        print("─"*70)
        print(f"\n📋 Strategy: {output.strategy_explanation}")
        print(f"\n🎯 Will cover: {', '.join(output.expected_coverage)}")
        
        queries_dict = [
            {
                "query": q.query,
                "priority": q.priority,
                "data_type": q.data_type,
                "rationale": q.rationale
            }
            for q in output.queries
        ]
        
        updates = {
            "research_queries": queries_dict,
            "query_strategy": output.strategy_explanation,
            "current_step": "research_strategy_complete"
        }
        
        print(f"\n✅ Research strategy complete")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ RESEARCH_STRATEGY_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "research_strategy_failed",
            "errors": [f"Query generation failed: {str(e)}"]
        }