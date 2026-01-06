"""
Recommendation model for storing generated recommendations (Module D).
Implements RF-REC-01 traceability requirements.
"""
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..core.database import Base


class Recommendation(Base):
    """
    Stores a generated recommendation for traceability and analysis.
    Each recommendation links a session profile to a recommended game with scoring details.
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_profile_id = Column(Integer, ForeignKey("session_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Ranking and scoring
    rank = Column(Integer, nullable=False)  # Position in top-N (1 is best)
    total_score = Column(Float, nullable=False)  # Final weighted score
    
    # Score components (for explainability)
    skill_score = Column(Float, nullable=False)  # Skill match component
    mechanics_score = Column(Float, nullable=False)  # Mechanics similarity component
    difficulty_score = Column(Float, nullable=False)  # Difficulty appropriateness component
    ranking_score = Column(Float, nullable=False)  # BGG ranking component
    feedback_boost = Column(Float, nullable=True, default=0.0)  # Historical feedback boost
    
    # Weights used (for reproducibility)
    weights_used = Column(JSON, nullable=False)  # {"skill": 0.4, "mechanics": 0.3, ...}
    
    # Explanation
    explanation_text = Column(Text, nullable=True)  # Human-readable explanation
    match_reasons = Column(JSON, nullable=True)  # Structured reasons for match
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    was_selected = Column(Boolean, default=False, nullable=True)  # Did asesor choose this one?
    user_feedback_score = Column(Integer, nullable=True)  # 1-5 if feedback was given
    
    # Feedback fields (RF-RETRO-01)
    was_used = Column(Boolean, nullable=True)  # Was the game actually used in session?
    feedback_date = Column(DateTime, nullable=True)  # When feedback was given
    feedback_asesor = Column(String(100), nullable=True)  # Asesor who gave feedback
    skill_actually_worked = Column(String(200), nullable=True)  # Skill that was actually developed
    what_worked_well = Column(Text, nullable=True)  # Qualitative: what worked (max 500 chars)
    what_didnt_work = Column(Text, nullable=True)  # Qualitative: what didn't work (max 500 chars)
    additional_notes = Column(Text, nullable=True)  # Additional observations (max 500 chars)
    can_edit_until = Column(DateTime, nullable=True)  # Feedback editable for 7 days
    
    # Relationships
    session_profile = relationship("SessionProfile", back_populates="recommendations")
    game = relationship("Game")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, session={self.session_profile_id}, game={self.game_id}, rank={self.rank}, score={self.total_score:.2f})>"


class ScoringConfig(Base):
    """
    Stores scoring weight configurations for the recommendation engine.
    Implements RF-REC-02 (configurable weights).
    """
    __tablename__ = "scoring_configs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Weight components (must sum to 1.0)
    skill_weight = Column(Float, nullable=False, default=0.40)
    mechanics_weight = Column(Float, nullable=False, default=0.30)
    difficulty_weight = Column(Float, nullable=False, default=0.20)
    ranking_weight = Column(Float, nullable=False, default=0.10)
    
    is_active = Column(Boolean, default=False, nullable=False)  # Only one can be active
    is_default = Column(Boolean, default=False, nullable=False)  # Marks the default config
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<ScoringConfig(name='{self.name}', skill={self.skill_weight}, mechanics={self.mechanics_weight})>"
    
    def get_weights_dict(self) -> dict:
        """Return weights as dictionary."""
        return {
            "skill": self.skill_weight,
            "mechanics": self.mechanics_weight,
            "difficulty": self.difficulty_weight,
            "ranking": self.ranking_weight
        }
    
    def weights_sum(self) -> float:
        """Calculate sum of all weights."""
        return self.skill_weight + self.mechanics_weight + self.difficulty_weight + self.ranking_weight
    
    def is_valid(self) -> bool:
        """Check if weights are valid (sum to 1.0)."""
        return abs(self.weights_sum() - 1.0) < 0.001  # Allow small floating point errors
