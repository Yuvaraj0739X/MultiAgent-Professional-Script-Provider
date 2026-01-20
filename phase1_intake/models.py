from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional


class DetectedElement(BaseModel):
    """Single detected element key-value pair"""
    key: str = Field(..., description="Element name (e.g., 'genre', 'protagonist')")
    value: str = Field(..., description="Element value")


class IntakeAnalysisOutput(BaseModel):
    """
    Output from INTAKE_NODE analysis.
    LLM must return this exact structure.
    """
    clarity_score: int = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Clarity score from 0-100"
    )
    
    is_complete: bool = Field(
        ..., 
        description="Whether story has sufficient detail"
    )
    
    missing_elements: List[str] = Field(
        ...,
        description="List of missing critical elements"
    )
    
    detected_elements: List[DetectedElement] = Field(
        ...,
        description="Elements that ARE present"
    )
    
    ambiguities: List[str] = Field(
        ...,
        description="Unclear aspects needing clarification"
    )
    
    classification: Literal["real", "fictional", "mixed"] = Field(
        ...,
        description="Story type classification"
    )
    
    research_required: bool = Field(
        ...,
        description="Whether external research needed"
    )
    
    reasoning: str = Field(
        ...,
        description="Brief explanation of the analysis"
    )


class QuestionOption(BaseModel):
    """Single option in a multiple choice question"""
    label: str = Field(..., description="Option label (e.g., 'A', 'B')")
    text: str = Field(..., description="Full option text")


class ClarificationQuestion(BaseModel):
    """
    Single clarification question.
    """
    id: str = Field(..., description="Unique question ID (e.g., 'q1')")
    
    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="Question priority"
    )
    
    question_text: str = Field(
        ...,
        description="The actual question to ask user"
    )
    
    question_type: Literal["multiple_choice", "binary", "open_ended"] = Field(
        ...,
        description="Type of question"
    )
    
    options: Optional[List[QuestionOption]] = Field(
        None,
        description="Options for multiple choice (null for open-ended)"
    )
    
    context: str = Field(
        ...,
        description="Why this question matters (shown to user)"
    )


class ClarificationOutput(BaseModel):
    """
    Output from CLARIFICATION_NODE.
    Contains 1-3 questions to ask user.
    """
    questions: List[ClarificationQuestion] = Field(
        ...,
        min_items=1,
        max_items=3,
        description="List of questions (max 3)"
    )
    
    question_count: int = Field(
        ...,
        ge=1,
        le=3,
        description="Number of questions generated"
    )
    
    rationale: str = Field(
        ...,
        description="Why these specific questions were chosen"
    )


class IntegrationOutput(BaseModel):
    """
    Output from INTEGRATION_NODE.
    Refined story description incorporating user responses.
    """
    refined_description: str = Field(
        ...,
        description="Enriched story description"
    )
    
    changes_made: List[str] = Field(
        ...,
        description="What was added/clarified"
    )


class StoryBrief(BaseModel):
    """
    Output from SUMMARY_NODE.
    Complete structured story brief.
    """
    title: str = Field(..., description="Working title")
    logline: str = Field(..., description="One-sentence story summary")
    
    classification: str = Field(..., description="real/fictional/mixed")
    research_required: bool
    
    genre_and_tone: str = Field(..., description="Genre and tonal description")
    runtime: str = Field(..., description="Target runtime (e.g., '25-30 minutes')")
    
    timeline_structure: str = Field(
        ..., 
        description="How story unfolds over time"
    )
    
    characters: str = Field(
        ..., 
        description="Character descriptions"
    )
    
    setting: str = Field(..., description="Where and when story takes place")
    
    visual_approach: str = Field(
        ..., 
        description="Cinematography and visual style"
    )
    
    themes: str = Field(..., description="Thematic exploration")
    
    key_moments: str = Field(
        ..., 
        description="Critical dramatic beats"
    )
    
    full_brief_markdown: str = Field(
        ...,
        description="Complete brief in markdown format"
    )



class UserResponse(BaseModel):
    """User's answer to a clarification question"""
    question_id: str
    question_text: str
    answer: str
    timestamp: str


class QuestionHistory(BaseModel):
    """Record of a question asked"""
    iteration: int
    question: ClarificationQuestion
    user_response: Optional[UserResponse] = None