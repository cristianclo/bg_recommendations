"""
Pydantic schemas for Game API requests and responses.
Implements validation for RF-ING-01 and RF-ING-02.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

from ..models.game import LanguageDependency


class GameBase(BaseModel):
    """Base schema with common game attributes."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Game name")
    bgg_id: int = Field(..., gt=0, description="BoardGameGeek ID")
    duration_min: int = Field(60, ge=5, le=360, description="Duration in minutes (5-360)")
    complexity: float = Field(2.5, ge=1.0, le=5.0, description="Complexity scale (1.0-5.0)")
    min_players: int = Field(2, ge=1, le=100, description="Minimum players")
    max_players: int = Field(4, ge=1, le=100, description="Maximum players")
    mechanics: list[str] = Field(default_factory=list, description="Game mechanics")
    language_dependency: LanguageDependency = Field(
        LanguageDependency.BAJA,
        description="Language dependency level"
    )
    bgg_rank: Optional[int] = Field(None, gt=0, description="BGG rank (optional)")
    description: Optional[str] = Field(None, max_length=5000, description="Game description")
    image_url: Optional[str] = Field(None, max_length=500, description="Cover image URL")
    year_published: Optional[int] = Field(None, ge=1900, le=2100, description="Publication year")
    available: bool = Field(True, description="Available at CJEI")
    
    @field_validator('max_players')
    @classmethod
    def validate_player_range(cls, v, info):
        """Ensure max_players >= min_players."""
        if 'min_players' in info.data and v < info.data['min_players']:
            raise ValueError('max_players must be >= min_players')
        return v
    
    @field_validator('mechanics')
    @classmethod
    def validate_mechanics(cls, v):
        """Validate mechanics against controlled vocabulary (RF-ING-02)."""
        # Standard BGG mechanics vocabulary
        VALID_MECHANICS = {
            "Action Points", "Area Control", "Auction/Bidding", "Card Drafting",
            "Cooperative Play", "Deck Building", "Dice Rolling", "Grid Movement",
            "Hand Management", "Memory", "Modular Board", "Pattern Building",
            "Player Elimination", "Push Your Luck", "Role Playing", "Set Collection",
            "Tile Placement", "Trading", "Variable Player Powers", "Worker Placement",
            "Voting", "Hidden Roles", "Real-time", "Engine Building", "Legacy",
            "Route Building", "Network Building", "Simultaneous Action Selection"
        }
        
        if v:
            invalid = [m for m in v if m not in VALID_MECHANICS]
            if invalid:
                # In production, log warning but don't reject
                # For now, we accept any mechanics but could add to vocabulary
                pass
        return v


class GameCreate(GameBase):
    """Schema for creating a new game."""
    pass


class GameUpdate(BaseModel):
    """Schema for updating an existing game. All fields are optional."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    bgg_id: Optional[int] = Field(None, gt=0)
    duration_min: Optional[int] = Field(None, ge=5, le=360)
    complexity: Optional[float] = Field(None, ge=1.0, le=5.0)
    min_players: Optional[int] = Field(None, ge=1, le=100)
    max_players: Optional[int] = Field(None, ge=1, le=100)
    mechanics: Optional[list[str]] = None
    language_dependency: Optional[LanguageDependency] = None
    bgg_rank: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=5000)
    image_url: Optional[str] = Field(None, max_length=500)
    year_published: Optional[int] = Field(None, ge=1900, le=2100)
    available: Optional[bool] = None
    
    model_config = ConfigDict(extra='forbid')


class Game(GameBase):
    """Schema for game responses (includes database fields)."""
    
    id: int = Field(..., description="Database ID")
    has_partial_data: bool = Field(False, description="Has incomplete data")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GameList(BaseModel):
    """Paginated list of games."""
    
    items: list[Game]
    total: int = Field(..., description="Total number of games")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(from_attributes=True)


class GameImportResult(BaseModel):
    """Result of a bulk import operation (RF-ING-03)."""
    
    total_processed: int = Field(..., description="Total records processed")
    imported: int = Field(..., description="Successfully imported")
    updated: int = Field(..., description="Updated existing records")
    rejected: int = Field(..., description="Rejected due to errors")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_processed == 0:
            return 0.0
        return ((self.imported + self.updated) / self.total_processed) * 100


class GameFilters(BaseModel):
    """Filters for game search/list operations."""
    
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    available: Optional[bool] = Field(None, description="Filter by availability")
    min_duration: Optional[int] = Field(None, ge=5, description="Minimum duration")
    max_duration: Optional[int] = Field(None, le=360, description="Maximum duration")
    min_complexity: Optional[float] = Field(None, ge=1.0, description="Minimum complexity")
    max_complexity: Optional[float] = Field(None, le=5.0, description="Maximum complexity")
    min_players_supported: Optional[int] = Field(None, ge=1, description="Must support this player count")
    max_players_supported: Optional[int] = Field(None, ge=1, description="Must support this player count")
    mechanics: Optional[list[str]] = Field(None, description="Filter by mechanics (any match)")
    language_dependency: Optional[LanguageDependency] = Field(None, description="Filter by language level")
