"""
Router for recommendation endpoints.
Implements RF-REC-01, RF-REC-02, RF-REC-03, RF-EXP-01, RF-EXP-02 requirements.
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from ..core.database import get_db
from ..core.exceptions import NotFoundException, ValidationException
from ..schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    Recommendation,
    ScoringConfig,
    ScoringConfigCreate,
    ScoringConfigUpdate,
)
from ..recommendations.engine import RecommendationEngine
from ..recommendations.config_service import ScoringConfigService
from ..recommendations.explainability_service import ExplainabilityService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


# ============================================================================
# Recommendation Generation Endpoints (RF-REC-01, RF-REC-03)
# ============================================================================

@router.post("/generate", response_model=RecommendationResponse)
def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate top-N game recommendations for a session profile.
    
    **RF-REC-01**: Generates ranked recommendations with scoring details and traceability.
    **RF-REC-03**: Returns relaxation suggestions if no results found.
    
    **Args:**
    - **session_profile_id**: Session to generate recommendations for
    - **top_n**: Number of recommendations (1-50, default: 10)
    - **use_config_id**: Specific scoring config (default: active config)
    - **include_explanations**: Include human-readable explanations (default: true)
    
    **Returns:**
    - Ranked list of game recommendations
    - Scoring details for each game
    - Total candidates matching filters
    - Scoring configuration used
    - Relaxation suggestions if no results (RF-REC-03)
    """
    engine = RecommendationEngine(db)
    
    return engine.generate_recommendations(
        session_profile_id=request.session_profile_id,
        top_n=request.top_n,
        config_id=request.use_config_id,
        include_explanations=request.include_explanations
    )


@router.get("/session/{session_id}", response_model=List[Recommendation])
def get_session_recommendations(
    session_id: int = Path(..., description="Session profile ID"),
    db: Session = Depends(get_db)
):
    """
    Get all recommendations previously generated for a session.
    
    **Returns:**
    - List of recommendations ordered by rank
    - Empty list if no recommendations generated yet
    """
    from ..models.recommendation import Recommendation as RecommendationModel
    
    recommendations = db.query(RecommendationModel).filter(
        RecommendationModel.session_profile_id == session_id
    ).order_by(RecommendationModel.rank).all()
    
    # Convert to Pydantic schemas to avoid serialization issues
    result = []
    for rec in recommendations:
        rec_dict = {
            'id': rec.id,
            'session_profile_id': rec.session_profile_id,
            'game_id': rec.game_id,
            'rank': rec.rank,
            'total_score': rec.total_score,
            'skill_score': rec.skill_score,
            'mechanics_score': rec.mechanics_score,
            'difficulty_score': rec.difficulty_score,
            'ranking_score': rec.ranking_score,
            'feedback_boost': rec.feedback_boost,
            'weights_used': rec.weights_used,
            'explanation_text': rec.explanation_text,
            'match_reasons': rec.match_reasons,
            'was_selected': rec.was_selected,
            'user_feedback_score': rec.user_feedback_score,
            'created_at': rec.created_at,
            'game': None
        }
        result.append(Recommendation(**rec_dict))
    
    return result


@router.put("/recommendation/{rec_id}/feedback", response_model=Recommendation)
def update_recommendation_feedback(
    rec_id: int = Path(..., description="Recommendation ID"),
    was_selected: Optional[bool] = Query(None, description="Mark as selected"),
    feedback_score: Optional[int] = Query(None, ge=1, le=5, description="User rating (1-5)"),
    db: Session = Depends(get_db)
):
    """
    Update recommendation feedback (for RF-RETRO-01, RF-RETRO-02).
    
    **Args:**
    - **rec_id**: Recommendation ID
    - **was_selected**: Whether user selected this game
    - **feedback_score**: User rating from 1-5
    
    **Returns:**
    - Updated recommendation
    """
    from ..models.recommendation import Recommendation as RecommendationModel
    
    rec = db.query(RecommendationModel).filter(
        RecommendationModel.id == rec_id
    ).first()
    
    if not rec:
        raise NotFoundException("Recommendation", str(rec_id))
    
    if was_selected is not None:
        rec.was_selected = was_selected
    
    if feedback_score is not None:
        rec.user_feedback_score = feedback_score
    
    db.commit()
    db.refresh(rec)
    
    return rec


