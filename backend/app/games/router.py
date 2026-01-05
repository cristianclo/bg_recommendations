"""
FastAPI router for game CRUD operations.
Implements RF-ING-01, RF-ING-02, and RF-ING-03 endpoints.
"""
import logging
import math
from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.config import settings
from ..schemas.game import (
    Game, GameCreate, GameUpdate, GameList, GameFilters, GameImportResult
)
from .service import GameService
from .import_handler import GameImportHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/games", tags=["games"])
game_service = GameService()
import_handler = GameImportHandler()


@router.post("/", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(
    game_data: GameCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new game in the catalog (RF-ING-01).
    
    Applies normalization rules from RF-ING-02:
    - Duration clamped to 5-360 minutes
    - Complexity clamped to 1.0-5.0
    - Mechanics validated against controlled vocabulary
    - Language dependency as enum
    
    **Requires:** Admin role (to be implemented with auth)
    """
    return game_service.create(db, game_data)


@router.get("/", response_model=GameList)
def list_games(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", pattern="^(name|complexity|duration|rank|created_at)$"),
    # Filters
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    min_duration: Optional[int] = Query(None, ge=5, description="Minimum duration"),
    max_duration: Optional[int] = Query(None, le=360, description="Maximum duration"),
    min_complexity: Optional[float] = Query(None, ge=1.0, description="Minimum complexity"),
    max_complexity: Optional[float] = Query(None, le=5.0, description="Maximum complexity"),
    min_players: Optional[int] = Query(None, ge=1, description="Supports this player count"),
    max_players: Optional[int] = Query(None, ge=1, description="Supports this player count"),
    mechanics: Optional[str] = Query(None, description="Filter by mechanics (comma-separated)"),
    language: Optional[str] = Query(None, description="Filter by language dependency"),
    db: Session = Depends(get_db)
):
    """
    List games with optional filters and pagination.
    
    Supports filtering by:
    - Name (partial match, case-insensitive)
    - Availability at CJEI
    - Duration range
    - Complexity range
    - Player count support
    - Mechanics
    - Language dependency
    
    Results are paginated with configurable page size.
    """
    # Build filters
    filters = GameFilters(
        name=name,
        available=available,
        min_duration=min_duration,
        max_duration=max_duration,
        min_complexity=min_complexity,
        max_complexity=max_complexity,
        min_players_supported=min_players,
        max_players_supported=max_players,
        mechanics=mechanics.split(",") if mechanics else None,
        language_dependency=language if language else None
    )
    
    # Get games
    games, total = game_service.list(db, filters, page, page_size, sort_by)
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return GameList(
        items=games,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/mechanics", response_model=list[str])
def get_mechanics_vocabulary(db: Session = Depends(get_db)):
    """
    Get controlled vocabulary of game mechanics (RF-ING-02).
    
    Returns list of all mechanics currently in use in the catalog.
    Useful for UI autocomplete and validation.
    """
    return game_service.get_mechanics_vocabulary(db)


@router.get("/{game_id}", response_model=Game)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """
    Get a specific game by ID.
    
    Returns complete game details including all normalized attributes.
    """
    return game_service.get_by_id(db, game_id)


@router.put("/{game_id}", response_model=Game)
def update_game(
    game_id: int,
    update_data: GameUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing game.
    
    All fields are optional. Only provided fields will be updated.
    Normalization rules are applied to updated values.
    
    **Requires:** Admin role (to be implemented with auth)
    """
    return game_service.update(db, game_id, update_data)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """
    Delete a game from the catalog.
    
    **Warning:** This operation is permanent and cannot be undone.
    **Requires:** Admin role (to be implemented with auth)
    """
    game_service.delete(db, game_id)


@router.post("/import/csv", response_model=GameImportResult)
async def import_games_csv(
    file: UploadFile = File(..., description="CSV file with game data"),
    merge_strategy: str = Query(
        "update",
        pattern="^(update|skip|replace)$",
        description="Strategy for duplicates: update, skip, or replace"
    ),
    db: Session = Depends(get_db)
):
    """
    Import games from CSV file (RF-ING-03).
    
    **CSV Format:** Expected columns:
    - name (required)
    - bgg_id (required)
    - duration_min
    - complexity
    - min_players
    - max_players
    - mechanics (semicolon-separated)
    - language_dependency
    - bgg_rank
    - description
    - image_url
    - year_published
    - available
    
    **Merge Strategies:**
    - `update`: Update existing games, add new ones (default)
    - `skip`: Skip duplicates, only add new games
    - `replace`: Replace existing games completely
    
    **Validation:** Files with >20% invalid rows are rejected.
    
    **Requires:** Admin role (to be implemented with auth)
    """
    content = await file.read()
    result = import_handler.import_from_csv(db, content, merge_strategy)
    
    logger.info(
        f"CSV import completed: {result.imported} imported, "
        f"{result.updated} updated, {result.rejected} rejected"
    )
    
    return result


@router.post("/import/json", response_model=GameImportResult)
async def import_games_json(
    file: UploadFile = File(..., description="JSON file with game data"),
    merge_strategy: str = Query(
        "update",
        pattern="^(update|skip|replace)$",
        description="Strategy for duplicates: update, skip, or replace"
    ),
    db: Session = Depends(get_db)
):
    """
    Import games from JSON file (RF-ING-03).
    
    **JSON Format:** Array of game objects with same structure as GameCreate schema.
    
    **Merge Strategies:**
    - `update`: Update existing games, add new ones (default)
    - `skip`: Skip duplicates, only add new games
    - `replace`: Replace existing games completely
    
    **Validation:** Files with >20% invalid rows are rejected.
    
    **Requires:** Admin role (to be implemented with auth)
    """
    content = await file.read()
    result = import_handler.import_from_json(db, content, merge_strategy)
    
    logger.info(
        f"JSON import completed: {result.imported} imported, "
        f"{result.updated} updated, {result.rejected} rejected"
    )
    
    return result
