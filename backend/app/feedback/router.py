"""
Feedback router for Module G - RF-RETRO-01/02/03.
API endpoints for submitting, retrieving, and analyzing feedback.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.feedback import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    GameFeedbackStatistics,
    FeedbackAnalytics
)
from .service import FeedbackService


router = APIRouter(prefix="/feedback", tags=["Feedback (Module G)"])
service = FeedbackService()


@router.post("/{recommendation_id}", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    recommendation_id: int,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a recommendation (RF-RETRO-01).
    
    **Requirements:**
    - recommendation_id: ID of the recommendation to give feedback on
    - was_used: Whether the game was actually used (required)
    - user_feedback_score: Utility rating 1-5 (required)
    - feedback_asesor: Name of asesor giving feedback (required)
    - Optional: skill_actually_worked, what_worked_well, what_didnt_work, additional_notes
    
    **Response:**
    - Complete feedback data with metadata
    - can_edit_until: Feedback is editable for 7 days
    
    **Notes:**
    - Feedback can only be submitted once per recommendation
    - Use PUT endpoint to update existing feedback
    - Marks recommendation as selected (was_selected=True)
    """
    recommendation = service.submit_feedback(db, recommendation_id, feedback)
    return service.get_feedback(db, recommendation.id)


@router.put("/{recommendation_id}", response_model=FeedbackResponse)
def update_feedback(
    recommendation_id: int,
    feedback: FeedbackUpdate,
    db: Session = Depends(get_db)
):
    """
    Update existing feedback (RF-RETRO-01).
    
    **Requirements:**
    - Feedback must already exist for this recommendation
    - Edit period must not be expired (7 days from submission)
    - Only non-null fields in request body will be updated
    
    **Editable fields:**
    - was_used
    - user_feedback_score (1-5)
    - skill_actually_worked
    - what_worked_well
    - what_didnt_work
    - additional_notes
    
    **Response:**
    - Updated feedback data
    - is_editable: Whether feedback can still be edited
    """
    recommendation = service.update_feedback(db, recommendation_id, feedback)
    return service.get_feedback(db, recommendation.id)


@router.get("/{recommendation_id}", response_model=FeedbackResponse)
def get_feedback(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get feedback for a specific recommendation.
    
    **Response:**
    - Complete feedback data
    - is_editable: Whether feedback can still be edited
    - can_edit_until: Expiration date for edits
    
    **Errors:**
    - 404: Recommendation not found or no feedback exists
    """
    return service.get_feedback(db, recommendation_id)


@router.get("/game/{game_id}/statistics", response_model=GameFeedbackStatistics)
def get_game_feedback_statistics(
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Get aggregated feedback statistics for a game (RF-RETRO-02).
    
    **Response includes:**
    - total_uses: Number of times game was used
    - average_utility: Average feedback score (1-5)
    - score_distribution: Count of each score {1: X, 2: Y, ...}
    - most_common_skill: Most frequently reported skill
    - recent_feedback: Up to 3 most recent feedback entries
    
    **Use cases:**
    - Display in game detail view (RF-UI-04)
    - Help asesores learn from colleagues' experiences
    - Identify games with consistent positive/negative feedback
    
    **Notes:**
    - Returns empty statistics if game has no feedback
    - Used to implement "Experiencias de Uso" section
    """
    return service.get_game_feedback_statistics(db, game_id)


@router.get("/analytics/system", response_model=FeedbackAnalytics)
def get_system_analytics(
    start_date: Optional[datetime] = Query(None, description="Filter feedback from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter feedback until this date"),
    db: Session = Depends(get_db)
):
    """
    Get system-wide feedback analytics (RF-RETRO-03).
    
    **Query parameters:**
    - start_date: Optional filter start date (ISO format)
    - end_date: Optional filter end date (ISO format)
    
    **Response includes:**
    - total_feedback_count: Total feedback entries
    - total_games_with_feedback: Unique games with feedback
    - average_utility_overall: System-wide average score
    - most_used_games: Top 10 games by usage count
    - highest_rated_games: Games with utility >= 4.5 and >= 3 uses (hidden gems)
    - underperforming_games: Games with utility < 3.0 and >= 3 uses (candidates for review)
    - skills_distribution: Distribution of feedback by skill
    
    **Use cases:**
    - Dashboard for admins (RF-ADM-01)
    - Identify catalog gaps and optimization opportunities
    - Support acquisition/retirement decisions
    - Validate taxonomy alignment
    
    **Notes:**
    - Implements "Analíticas de Uso" dashboard
    - Date filters allow period-specific analysis
    """
    return service.get_system_analytics(db, start_date, end_date)


@router.get("/list", response_model=List[FeedbackResponse])
def list_feedback(
    game_id: Optional[int] = Query(None, description="Filter by game"),
    asesor: Optional[str] = Query(None, description="Filter by asesor name"),
    min_score: Optional[int] = Query(None, ge=1, le=5, description="Filter by minimum score"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    db: Session = Depends(get_db)
):
    """
    List feedback with optional filters and pagination.
    
    **Query parameters:**
    - game_id: Filter feedback for specific game
    - asesor: Filter feedback by asesor name
    - min_score: Filter feedback with score >= X
    - skip: Pagination offset (default 0)
    - limit: Results per page (default 50, max 100)
    
    **Response:**
    - List of feedback entries sorted by date (newest first)
    - Each entry includes full feedback data and metadata
    
    **Use cases:**
    - Browse all feedback entries
    - Filter feedback for specific game or asesor
    - Export feedback data for reporting
    - Admin review of feedback quality
    """
    return service.list_feedback(db, game_id, asesor, min_score, skip, limit)


@router.delete("/{recommendation_id}", status_code=204)
def delete_feedback(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete feedback for a recommendation.
    
    **Requirements:**
    - Feedback must exist for this recommendation
    - Only admin users should have access (implement authorization)
    
    **Use cases:**
    - Remove inappropriate or spam feedback
    - Correct accidental submissions beyond edit period
    
    **Notes:**
    - This is a soft delete - sets feedback fields to NULL
    - Preserves recommendation record for traceability
    - Consider implementing hard authorization check
    """
    recommendation = db.query(
        __import__('app.models.recommendation', fromlist=['Recommendation']).Recommendation
    ).filter(
        __import__('app.models.recommendation', fromlist=['Recommendation']).Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        from ..core.exceptions import NotFoundException
        raise NotFoundException("Recommendation", str(recommendation_id))
    
    if recommendation.feedback_date is None:
        from ..core.exceptions import NotFoundException
        raise NotFoundException("Feedback", f"for recommendation {recommendation_id}")
    
    # Soft delete - clear feedback fields
    recommendation.feedback_date = None
    recommendation.feedback_asesor = None
    recommendation.was_used = None
    recommendation.user_feedback_score = None
    recommendation.skill_actually_worked = None
    recommendation.what_worked_well = None
    recommendation.what_didnt_work = None
    recommendation.additional_notes = None
    recommendation.can_edit_until = None
    
    db.commit()
    return None
