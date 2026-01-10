"""
Game service implementing business logic, normalization, and CRUD operations.
Implements RF-ING-01 and RF-ING-02 requirements.
"""
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from ..models.game import Game, LanguageDependency
from ..schemas.game import GameCreate, GameUpdate, GameFilters
from ..core.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class GameService:
    """
    Service for game management with normalization logic.
    Implements RF-ING-02 normalization rules.
    """
    
    # Normalization constants (RF-ING-02)
    MIN_DURATION = 5
    MAX_DURATION = 360
    DEFAULT_DURATION = 60
    
    MIN_COMPLEXITY = 1.0
    MAX_COMPLEXITY = 5.0
    DEFAULT_COMPLEXITY = 2.5
    
    # Controlled vocabulary for mechanics (RF-ING-02)
    STANDARD_MECHANICS = {
        "Action Points", "Area Control", "Auction/Bidding", "Card Drafting",
        "Cooperative Play", "Deck Building", "Dice Rolling", "Grid Movement",
        "Hand Management", "Memory", "Modular Board", "Pattern Building",
        "Player Elimination", "Push Your Luck", "Role Playing", "Set Collection",
        "Tile Placement", "Trading", "Variable Player Powers", "Worker Placement",
        "Voting", "Hidden Roles", "Real-time", "Engine Building", "Legacy",
        "Route Building", "Network Building", "Simultaneous Action Selection",
        "Storytelling", "Bluffing", "Deduction", "Take That", "Negotiation",
        "Race", "Trick-taking", "Drafting", "Partnerships", "Action Queue",
        "Action Retrieval", "Advantage Token", "Alliances", "Auction Compensation",
        "Betting and Bluffing", "Bingo", "Campaign / Battle Card Driven",
        "Catch the Leader", "Chit-Pull System", "Command Cards", "Connections",
        "Constrained Bidding", "Contracts", "Crayon Rail System", "Cube Tower",
        "Deck Construction", "Dexterity", "Die Icon Resolution", "Elapsed Real Time Ending"
    }
    
    @staticmethod
    def normalize_duration(duration: Optional[int]) -> int:
        """
        Normalize duration to valid range (RF-ING-02).
        Clamps to 5-360 minutes, defaults to 60 if missing.
        """
        if duration is None:
            logger.warning("Duration missing, using default: 60")
            return GameService.DEFAULT_DURATION
        
        if duration < GameService.MIN_DURATION:
            logger.warning(f"Duration {duration} below minimum, clamping to {GameService.MIN_DURATION}")
            return GameService.MIN_DURATION
        
        if duration > GameService.MAX_DURATION:
            logger.warning(f"Duration {duration} above maximum, clamping to {GameService.MAX_DURATION}")
            return GameService.MAX_DURATION
        
        return duration
    
    @staticmethod
    def normalize_complexity(complexity: Optional[float]) -> float:
        """
        Normalize complexity to valid range (RF-ING-02).
        Clamps to 1.0-5.0, defaults to 2.5 if missing.
        """
        if complexity is None:
            logger.warning("Complexity missing, using default: 2.5")
            return GameService.DEFAULT_COMPLEXITY
        
        if complexity < GameService.MIN_COMPLEXITY:
            logger.warning(f"Complexity {complexity} below minimum, clamping to {GameService.MIN_COMPLEXITY}")
            return GameService.MIN_COMPLEXITY
        
        if complexity > GameService.MAX_COMPLEXITY:
            logger.warning(f"Complexity {complexity} above maximum, clamping to {GameService.MAX_COMPLEXITY}")
            return GameService.MAX_COMPLEXITY
        
        return complexity
    
    @staticmethod
    def normalize_mechanics(mechanics: list[str]) -> list[str]:
        """
        Normalize mechanics against controlled vocabulary (RF-ING-02).
        Returns normalized list and logs warnings for unknown mechanics.
        """
        if not mechanics:
            return []
        
        normalized = []
        unknown = []
        
        for mechanic in mechanics:
            # Case-insensitive matching
            mechanic_clean = mechanic.strip()
            found = False
            
            for standard in GameService.STANDARD_MECHANICS:
                if mechanic_clean.lower() == standard.lower():
                    normalized.append(standard)
                    found = True
                    break
            
            if not found:
                unknown.append(mechanic_clean)
                # Still include unknown mechanics but log warning
                normalized.append(mechanic_clean)
        
        if unknown:
            logger.warning(f"Unknown mechanics detected: {unknown}")
        
        return list(set(normalized))  # Remove duplicates
    
    @staticmethod
    def validate_player_range(min_players: int, max_players: int) -> tuple[int, int]:
        """Validate and correct player range if needed."""
        if min_players > max_players:
            logger.warning(f"min_players ({min_players}) > max_players ({max_players}), swapping")
            return max_players, min_players
        
        if min_players < 1:
            logger.warning(f"min_players ({min_players}) < 1, setting to 1")
            min_players = 1
        
        if max_players < 1:
            logger.warning(f"max_players ({max_players}) < 1, setting to 1")
            max_players = 1
        
        return min_players, max_players
    
    def create(self, db: Session, game_data: GameCreate) -> Game:
        """
        Create a new game with normalization (RF-ING-01, RF-ING-02).
        """
        # Check for duplicate bgg_id
        existing = db.query(Game).filter(Game.bgg_id == game_data.bgg_id).first()
        if existing:
            raise BadRequestException(f"Game with BGG ID {game_data.bgg_id} already exists")
        
        # Apply normalization
        normalized_data = game_data.model_dump()
        normalized_data['duration_min'] = self.normalize_duration(normalized_data['duration_min'])
        normalized_data['complexity'] = self.normalize_complexity(normalized_data['complexity'])
        normalized_data['mechanics'] = self.normalize_mechanics(normalized_data['mechanics'])
        
        # Validate player range
        min_p, max_p = self.validate_player_range(
            normalized_data['min_players'],
            normalized_data['max_players']
        )
        normalized_data['min_players'] = min_p
        normalized_data['max_players'] = max_p
        
        # Determine if data is partial (RF-ING-01)
        has_partial = (
            not normalized_data.get('description') or
            not normalized_data.get('image_url') or
            not normalized_data.get('mechanics') or
            normalized_data.get('bgg_rank') is None
        )
        normalized_data['has_partial_data'] = has_partial
        
        # Create game
        game = Game(**normalized_data)
        db.add(game)
        db.commit()
        db.refresh(game)
        
        logger.info(f"Created game: {game.name} (BGG ID: {game.bgg_id})")
        return game
    
    def get_by_id(self, db: Session, game_id: int) -> Game:
        """Get game by database ID."""
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise NotFoundException("Game", str(game_id))
        return game
    
    def get_by_bgg_id(self, db: Session, bgg_id: int) -> Optional[Game]:
        """Get game by BoardGameGeek ID."""
        return db.query(Game).filter(Game.bgg_id == bgg_id).first()
    
    def list(
        self,
        db: Session,
        filters: Optional[GameFilters] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "name"
    ) -> tuple[list[Game], int]:
        """
        List games with optional filters and pagination.
        Returns (games, total_count).
        """
        query = db.query(Game)
        
        # Apply filters
        if filters:
            if filters.name:
                query = query.filter(Game.name.ilike(f"%{filters.name}%"))
            
            if filters.available is not None:
                query = query.filter(Game.available == filters.available)
            
            if filters.min_duration:
                query = query.filter(Game.duration_min >= filters.min_duration)
            
            if filters.max_duration:
                query = query.filter(Game.duration_min <= filters.max_duration)
            
            if filters.min_complexity:
                query = query.filter(Game.complexity >= filters.min_complexity)
            
            if filters.max_complexity:
                query = query.filter(Game.complexity <= filters.max_complexity)
            
            if filters.min_players_supported:
                query = query.filter(
                    and_(
                        Game.min_players <= filters.min_players_supported,
                        Game.max_players >= filters.min_players_supported
                    )
                )
            
            if filters.max_players_supported:
                query = query.filter(
                    and_(
                        Game.min_players <= filters.max_players_supported,
                        Game.max_players >= filters.max_players_supported
                    )
                )
            
            if filters.mechanics:
                # Match any of the specified mechanics
                mechanic_filters = [
                    Game.mechanics.contains([mechanic]) for mechanic in filters.mechanics
                ]
                query = query.filter(or_(*mechanic_filters))
            
            if filters.language_dependency:
                query = query.filter(Game.language_dependency == filters.language_dependency)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if sort_by == "name":
            query = query.order_by(Game.name)
        elif sort_by == "complexity":
            query = query.order_by(Game.complexity)
        elif sort_by == "duration":
            query = query.order_by(Game.duration_min)
        elif sort_by == "rank":
            query = query.order_by(Game.bgg_rank.nulls_last())
        elif sort_by == "created_at":
            query = query.order_by(Game.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        games = query.offset(offset).limit(page_size).all()
        
        return games, total
    
    def update(self, db: Session, game_id: int, update_data: GameUpdate) -> Game:
        """Update game with normalization."""
        game = self.get_by_id(db, game_id)
        
        # Get only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Apply normalization to updated fields
        if 'duration_min' in update_dict:
            update_dict['duration_min'] = self.normalize_duration(update_dict['duration_min'])
        
        if 'complexity' in update_dict:
            update_dict['complexity'] = self.normalize_complexity(update_dict['complexity'])
        
        if 'mechanics' in update_dict:
            update_dict['mechanics'] = self.normalize_mechanics(update_dict['mechanics'])
        
        # Validate player range if both are being updated
        if 'min_players' in update_dict or 'max_players' in update_dict:
            min_p = update_dict.get('min_players', game.min_players)
            max_p = update_dict.get('max_players', game.max_players)
            min_p, max_p = self.validate_player_range(min_p, max_p)
            update_dict['min_players'] = min_p
            update_dict['max_players'] = max_p
        
        # Update game
        for key, value in update_dict.items():
            setattr(game, key, value)
        
        db.commit()
        db.refresh(game)
        
        logger.info(f"Updated game: {game.name} (ID: {game.id})")
        return game
    
    def delete(self, db: Session, game_id: int) -> None:
        """Delete game by ID."""
        game = self.get_by_id(db, game_id)
        db.delete(game)
        db.commit()
        logger.info(f"Deleted game: {game.name} (ID: {game.id})")
    
    def get_mechanics_vocabulary(self, db: Session) -> list:
        """
        Get list of all mechanics currently in use in the catalog.
        Useful for UI autocomplete and validation.
        """
        # Get all unique mechanics from database
        result = db.query(Game.mechanics).distinct().all()
        mechanics_set = set()
        
        for (mechanics_list,) in result:
            if mechanics_list:
                mechanics_set.update(mechanics_list)
        
        return sorted(list(mechanics_set))
