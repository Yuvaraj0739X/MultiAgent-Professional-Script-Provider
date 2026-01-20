import os
import sys
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

sys.path.append('..')

from ..state import Phase2State
from ..models import TimelineOutput



TIMELINE_BUILD_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a historical timeline construction specialist.

Your job is to organize verified facts into a CHRONOLOGICAL TIMELINE for screenplay use.

TIMELINE CONSTRUCTION RULES:

1. CHRONOLOGICAL ORDER:
   - Sort events by date (earliest to latest)
   - Use format: YYYY-MM-DD (or YYYY-MM or YYYY if partial)
   - If exact date unknown, estimate based on context

2. EVENT STRUCTURE:
   Each event should have:
   - Date (as specific as possible)
   - Event title (concise, descriptive)
   - Event description (2-3 sentences, filmable details)
   - Participants (who was involved)
   - Location (where it occurred)
   - Significance (why it matters for the story)
   - Sources (which Wikipedia articles confirm this)

3. KEY FIGURES:
   Create profiles for main people:
   - Full name
   - Role in story/history
   - Verified biographical details
   - Relevant dates of involvement
   - Sources

4. KEY LOCATIONS:
   Document important places:
   - Location name
   - Type (city, battlefield, building, etc.)
   - Verified details
   - Significance to story
   - Sources

5. SCREENPLAY FOCUS:
   - Emphasize FILMABLE events (not abstract concepts)
   - Include sensory details when available
   - Note dramatic moments
   - Identify potential scene locations

Return structured JSON matching TimelineOutput schema."""),
    
    ("user", """Build a chronological timeline from these verified facts:

VERIFIED FACTS:
{verified_facts_text}

STORY BRIEF (for context):
{story_brief}

Create:
1. Chronological timeline of events
2. Key figures profiles
3. Key locations documentation

Focus on events relevant for a screenplay.""")
])



def get_llm():
    """Initialize OpenAI LLM with structured output"""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,  # Low-medium for structured organization
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(TimelineOutput)



def build_timeline(
    verified_facts: List[Dict],
    story_brief: str
) -> TimelineOutput:
    """
    Build chronological timeline from verified facts.
    
    Args:
        verified_facts: List of verified fact dicts
        story_brief: Story brief for context
    
    Returns:
        TimelineOutput with timeline and key entities
    """
    llm = get_llm()
    chain = TIMELINE_BUILD_PROMPT | llm
    
    facts_text = ""
    
    for i, fact in enumerate(verified_facts, 1):
        facts_text += f"\n{i}. [{fact['fact_type'].upper()}] {fact['fact_text']}\n"
        facts_text += f"   Sources: {', '.join(fact.get('supporting_sources', []))}\n"
    
    result = chain.invoke({
        "verified_facts_text": facts_text,
        "story_brief": story_brief[:2000]  # Truncate brief for token limits
    })
    
    return result



def timeline_build_node(state: Phase2State) -> Dict:
    """
    TIMELINE_BUILD_NODE: Constructs chronological timeline.
    
    Args:
        state: Current Phase2State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("📅 TIMELINE_BUILD_NODE: Constructing chronological timeline...")
    print("="*70)
    
    verified_facts = state.get("verified_facts", [])
    
    if not verified_facts:
        print("\n⚠️  No verified facts to build timeline!")
        return {
            "current_step": "timeline_build_skipped",
            "errors": ["No verified facts available"]
        }
    
    print(f"\n📊 Building timeline from {len(verified_facts)} verified facts")
    print(f"🗓️  Organizing chronologically...\n")
    
    try:
        output = build_timeline(
            verified_facts=verified_facts,
            story_brief=state.get("phase1_brief", "")
        )
        
        print("─"*70)
        print("TIMELINE RESULTS:")
        print("─"*70)
        print(f"📅 Timeline span: {output.timeline_span}")
        print(f"🎬 Total events: {output.event_count}")
        print(f"👥 Key figures: {len(output.key_figures)}")
        print(f"📍 Key locations: {len(output.key_locations)}")
        
        if output.timeline:
            print(f"\n📅 Timeline preview:")
            for event in output.timeline[:5]:
                print(f"\n   {event.date} - {event.event_title}")
                print(f"   {event.event_description[:100]}...")
                if event.location:
                    print(f"   Location: {event.location}")
        
        if output.key_figures:
            print(f"\n👥 Key figures:")
            for figure in output.key_figures[:3]:
                print(f"   • {figure.name} - {figure.role}")
        
        if output.key_locations:
            print(f"\n📍 Key locations:")
            for location in output.key_locations[:3]:
                print(f"   • {location.name} ({location.location_type})")
        
        timeline_dict = [
            {
                "date": event.date,
                "event_title": event.event_title,
                "event_description": event.event_description,
                "participants": event.participants,
                "location": event.location,
                "significance": event.significance,
                "sources": event.sources
            }
            for event in output.timeline
        ]
        
        figures_dict = [
            {
                "name": fig.name,
                "role": fig.role,
                "verified_details": {f"detail_{i}": detail for i, detail in enumerate(fig.verified_details)},
                "relevant_dates": fig.relevant_dates,
                "sources": fig.sources
            }
            for fig in output.key_figures
        ]
        
        locations_dict = [
            {
                "name": loc.name,
                "location_type": loc.location_type,
                "verified_details": {f"detail_{i}": detail for i, detail in enumerate(loc.verified_details)},
                "significance": loc.significance,
                "sources": loc.sources
            }
            for loc in output.key_locations
        ]
        
        updates = {
            "timeline": timeline_dict,
            "key_figures": figures_dict,
            "key_locations": locations_dict,
            "timeline_metadata": {
                "timeline_span": output.timeline_span,
                "event_count": output.event_count,
                "figures_count": len(figures_dict),
                "locations_count": len(locations_dict)
            },
            "current_step": "timeline_build_complete"
        }
        
        print(f"\n✅ Timeline construction complete")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ TIMELINE_BUILD_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "timeline_build_failed",
            "errors": [f"Timeline construction failed: {str(e)}"]
        }