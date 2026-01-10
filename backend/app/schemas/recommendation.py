"""
Pydantic schemas for recommendations.
Implements RF-REC-01, RF-REC-02, RF-REC-03 requirements.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any
from datetime import datetime


# ============================================================================
# Scoring Configuration Schemas
# ============================================================================

class ScoringConfigBase(BaseModel):
    """Base schema for scoring configuration."""
    name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    description: Optional[str] = Field(None, description="Optional description")
    
    # Weights (must sum to 1.0)
    skill_weight: float = Field(0.40, ge=0.0, le=1.0, description="Weight for skill match score")
    mechanics_weight: float = Field(0.30, ge=0.0, le=1.0, description="Weight for mechanics similarity")
    difficulty_weight: float = Field(0.20, ge=0.0, le=1.0, description="Weight for difficulty match")
    ranking_weight: float = Field(0.10, ge=0.0, le=1.0, description="Weight for BGG ranking")
    
    @field_validator('skill_weight', 'mechanics_weight', 'difficulty_weight', 'ranking_weight')
    @classmethod
    def validate_weight_range(cls, v: float, info) -> float:
        """Ensure individual weights are in [0, 1] range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{info.field_name} must be between 0.0 and 1.0")
        return v


class ScoringConfigCreate(ScoringConfigBase):
    """Schema for creating a new scoring configuration."""
    is_active: bool = Field(False, description="Whether this is the active configuration")
    is_default: bool = Field(False, description="Whether this is the default configuration")
    
    @field_validator('is_active')
    @classmethod
    def validate_weights_sum(cls, v: bool, info) -> bool:
        """Ensure weights sum to 1.0 when creating config."""
        # Get all weight values from data
        data = info.data
        weights_sum = (
            data.get('skill_weight', 0) +
            data.get('mechanics_weight', 0) +
            data.get('difficulty_weight', 0) +
            data.get('ranking_weight', 0)
        )
        
        # Allow small floating point tolerance
        if not (0.99 <= weights_sum <= 1.01):
            raise ValueError(
                f"Weights must sum to 1.0 (got {weights_sum:.4f}). "
                f"Adjust: skill={data.get('skill_weight')}, mechanics={data.get('mechanics_weight')}, "
                f"difficulty={data.get('difficulty_weight')}, ranking={data.get('ranking_weight')}"
            )
        return v


class ScoringConfigUpdate(BaseModel):
    """Schema for updating a scoring configuration (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    skill_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    mechanics_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    difficulty_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    ranking_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ScoringConfig(ScoringConfigBase):
    """Schema for scoring configuration response."""
    id: int
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ============================================================================
# Recommendation Schemas
# ============================================================================

class RecommendationBase(BaseModel):
    """Base schema for recommendation."""
    session_profile_id: int = Field(..., description="Session profile ID")
    game_id: int = Field(..., description="Recommended game ID")
    rank: int = Field(..., ge=1, description="Position in top-N ranking")
    
    # Score components
    total_score: float = Field(..., ge=0.0, le=1.0, description="Final weighted score")
    skill_score: float = Field(..., ge=0.0, le=1.0, description="Skill match score")
    mechanics_score: float = Field(..., ge=0.0, le=1.0, description="Mechanics similarity score")
    difficulty_score: float = Field(..., ge=0.0, le=1.0, description="Difficulty appropriateness score")
    ranking_score: float = Field(..., ge=0.0, le=1.0, description="BGG ranking score")
    feedback_boost: float = Field(0.0, ge=0.0, le=0.5, description="Historical feedback boost")
    
    # Traceability (RF-REC-01, RF-EXP-02)
    weights_used: Dict[str, float] = Field(..., description="Weights used for this recommendation")
    explanation_text: Optional[str] = Field(None, description="Human-readable explanation")
    match_reasons: Optional[List[str]] = Field(None, description="List of match reasons")


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation (internal use)."""
    was_selected: bool = Field(False, description="Whether this recommendation was selected")
    user_feedback_score: Optional[int] = Field(None, ge=1, le=5, description="User feedback score (1-5)")


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation (feedback only)."""
    was_selected: Optional[bool] = Field(None, description="Mark as selected by user")
    user_feedback_score: Optional[int] = Field(None, ge=1, le=5, description="User feedback score (1-5)")


class Recommendation(RecommendationBase):
    """Schema for recommendation response with related data."""
    id: int
    was_selected: bool
    user_feedback_score: Optional[int]
    created_at: datetime
    
    # Optional: include related game data
    game: Optional[Any] = None  # Will be populated with Game schema if needed
    
    model_config = {"from_attributes": True}


# ============================================================================
# Recommendation Generation Schemas
# ============================================================================

class RecommendationRequest(BaseModel):
    """Request schema for generating recommendations (RF-REC-01)."""
    session_profile_id: int = Field(..., description="Session profile to generate recommendations for")
    top_n: int = Field(10, ge=1, le=50, description="Number of recommendations to generate")
    use_config_id: Optional[int] = Field(None, description="Specific scoring config to use (default: active)")
    include_explanations: bool = Field(True, description="Include human-readable explanations")


class RecommendationResponse(BaseModel):
    """Response schema for recommendation generation."""
    session_profile_id: int
    recommendations: List[Recommendation]
    total_candidates: int = Field(..., description="Total games matching hard filters")
    scoring_config_used: ScoringConfig
    generation_timestamp: datetime
    
    # RF-REC-03: No results handling
    has_results: bool = Field(..., description="Whether any recommendations were found")
    relaxation_suggestions: Optional[List[str]] = Field(None, description="Suggestions if no results")


class RecommendationStatistics(BaseModel):
    """Statistics about recommendations for a session."""
    session_profile_id: int
    total_recommendations: int
    selected_count: int
    avg_total_score: float
    avg_skill_score: float
    avg_mechanics_score: float
    avg_difficulty_score: float
    avg_ranking_score: float
    games_with_feedback: int
    avg_feedback_score: Optional[float]
