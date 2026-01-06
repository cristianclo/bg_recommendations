"""
Router for recommendation endpoints.
Implements RF-REC-01, RF-REC-02, RF-REC-03 requirements.
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

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
    
    return recommendations


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
