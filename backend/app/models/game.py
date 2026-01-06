"""
Game model representing board games in the catalog.
Implements RF-ING-01 and RF-ING-02 requirements.
"""
from sqlalchemy import Boolean, Column, Float, Integer, String, Text, Enum as SQLEnum, DateTime, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import TYPE_CHECKING

from ..core.database import Base

if TYPE_CHECKING:
    from .recommendation import Recommendation


class LanguageDependency(str, enum.Enum):
    """Language dependency levels according to RF-ING-02."""
    NINGUNA = "ninguna"  # No text, only images/numbers
    BAJA = "baja"  # Minimal text (card names, simple instructions)
    MEDIA = "media"  # Moderate text (flavor text, abilities)
    ALTA = "alta"  # Heavy text (storytelling, complex rules)


class Game(Base):
    """
    Board game model with normalized attributes.
    
    Attributes according to RF-ING-01:
    - name: Game name
    - bgg_id: BoardGameGeek ID (unique identifier)
    - duration_min: Average duration in minutes
    - complexity: Difficulty/complexity (1.0-5.0 scale)
    - min_players: Minimum number of players
    - max_players: Maximum number of players
    - mechanics: List of game mechanics
    - language_dependency: Text dependency level
    - bgg_rank: BoardGameGeek ranking (lower is better)
    - available: Physical availability at CJEI
    """
    
    __tablename__ = "games"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic attributes (RF-ING-01)
    name = Column(String(255), nullable=False, index=True)
    bgg_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Game characteristics (RF-ING-02 normalized)
    duration_min = Column(Integer, nullable=False, default=60)  # Clamped 5-360
    complexity = Column(Float, nullable=False, default=2.5)  # Clamped 1.0-5.0
    min_players = Column(Integer, nullable=False, default=2)
    max_players = Column(Integer, nullable=False, default=4)
    
    # Mechanics (controlled vocabulary, RF-ING-02)
    mechanics = Column(ARRAY(String), nullable=False, default=list)
    
    # Language dependency (enum, RF-ING-02)
    language_dependency = Column(
        SQLEnum(LanguageDependency, name="language_dependency_enum"),
        nullable=False,
        default=LanguageDependency.BAJA
    )
    
    # Additional metadata
    bgg_rank = Column(Integer, nullable=True, index=True)  # Nullable, used for scoring
    description = Column(Text, nullable=True)  # Full game description from BGG
    image_url = Column(String(500), nullable=True)  # Cover image URL
    year_published = Column(Integer, nullable=True)
    
    # CJEI specific
    available = Column(Boolean, nullable=False, default=True, index=True)  # Physical availability
    
    # Data quality flags (RF-ING-01)
    has_partial_data = Column(Boolean, default=False)  # Mark incomplete records
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # Using string reference to avoid circular import
    recommendations = relationship("Recommendation", back_populates="game", lazy="dynamic")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_game_available_complexity', 'available', 'complexity'),
        Index('idx_game_players', 'min_players', 'max_players'),
        Index('idx_game_duration', 'duration_min'),
    )
    
    def __repr__(self):
        return f"<Game(id={self.id}, name='{self.name}', bgg_id={self.bgg_id})>"
    
    def supports_player_count(self, players: int) -> bool:
        """Check if game supports given player count."""
        return self.min_players <= players <= self.max_players
    
    def fits_time_constraint(self, available_time: int, buffer_minutes: int = 15) -> bool:
        """Check if game fits within available time (with buffer for setup/explanation)."""
        return self.duration_min + buffer_minutes <= available_time
    
    def matches_language_constraint(self, max_dependency: LanguageDependency) -> bool:
        """
        Check if game's language dependency is within acceptable level.
        Uses hierarchy: ninguna < baja < media < alta
        """
        dependency_order = {
            LanguageDependency.NINGUNA: 0,
            LanguageDependency.BAJA: 1,
            LanguageDependency.MEDIA: 2,
            LanguageDependency.ALTA: 3,
        }
        return dependency_order[self.language_dependency] <= dependency_order[max_dependency]
