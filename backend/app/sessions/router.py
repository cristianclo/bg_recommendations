"""
FastAPI router for session profile operations (Module B).
Implements RF-CTX-01 and RF-CTX-02 endpoints.
"""
import logging
import math
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..schemas.session import (
    SessionProfile, SessionProfileCreate, SessionProfileUpdate,
    SessionProfileList, SessionProfileSummary
)
from ..sessions.service import SessionProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])
session_service = SessionProfileService()


@router.post("/", response_model=SessionProfile, status_code=status.HTTP_201_CREATED)
def create_session_profile(
    profile_data: SessionProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new session profile (RF-CTX-01).
    
    Captures the context of a teaching session including:
    - Class objectives (at least 1 required)
    - Primary skill to work on (required)
    - Secondary skill (optional)
    - Available time (15-240 minutes)
    - Group size (1-100)
    - Language dependency constraint
    - Modality preference (competitive/cooperative/any)
    - Additional constraints and notes
    
    **Automatic Validation (RF-CTX-02):**
    The system automatically validates operational coherence and generates
    warnings (not errors) for potentially problematic configurations:
    
    - Large groups (>20): Suggests stations/multiple tables
    - Very large groups (>30): Strongly recommends stations
    - Limited time (<30min): Warns about complexity limitations
    - Cooperative + large group: Suggests team subdivision
    
    Warnings are informational and never block session creation.
    They are stored in the `validation_warnings` field for advisor awareness.
    """
    return session_service.create(db, profile_data)


@router.get("/", response_model=SessionProfileList)
def list_session_profiles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|group_size|time)$",
        description="Sort field"
    ),
    # Filters
    has_warnings: Optional[bool] = Query(None, description="Filter by warning presence"),
    min_group_size: Optional[int] = Query(None, ge=1, description="Minimum group size"),
    max_group_size: Optional[int] = Query(None, le=100, description="Maximum group size"),
    skill_name: Optional[str] = Query(None, description="Filter by skill name"),
    db: Session = Depends(get_db)
):
    """
    List session profiles with optional filters and pagination.
    
    Supports filtering by:
    - Warning presence (sessions with/without operational warnings)
    - Group size range
    - Skill name (searches both primary and secondary)
    
    Results are paginated and can be sorted by creation date, group size, or time.
    """
    profiles, total = session_service.list(
        db,
        page=page,
        page_size=page_size,
        has_warnings=has_warnings,
        min_group_size=min_group_size,
        max_group_size=max_group_size,
        skill_name=skill_name,
        sort_by=sort_by
    )
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return SessionProfileList(
        items=profiles,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/recent", response_model=list[SessionProfileSummary])
def get_recent_sessions(
    limit: int = Query(10, ge=1, le=50, description="Number of recent sessions"),
    created_by: Optional[str] = Query(None, description="Filter by creator name"),
    db: Session = Depends(get_db)
):
    """
    Get recent session profiles.
    
    Useful for quick access to recently created sessions,
    optionally filtered by creator name.
    
    Returns lighter-weight summaries instead of full profiles.
    """
    profiles = session_service.get_recent(db, limit=limit, created_by=created_by)
    
    # Convert to summaries
    summaries = []
    for profile in profiles:
        summaries.append(SessionProfileSummary(
            id=profile.id,
            session_name=profile.session_name,
            objectives=profile.objectives,
            primary_skill_name=profile.primary_skill_name,
            group_size=profile.group_size,
            available_time_min=profile.available_time_min,
            has_warnings=profile.has_warnings,
            warning_count=profile.get_warning_count(),
            created_at=profile.created_at
        ))
    
    return summaries


@router.get("/statistics")
def get_session_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about session profiles.
    
    Returns aggregate information useful for analytics:
    - Total number of sessions created
    - Number with operational warnings
    - Warning rate percentage
    - Sessions with recommendations generated
    - Average group size
    - Average available time
    
    Useful for understanding usage patterns and common scenarios.
    """
    return session_service.get_statistics(db)


@router.get("/{session_id}", response_model=SessionProfile)
def get_session_profile(session_id: int, db: Session = Depends(get_db)):
    """
    Get a specific session profile by ID.
    
    Returns complete session profile including all validation warnings
    with detailed suggestions for addressing operational concerns.
    """
    return session_service.get_by_id(db, session_id)


@router.put("/{session_id}", response_model=SessionProfile)
def update_session_profile(
    session_id: int,
    update_data: SessionProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing session profile.
    
    All fields are optional. Only provided fields will be updated.
    
    **Important:** If group_size, available_time_min, or preferred_modality
    are updated, the system will automatically re-validate operational
    coherence and update the validation warnings accordingly (RF-CTX-02).
    """
    return session_service.update(db, session_id, update_data)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_profile(session_id: int, db: Session = Depends(get_db)):
    """
    Delete a session profile.
    
    **Warning:** This operation is permanent and cannot be undone.
    
    **Note:** If this session has associated recommendations (Module D),
    those will also need to be handled appropriately.
    """
    session_service.delete(db, session_id)