# ============================================================================
# Scoring Configuration Endpoints (RF-REC-02)
# ============================================================================

@router.post("/configs", response_model=ScoringConfig, status_code=201)
def create_scoring_config(
    config_create: ScoringConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new scoring configuration.
    
    **RF-REC-02**: Allows administrators to create custom weight configurations.
    
    **Args:**
    - **name**: Configuration name (unique)
    - **description**: Optional description
    - **skill_weight**: Weight for skill match (0.0-1.0)
    - **mechanics_weight**: Weight for mechanics similarity (0.0-1.0)
    - **difficulty_weight**: Weight for difficulty match (0.0-1.0)
    - **ranking_weight**: Weight for BGG ranking (0.0-1.0)
    - **is_active**: Set as active configuration
    - **is_default**: Set as default configuration
    
    **Validation:**
    - All weights must sum to 1.0 (±0.01 tolerance)
    - Name must be unique
    """
    service = ScoringConfigService(db)
    return service.create(config_create)


@router.get("/configs", response_model=List[ScoringConfig])
def list_scoring_configs(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records"),
    active_only: bool = Query(False, description="Only return active config"),
    db: Session = Depends(get_db)
):
    """
    List all scoring configurations.
    
    **Args:**
    - **skip**: Pagination offset
    - **limit**: Page size (1-100)
    - **active_only**: Filter for active configuration only
    
    **Returns:**
    - List of scoring configurations
    """
    service = ScoringConfigService(db)
    return service.list(skip=skip, limit=limit, active_only=active_only)


@router.get("/configs/active", response_model=ScoringConfig)
def get_active_config(db: Session = Depends(get_db)):
    """
    Get currently active scoring configuration.
    
    **Returns:**
    - Active scoring configuration
    - Falls back to default if no active config
    
    **Raises:**
    - 404 if no active or default configuration found
    """
    service = ScoringConfigService(db)
    
    config = service.get_active()
    if not config:
        config = service.get_default()
    
    if not config:
        raise NotFoundException(
            "ScoringConfig",
            "No active or default configuration found"
        )
    
    return config


@router.get("/configs/{config_id}", response_model=ScoringConfig)
def get_scoring_config(
    config_id: int = Path(..., description="Configuration ID"),
    db: Session = Depends(get_db)
):
    """
    Get scoring configuration by ID.
    
    **Returns:**
    - Scoring configuration details
    """
    service = ScoringConfigService(db)
    config = service.get_by_id(config_id)
    
    if not config:
        raise NotFoundException("ScoringConfig", str(config_id))
    
    return config


@router.put("/configs/{config_id}", response_model=ScoringConfig)
def update_scoring_config(
    config_update: ScoringConfigUpdate,
    config_id: int = Path(..., description="Configuration ID"),
    db: Session = Depends(get_db)
):
    """
    Update scoring configuration.
    
    **RF-REC-02**: Allows administrators to adjust weights.
    
    **Args:**
    - **config_id**: Configuration to update
    - Fields to update (all optional)
    
    **Validation:**
    - If updating weights, sum must still equal 1.0
    - Name must remain unique
    """
    service = ScoringConfigService(db)
    return service.update(config_id, config_update)


@router.delete("/configs/{config_id}", status_code=204)
def delete_scoring_config(
    config_id: int = Path(..., description="Configuration ID"),
    db: Session = Depends(get_db)
):
    """
    Delete scoring configuration.
    
    **Restrictions:**
    - Cannot delete active configuration
    - Cannot delete default configuration
    
    **Returns:**
    - 204 No Content on success
    """
    service = ScoringConfigService(db)
    service.delete(config_id)


@router.post("/configs/{config_id}/activate", response_model=ScoringConfig)
def activate_config(
    config_id: int = Path(..., description="Configuration ID"),
    db: Session = Depends(get_db)
):
    """
    Activate a scoring configuration.
    
    **RF-REC-02**: Set which configuration to use for recommendations.
    
    **Effect:**
    - Deactivates all other configurations
    - Sets this configuration as active
    
    **Returns:**
    - Updated configuration
    """
    service = ScoringConfigService(db)
    return service.activate(config_id)


@router.post("/configs/{config_id}/set-default", response_model=ScoringConfig)
def set_default_config(
    config_id: int = Path(..., description="Configuration ID"),
    db: Session = Depends(get_db)
):
    """
    Set configuration as default.
    
    **Effect:**
    - Removes default flag from other configurations
    - Sets this configuration as default
    
    **Returns:**
    - Updated configuration
    """
    service = ScoringConfigService(db)
    return service.set_as_default(config_id)


# ============================================================================
# Explainability Endpoints (RF-EXP-01, RF-EXP-02) - Module E
# ============================================================================

@router.get("/explanations/{recommendation_id}", response_model=Dict)
def get_recommendation_explanation(
    recommendation_id: int = Path(..., description="Recommendation ID"),
    include_technical: bool = Query(False, description="Include technical scoring details"),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation for a specific recommendation.
    
    **RF-EXP-01**: Provides natural language explanation with at least 3 specific reasons:
    - Skill/habilidades alignment
    - Operational constraints (time, players)
    - Relevant mechanics
    - Quality indicators (BGG rank)
    - Boost factors (if applicable)
    
    **Args:**
    - **recommendation_id**: ID of the recommendation
    - **include_technical**: Include technical scoring breakdown
    
    **Returns:**
    - Detailed explanation with score components
    - Game details in context
    - Session context for full traceability
    - Optional technical details
    """
    service = ExplainabilityService(db)
    return service.get_recommendation_explanation(
        recommendation_id=recommendation_id,
        include_technical=include_technical
    )


@router.post("/explanations/compare", response_model=Dict)
def compare_recommendations(
    recommendation_ids: List[int] = Query(..., description="2-5 recommendation IDs to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple recommendations side-by-side.
    
    **RF-EXP-01**: Helps understand why one game was recommended over another.
    Useful for pedagogical advisors to make informed decisions.
    
    **Args:**
    - **recommendation_ids**: List of 2-5 recommendation IDs
    
    **Returns:**
    - Comparative score analysis
    - Key differences identified
    - Natural language explanations of differences
    
    **Raises:**
    - 400: If less than 2 or more than 5 IDs provided
    - 404: If any recommendation not found
    """
    service = ExplainabilityService(db)
    return service.compare_recommendations(recommendation_ids)


@router.get("/traceability/{recommendation_id}", response_model=Dict)
def get_traceability_report(
    recommendation_id: int = Path(..., description="Recommendation ID"),
    db: Session = Depends(get_db)
):
    """
    Generate complete traceability report for audit purposes.
    
    **RF-EXP-02**: Complete, non-editable decision trail including:
    - Timestamp and user
    - Complete session profile snapshot
    - Scoring configuration used
    - All score components
    - Decision rationale
    - User outcome (if selected/feedback)
    
    **Purpose:** Institutional knowledge preservation, system evaluation, auditing.
    Allows answering: "Why did we recommend game X for session Y 3 months ago?"
    
    **Args:**
    - **recommendation_id**: Recommendation ID
    
    **Returns:**
    - Complete audit trail (read-only, immutable)
    - Session and game snapshots
    - Scoring details
    - Outcome tracking
    """
    service = ExplainabilityService(db)
    return service.get_traceability_report(recommendation_id)


@router.get("/history/session/{session_profile_id}", response_model=List[Dict])
def get_session_recommendation_history(
    session_profile_id: int = Path(..., description="Session profile ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of historical entries"),
    db: Session = Depends(get_db)
):
    """
    Get historical recommendations for a specific session profile.
    
    **RF-EXP-02**: Traceability over time. View all past recommendation batches
    generated for this session profile.
    
    **Use cases:**
    - Track how recommendations changed over time
    - Analyze pattern of selections
    - Evaluate system performance for specific contexts
    
    **Args:**
    - **session_profile_id**: Session profile ID
    - **limit**: Maximum number of historical batches (default: 10)
    
    **Returns:**
    - List of recommendation batches ordered by timestamp (newest first)
    - Each batch includes: timestamp, games recommended, selection status
    """
    service = ExplainabilityService(db)
    return service.get_session_recommendation_history(
        session_profile_id=session_profile_id,
        limit=limit
    )

