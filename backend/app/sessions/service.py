"""
SessionProfile service implementing business logic and CRUD operations (Module B).
Implements RF-CTX-01 and RF-CTX-02 requirements.
"""
from __future__ import annotations

import logging
import math
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.session import SessionProfile
from ..schemas.session import SessionProfileCreate, SessionProfileUpdate, ValidationWarning
from ..sessions.validator import SessionValidator
from ..core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class SessionProfileService:
    """
    Service for session profile management with automatic validation.
    Implements RF-CTX-01 (session capture) and RF-CTX-02 (coherence validation).
    """
    
    def __init__(self):
        self.validator = SessionValidator()
    
    def create(self, db: Session, profile_data: SessionProfileCreate) -> SessionProfile:
        """
        Create a new session profile with automatic validation (RF-CTX-01, RF-CTX-02).
        
        Args:
            db: Database session
            profile_data: Session profile data
            
        Returns:
            Created SessionProfile with validation warnings
        """
        # Create session profile from data
        profile_dict = profile_data.model_dump()
        profile = SessionProfile(**profile_dict)
        
        # Run validation (RF-CTX-02)
        warnings = self.validator.validate_session(profile)
        
        # Store warnings as JSON
        if warnings:
            profile.validation_warnings = [w.model_dump() for w in warnings]
            profile.has_warnings = True
            logger.info(
                f"Session profile created with {len(warnings)} warnings: "
                f"{[w.code for w in warnings]}"
            )
        else:
            profile.validation_warnings = []
            profile.has_warnings = False
            logger.info("Session profile created with no warnings")
        
        # Save to database
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        logger.info(
            f"Created session profile {profile.id}: "
            f"group={profile.group_size}, time={profile.available_time_min}min, "
            f"warnings={len(warnings)}"
        )
        
        return profile
    
    def get_by_id(self, db: Session, profile_id: int) -> SessionProfile:
        """Get session profile by ID."""
        profile = db.query(SessionProfile).filter(SessionProfile.id == profile_id).first()
        if not profile:
            raise NotFoundException("SessionProfile", str(profile_id))
        return profile
    
    def list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        has_warnings: Optional[bool] = None,
        min_group_size: Optional[int] = None,
        max_group_size: Optional[int] = None,
        skill_name: Optional[str] = None,
        sort_by: str = "created_at"
    ) -> tuple[list[SessionProfile], int]:
        """
        List session profiles with optional filters and pagination.
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Items per page
            has_warnings: Filter by warning presence
            min_group_size: Minimum group size filter
            max_group_size: Maximum group size filter
            skill_name: Filter by skill name (partial match)
            sort_by: Sort field
            
        Returns:
            Tuple of (profiles, total_count)
        """
        query = db.query(SessionProfile)
        
        # Apply filters
        if has_warnings is not None:
            query = query.filter(SessionProfile.has_warnings == has_warnings)
        
        if min_group_size:
            query = query.filter(SessionProfile.group_size >= min_group_size)
        
        if max_group_size:
            query = query.filter(SessionProfile.group_size <= max_group_size)
        
        if skill_name:
            # Search in both primary and secondary skills
            query = query.filter(
                (SessionProfile.primary_skill_name.ilike(f"%{skill_name}%")) |
                (SessionProfile.secondary_skill_name.ilike(f"%{skill_name}%"))
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if sort_by == "created_at":
            query = query.order_by(desc(SessionProfile.created_at))
        elif sort_by == "group_size":
            query = query.order_by(desc(SessionProfile.group_size))
        elif sort_by == "time":
            query = query.order_by(SessionProfile.available_time_min)
        
        # Apply pagination
        offset = (page - 1) * page_size
        profiles = query.offset(offset).limit(page_size).all()
        
        return profiles, total
    
    def update(
        self,
        db: Session,
        profile_id: int,
        update_data: SessionProfileUpdate
    ) -> SessionProfile:
        """
        Update session profile and re-validate.
        
        Args:
            db: Database session
            profile_id: Profile ID to update
            update_data: Update data
            
        Returns:
            Updated SessionProfile with new validation warnings
        """
        profile = self.get_by_id(db, profile_id)
        
        # Get only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Update fields
        for key, value in update_dict.items():
            setattr(profile, key, value)
        
        # Re-run validation if key fields changed
        validation_fields = {
            'group_size', 'available_time_min', 'preferred_modality'
        }
        if any(field in update_dict for field in validation_fields):
            warnings = self.validator.validate_session(profile)
            profile.validation_warnings = [w.model_dump() for w in warnings]
            profile.has_warnings = len(warnings) > 0
            logger.info(f"Re-validated profile {profile_id}: {len(warnings)} warnings")
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Updated session profile {profile_id}")
        return profile
    
    def delete(self, db: Session, profile_id: int) -> None:
        """Delete session profile by ID."""
        profile = self.get_by_id(db, profile_id)
        db.delete(profile)
        db.commit()
        logger.info(f"Deleted session profile {profile_id}")
    
    def get_recent(
        self,
        db: Session,
        limit: int = 10,
        created_by: Optional[str] = None
    ) -> list[SessionProfile]:
        """
        Get recent session profiles, optionally filtered by creator.
        
        Args:
            db: Database session
            limit: Maximum number of profiles to return
            created_by: Filter by creator name
            
        Returns:
            List of recent SessionProfiles
        """
        query = db.query(SessionProfile).order_by(desc(SessionProfile.created_at))
        
        if created_by:
            query = query.filter(SessionProfile.created_by_name == created_by)
        
        return query.limit(limit).all()
    
    def get_statistics(self, db: Session) -> dict:
        """
        Get statistics about session profiles.
        
        Returns:
            Dictionary with various statistics
        """
        total = db.query(SessionProfile).count()
        with_warnings = db.query(SessionProfile).filter(
            SessionProfile.has_warnings == True
        ).count()
        with_recommendations = db.query(SessionProfile).filter(
            SessionProfile.has_recommendations == True
        ).count()
        
        # Average group size
        from sqlalchemy import func
        avg_group_size = db.query(
            func.avg(SessionProfile.group_size)
        ).scalar() or 0
        
        avg_time = db.query(
            func.avg(SessionProfile.available_time_min)
        ).scalar() or 0
        
        return {
            "total_sessions": total,
            "sessions_with_warnings": with_warnings,
            "warning_rate": (with_warnings / total * 100) if total > 0 else 0,
            "sessions_with_recommendations": with_recommendations,
            "average_group_size": round(avg_group_size, 1),
            "average_time_minutes": round(avg_time, 1)
        }
