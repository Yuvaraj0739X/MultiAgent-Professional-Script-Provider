from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime



class ResearchQuery(BaseModel):
    """Single Wikipedia search query"""
    query: str = Field(..., description="Wikipedia search query")
    priority: Literal["high", "medium", "low"] = Field(..., description="Query priority")
    data_type: str = Field(..., description="What type of data to extract (biographical, event, contextual)")
    rationale: str = Field(..., description="Why this query is needed")


class ResearchStrategyOutput(BaseModel):
    """Output from research strategy generation"""
    queries: List[ResearchQuery] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of Wikipedia queries (5-10 queries)"
    )
    
    strategy_explanation: str = Field(
        ...,
        description="Overall research strategy"
    )
    
    expected_coverage: List[str] = Field(
        ...,
        description="What aspects will be covered by research"
    )



class ExtractedFact(BaseModel):
    """Single extracted fact from Wikipedia"""
    fact_id: str = Field(..., description="Unique fact identifier")
    fact_text: str = Field(..., description="The actual fact")
    fact_type: Literal["date", "event", "person", "location", "statistic", "relationship"] = Field(
        ...,
        description="Type of fact"
    )
    source_article: str = Field(..., description="Wikipedia article title")
    source_section: Optional[str] = Field(None, description="Section within article")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence in fact accuracy")


class FactExtractionOutput(BaseModel):
    """Output from fact extraction node"""
    extracted_facts: List[ExtractedFact] = Field(
        ...,
        description="All facts extracted from Wikipedia"
    )
    
    total_facts_found: int = Field(..., description="Total number of facts")
    
    extraction_summary: str = Field(
        ...,
        description="Summary of extraction process"
    )



class VerifiedFact(BaseModel):
    """Fact verified by multiple sources"""
    fact_id: str = Field(..., description="Unique identifier")
    fact_text: str = Field(..., description="The verified fact")
    fact_type: str = Field(..., description="Type of fact")
    
    supporting_sources: List[str] = Field(
        ...,
        min_items=2,
        description="Wikipedia articles confirming this fact (minimum 2)"
    )
    
    verification_status: Literal["confirmed", "disputed", "unverified"] = Field(
        ...,
        description="Verification status"
    )
    
    notes: Optional[str] = Field(
        None,
        description="Additional notes or caveats"
    )


class FactValidationOutput(BaseModel):
    """Output from fact validation node"""
    verified_facts: List[VerifiedFact] = Field(..., description="Facts confirmed by 2+ sources")
    disputed_facts: List[VerifiedFact] = Field(..., description="Facts with conflicting info")
    unverified_facts: List[VerifiedFact] = Field(..., description="Single-source facts")
    
    verification_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Percentage of facts verified (0.0-1.0)"
    )
    
    validation_summary: str = Field(..., description="Summary of validation process")



class TimelineEvent(BaseModel):
    """Single event in chronological timeline"""
    date: str = Field(..., description="Date of event (YYYY-MM-DD or partial)")
    event_title: str = Field(..., description="Brief title of event")
    event_description: str = Field(..., description="Detailed description")
    
    participants: List[str] = Field(
        ...,
        description="People involved in event"
    )
    
    location: Optional[str] = Field(None, description="Where event occurred")
    
    significance: str = Field(
        ...,
        description="Why this event matters for the story"
    )
    
    sources: List[str] = Field(..., description="Supporting Wikipedia sources")


class KeyFigure(BaseModel):
    """Important person in the story"""
    name: str = Field(..., description="Full name")
    role: str = Field(..., description="Role in story/history")
    
    verified_details: List[str] = Field(
        ...,
        description="List of verified biographical details as strings"
    )
    
    relevant_dates: List[str] = Field(
        ...,
        description="Key dates in their involvement"
    )
    
    sources: List[str] = Field(..., description="Wikipedia sources")


class KeyLocation(BaseModel):
    """Important place in the story"""
    name: str = Field(..., description="Location name")
    location_type: str = Field(..., description="Type (city, battlefield, building, etc.)")
    
    verified_details: List[str] = Field(
        ...,
        description="List of verified location details as strings"
    )
    
    significance: str = Field(..., description="Why location matters")
    sources: List[str] = Field(..., description="Wikipedia sources")


class TimelineOutput(BaseModel):
    """Output from timeline construction node"""
    timeline: List[TimelineEvent] = Field(
        ...,
        description="Chronological timeline of events"
    )
    
    key_figures: List[KeyFigure] = Field(
        ...,
        description="Important people"
    )
    
    key_locations: List[KeyLocation] = Field(
        ...,
        description="Important places"
    )
    
    timeline_span: str = Field(
        ...,
        description="Time period covered (e.g., 'June 12-18, 1815')"
    )
    
    event_count: int = Field(..., description="Total events in timeline")