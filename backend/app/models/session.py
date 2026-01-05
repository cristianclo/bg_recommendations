"""
SessionProfile model for class context characterization (Module B - RF-CTX-01).
Represents a teaching session with objectives, constraints, and requirements.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import enum

from ..core.database import Base
from ..models.game import LanguageDependency


class Modality(str, enum.Enum):
    """Game modality preference."""
    COMPETITIVE = "competitive"
    COOPERATIVE = "cooperative"
    ANY = "any"


class SessionProfile(Base):
    """
    Session profile capturing the context of a teaching session (RF-CTX-01).
    
    Stores all parameters needed to generate appropriate game recommendations
    for a specific class session, including objectives, constraints, and warnings.
    """
    
    __tablename__ = "session_profiles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Session identification (RF-CTX-01)
    session_name = Column(String(255), nullable=True)  # Optional friendly name
    objectives = Column(ARRAY(String), nullable=False)  # At least 1 required (RF-CTX-01)
    
    # Skills to work on (RF-CTX-01)
    # Note: These will reference Skill model once Module C is implemented
    primary_skill_id = Column(Integer, nullable=True)  # Will be FK to skills table
    secondary_skill_id = Column(Integer, nullable=True)  # Optional
    
    # For now, store skill names as text until Module C is ready
    primary_skill_name = Column(String(255), nullable=False)  # Temporary
    secondary_skill_name = Column(String(255), nullable=True)  # Temporary
    
    # Time constraints (RF-CTX-01)
    available_time_min = Column(Integer, nullable=False)  # 15-240 minutes
    
    # Group characteristics (RF-CTX-01)
    group_size = Column(Integer, nullable=False)  # 1-100
    
    # Language constraints (RF-CTX-01)
    max_language_dependency = Column(
        SQLEnum(LanguageDependency, name="language_dependency_enum"),
        nullable=False,
        default=LanguageDependency.MEDIA
    )
    
    # Modality preference (RF-CTX-01)
    preferred_modality = Column(
        SQLEnum(Modality, name="modality_enum"),
        nullable=False,
        default=Modality.ANY
    )
    
    # Additional constraints (RF-CTX-01)
    additional_constraints = Column(JSON, nullable=True)  # Flexible structure
    notes = Column(Text, nullable=True)  # Free text notes
    
    # Validation warnings (RF-CTX-02)
    # Stored as JSON array of warning messages
    validation_warnings = Column(JSON, nullable=True, default=list)
    has_warnings = Column(Boolean, default=False)  # Quick flag for filtering
    
    # Traceability (RF-EXP-02)
    # user_id = Column(Integer, nullable=True)  # Will be FK once auth is implemented
    created_by_name = Column(String(255), nullable=True)  # Temporary
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Flag if this was used to generate recommendations
    has_recommendations = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<SessionProfile(id={self.id}, objectives={self.objectives}, group_size={self.group_size})>"
    
    def get_warning_count(self) -> int:
        """Get number of validation warnings."""
        if not self.validation_warnings:
            return 0
        return len(self.validation_warnings) if isinstance(self.validation_warnings, list) else 0
    
    def is_large_group(self) -> bool:
        """Check if group is considered large (>20 people)."""
        return self.group_size > 20
    
    def is_very_large_group(self) -> bool:
        """Check if group is very large (>30 people)."""
        return self.group_size > 30
    
    def has_limited_time(self) -> bool:
        """Check if available time is limited (<30 min)."""
        return self.available_time_min < 30
    
    def to_dict(self) -> dict:
        """Convert to dictionary for traceability."""
        return {
            "id": self.id,
            "session_name": self.session_name,
            "objectives": self.objectives,
            "primary_skill": self.primary_skill_name,
            "secondary_skill": self.secondary_skill_name,
            "available_time_min": self.available_time_min,
            "group_size": self.group_size,
            "max_language_dependency": self.max_language_dependency.value if self.max_language_dependency else None,
            "preferred_modality": self.preferred_modality.value if self.preferred_modality else None,
            "additional_constraints": self.additional_constraints,
            "validation_warnings": self.validation_warnings,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
