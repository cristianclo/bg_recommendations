"""
Feedback schemas for Module G - RF-RETRO-01.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FeedbackBase(BaseModel):
    """Base schema for feedback data."""
    was_used: bool = Field(..., description="Was the game actually used in the session?")
    user_feedback_score: int = Field(..., ge=1, le=5, description="Utility rating (1-5 stars)")
    skill_actually_worked: Optional[str] = Field(None, max_length=200, description="Skill that was actually developed")
    what_worked_well: Optional[str] = Field(None, max_length=500, description="What worked well")
    what_didnt_work: Optional[str] = Field(None, max_length=500, description="What didn't work")
    additional_notes: Optional[str] = Field(None, max_length=500, description="Additional observations")


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback (RF-RETRO-01)."""
    feedback_asesor: str = Field(..., max_length=100, description="Name of asesor giving feedback")
    
    @field_validator('user_feedback_score')
    @classmethod
    def validate_score(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Feedback score must be between 1 and 5')
        return v


class FeedbackUpdate(BaseModel):
    """Schema for updating feedback (editable for 7 days)."""
    was_used: Optional[bool] = None
    user_feedback_score: Optional[int] = Field(None, ge=1, le=5)
    skill_actually_worked: Optional[str] = Field(None, max_length=200)
    what_worked_well: Optional[str] = Field(None, max_length=500)
    what_didnt_work: Optional[str] = Field(None, max_length=500)
    additional_notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('user_feedback_score')
    @classmethod
    def validate_score(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Feedback score must be between 1 and 5')
        return v


class FeedbackResponse(FeedbackBase):
    """Complete feedback response."""
    recommendation_id: int
    game_id: int
    game_name: str
    session_profile_id: int
    feedback_date: datetime
    feedback_asesor: str
    can_edit_until: datetime
    is_editable: bool = Field(..., description="Whether feedback can still be edited")
    
    model_config = {"from_attributes": True}


class GameFeedbackStatistics(BaseModel):
    """Aggregated feedback statistics for a game (RF-RETRO-02)."""
    game_id: int
    game_name: str
    total_uses: int = Field(..., description="Number of times the game was used")
    average_utility: Optional[float] = Field(None, description="Average feedback score (1-5)")
    score_distribution: dict = Field(..., description="Distribution of scores {1: count, 2: count, ...}")
    most_common_skill: Optional[str] = Field(None, description="Most frequently reported skill")
    recent_feedback: list[FeedbackResponse] = Field(default_factory=list, description="Up to 3 most recent feedback entries")
    
    model_config = {"from_attributes": True}


class FeedbackAnalytics(BaseModel):
    """System-wide feedback analytics (RF-RETRO-03)."""
    total_feedback_count: int
    total_games_with_feedback: int
    average_utility_overall: float
    most_used_games: list[dict] = Field(..., description="Top 10 most used games")
    highest_rated_games: list[dict] = Field(..., description="Games with utility >= 4.5 and >= 3 uses")
    underperforming_games: list[dict] = Field(..., description="Games with utility < 3.0 and >= 3 uses")
    skills_distribution: dict = Field(..., description="Distribution of feedback by skill")
    
    model_config = {"from_attributes": True}
