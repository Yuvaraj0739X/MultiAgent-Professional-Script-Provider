import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import get_llm_config

from ..state import Phase2State
from ..models import FactExtractionOutput



FACT_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a historical fact extraction specialist.

Your job is to extract VERIFIED, FACTUAL information from Wikipedia articles for screenplay research.

EXTRACTION RULES:

1. FACT TYPES TO EXTRACT:
   - DATES: Specific dates, time periods
   - EVENTS: What happened (battles, meetings, decisions)
   - PEOPLE: Who was involved, their roles, relationships
   - LOCATIONS: Where events occurred, geographic details
   - STATISTICS: Numbers (troop counts, casualties, distances)
   - RELATIONSHIPS: Connections between people, causes and effects

2. CONFIDENCE LEVELS:
   - HIGH: Explicitly stated, multiple confirmations in text
   - MEDIUM: Clearly stated but single mention
   - LOW: Implied or contextual

3. WHAT TO EXTRACT:
   - Specific, verifiable facts
   - Names, dates, numbers
   - Concrete events and actions
   - Geographic locations

4. WHAT TO AVOID:
   - Opinions or interpretations
   - "Believed to be" or "possibly"
   - Modern analyses
   - Speculative statements

5. FORMAT:
   Each fact should be:
   - Concise (one sentence)
   - Self-contained
   - Attributable to source article

Return structured JSON matching FactExtractionOutput schema."""),
    
    ("user", """Extract factual information from these Wikipedia articles:

ARTICLES:
{articles_text}

Extract 20-40 key facts relevant to the story. Focus on:
- Timeline of events
- Key people and their roles
- Important locations
- Critical decisions and outcomes

Return facts in structured format.""")
])



def get_llm():
    """Initialize OpenAI LLM with centralized config"""
    config = get_llm_config("phase2", "fact_extraction")  # Replace NODENAME
    return ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(FactExtractionOutput)  # Keep the output model



def extract_facts_from_articles(articles: List[Dict]) -> FactExtractionOutput:
    """
    Extract facts from Wikipedia articles using LLM.
    
    Args:
        articles: List of Wikipedia article dicts
    
    Returns:
        FactExtractionOutput with extracted facts
    """
    llm = get_llm()
    chain = FACT_EXTRACTION_PROMPT | llm
    
    articles_text = ""
    
    for i, article in enumerate(articles[:15], 1):  # Process first 15 articles
        title = article.get("title", "Unknown")
        summary = article.get("summary", "")[:2000]  # First 2000 chars
        
        articles_text += f"\n{'='*60}\n"
        articles_text += f"ARTICLE {i}: {title}\n"
        articles_text += f"{'='*60}\n"
        articles_text += summary
        articles_text += "\n"
    
    if len(articles_text) > 15000:
        articles_text = articles_text[:15000] + "\n\n[...truncated for length...]"
    
    result = chain.invoke({
        "articles_text": articles_text
    })
    
    return result



def fact_extraction_node(state: Phase2State) -> Dict:
    """
    FACT_EXTRACTION_NODE: Extracts facts from Wikipedia articles.
    
    Args:
        state: Current Phase2State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("🔍 FACT_EXTRACTION_NODE: Extracting facts from articles...")
    print("="*70)
    
    articles = state.get("wikipedia_articles", [])
    
    if not articles:
        print("\n⚠️  No Wikipedia articles to process!")
        return {
            "current_step": "fact_extraction_skipped",
            "errors": ["No Wikipedia articles available"]
        }
    
    print(f"\n📚 Processing {len(articles)} Wikipedia articles")
    print(f"📊 Extracting factual information...\n")
    
    try:
        output = extract_facts_from_articles(articles)
        
        fact_categories = {
            "dates": [],
            "events": [],
            "people": [],
            "locations": [],
            "statistics": [],
            "relationships": []
        }
        
        for fact in output.extracted_facts:
            fact_type = fact.fact_type
            if fact_type in fact_categories:
                fact_categories[fact_type].append(fact)
        
        print("─"*70)
        print("EXTRACTION RESULTS:")
        print("─"*70)
        print(f"✅ Total facts extracted: {output.total_facts_found}")
        print(f"\n📊 By category:")
        for category, facts in fact_categories.items():
            if facts:
                print(f"   • {category.capitalize()}: {len(facts)}")
        
        print(f"\n📝 Sample facts:")
        for fact in output.extracted_facts[:5]:
            confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
            emoji = confidence_emoji.get(fact.confidence, "⚪")
            print(f"\n   {emoji} [{fact.fact_type.upper()}]")
            print(f"   {fact.fact_text}")
            print(f"   Source: {fact.source_article}")
        
        if len(output.extracted_facts) > 5:
            print(f"\n   ... and {len(output.extracted_facts) - 5} more facts")
        
        facts_dict = [
            {
                "fact_id": fact.fact_id,
                "fact_text": fact.fact_text,
                "fact_type": fact.fact_type,
                "source_article": fact.source_article,
                "source_section": fact.source_section,
                "confidence": fact.confidence
            }
            for fact in output.extracted_facts
        ]
        
        updates = {
            "extracted_facts": facts_dict,
            "fact_categories": {k: [f.fact_text for f in v] for k, v in fact_categories.items()},
            "current_step": "fact_extraction_complete"
        }
        
        print(f"\n✅ Fact extraction complete")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ FACT_EXTRACTION_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "fact_extraction_failed",
            "errors": [f"Fact extraction failed: {str(e)}"]
        }