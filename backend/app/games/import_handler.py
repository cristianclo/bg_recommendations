"""
Game import handler for CSV and JSON files (RF-ING-03).
Handles bulk import with validation, duplicate detection, and merge strategies.
"""
import csv
import json
import logging
from io import StringIO
from typing import Literal
from sqlalchemy.orm import Session

from ..models.game import LanguageDependency
from ..schemas.game import GameCreate, GameImportResult
from .service import GameService

logger = logging.getLogger(__name__)


class GameImportHandler:
    """Handles bulk import of games from CSV/JSON files."""
    
    def __init__(self):
        self.game_service = GameService()
        self.MAX_REJECTION_RATE = 0.20  # 20% max rejection rate (RF-ING-03)
    
    def import_from_csv(
        self,
        db: Session,
        csv_content: bytes,
        merge_strategy: Literal["update", "skip", "replace"] = "update"
    ) -> GameImportResult:
        """
        Import games from CSV file (RF-ING-03).
        
        Args:
            db: Database session
            csv_content: CSV file content as bytes
            merge_strategy: How to handle duplicates (update/skip/replace)
            
        Returns:
            GameImportResult with statistics and errors
        """
        result = GameImportResult(
            total_processed=0,
            imported=0,
            updated=0,
            rejected=0,
            warnings=[],
            errors=[]
        )
        
        try:
            # Decode CSV content
            csv_text = csv_content.decode('utf-8')
            csv_file = StringIO(csv_text)
            reader = csv.DictReader(csv_file)
            
            # Validate CSV structure
            required_columns = {'name', 'bgg_id'}
            if not reader.fieldnames:
                result.errors.append("CSV file is empty or has no headers")
                return result
            
            missing_columns = required_columns - set(reader.fieldnames)
            if missing_columns:
                result.errors.append(f"Missing required columns: {missing_columns}")
                return result
            
            # Process each row
            rows = list(reader)
            result.total_processed = len(rows)
            
            for idx, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
                try:
                    game_data = self._parse_csv_row(row)
                    self._process_game_import(db, game_data, merge_strategy, result)
                    
                except Exception as e:
                    result.rejected += 1
                    error_msg = f"Row {idx}: {str(e)}"
                    result.errors.append(error_msg)
                    logger.error(error_msg)
            
            # Check rejection rate (RF-ING-03)
            if result.total_processed > 0:
                rejection_rate = result.rejected / result.total_processed
                if rejection_rate > self.MAX_REJECTION_RATE:
                    db.rollback()
                    result.errors.insert(
                        0,
                        f"Import rejected: {rejection_rate:.1%} of rows invalid "
                        f"(threshold: {self.MAX_REJECTION_RATE:.1%})"
                    )
                    result.imported = 0
                    result.updated = 0
                    return result
            
            db.commit()
            logger.info(f"CSV import successful: {result.imported} imported, {result.updated} updated")
            
        except Exception as e:
            db.rollback()
            result.errors.append(f"CSV parsing error: {str(e)}")
            logger.error(f"CSV import failed: {e}", exc_info=True)
        
        return result
    
    def import_from_json(
        self,
        db: Session,
        json_content: bytes,
        merge_strategy: Literal["update", "skip", "replace"] = "update"
    ) -> GameImportResult:
        """
        Import games from JSON file (RF-ING-03).
        
        Args:
            db: Database session
            json_content: JSON file content as bytes
            merge_strategy: How to handle duplicates (update/skip/replace)
            
        Returns:
            GameImportResult with statistics and errors
        """
        result = GameImportResult(
            total_processed=0,
            imported=0,
            updated=0,
            rejected=0,
            warnings=[],
            errors=[]
        )
        
        try:
            # Parse JSON
            json_text = json_content.decode('utf-8')
            games_data = json.loads(json_text)
            
            if not isinstance(games_data, list):
                result.errors.append("JSON must be an array of game objects")
                return result
            
            result.total_processed = len(games_data)
            
            # Process each game
            for idx, game_dict in enumerate(games_data, start=1):
                try:
                    # Validate with Pydantic
                    game_data = GameCreate(**game_dict)
                    self._process_game_import(db, game_data, merge_strategy, result)
                    
                except Exception as e:
                    result.rejected += 1
                    error_msg = f"Item {idx}: {str(e)}"
                    result.errors.append(error_msg)
                    logger.error(error_msg)
            
            # Check rejection rate (RF-ING-03)
            if result.total_processed > 0:
                rejection_rate = result.rejected / result.total_processed
                if rejection_rate > self.MAX_REJECTION_RATE:
                    db.rollback()
                    result.errors.insert(
                        0,
                        f"Import rejected: {rejection_rate:.1%} of items invalid "
                        f"(threshold: {self.MAX_REJECTION_RATE:.1%})"
                    )
                    result.imported = 0
                    result.updated = 0
                    return result
            
            db.commit()
            logger.info(f"JSON import successful: {result.imported} imported, {result.updated} updated")
            
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON format: {str(e)}")
            logger.error(f"JSON parsing failed: {e}")
        except Exception as e:
            db.rollback()
            result.errors.append(f"Import error: {str(e)}")
            logger.error(f"JSON import failed: {e}", exc_info=True)
        
        return result
    
    def _parse_csv_row(self, row: dict) -> GameCreate:
        """
        Parse CSV row into GameCreate schema.
        Handles type conversions and default values.
        """
        # Parse mechanics (semicolon-separated)
        mechanics_str = row.get('mechanics', '')
        mechanics = [m.strip() for m in mechanics_str.split(';') if m.strip()] if mechanics_str else []
        
        # Parse language dependency
        lang_dep = row.get('language_dependency', 'baja').lower()
        try:
            language_dependency = LanguageDependency(lang_dep)
        except ValueError:
            language_dependency = LanguageDependency.BAJA
        
        # Parse boolean
        available = row.get('available', 'true').lower() in ('true', '1', 'yes', 'si', 'sí')
        
        # Build game data
        game_data = GameCreate(
            name=row['name'].strip(),
            bgg_id=int(row['bgg_id']),
            duration_min=int(row.get('duration_min', 60)),
            complexity=float(row.get('complexity', 2.5)),
            min_players=int(row.get('min_players', 2)),
            max_players=int(row.get('max_players', 4)),
            mechanics=mechanics,
            language_dependency=language_dependency,
            bgg_rank=int(row['bgg_rank']) if row.get('bgg_rank') else None,
            description=row.get('description'),
            image_url=row.get('image_url'),
            year_published=int(row['year_published']) if row.get('year_published') else None,
            available=available
        )
        
        return game_data
    
    def _process_game_import(
        self,
        db: Session,
        game_data: GameCreate,
        merge_strategy: str,
        result: GameImportResult
    ):
        """
        Process a single game import with duplicate detection and merge strategy.
        
        Args:
            db: Database session
            game_data: Validated game data
            merge_strategy: How to handle duplicates
            result: Result object to update
        """
        # Check for duplicate by BGG ID (RF-ING-03)
        existing_game = self.game_service.get_by_bgg_id(db, game_data.bgg_id)
        
        if existing_game:
            # Handle duplicate based on strategy
            if merge_strategy == "skip":
                result.warnings.append(
                    f"Skipped duplicate: {game_data.name} (BGG ID: {game_data.bgg_id})"
                )
                return
            
            elif merge_strategy == "update":
                # Update only new/changed fields
                update_dict = game_data.model_dump(exclude_unset=True)
                for key, value in update_dict.items():
                    if value is not None:  # Only update non-null values
                        setattr(existing_game, key, value)
                
                # Apply normalization
                existing_game.duration_min = self.game_service.normalize_duration(
                    existing_game.duration_min
                )
                existing_game.complexity = self.game_service.normalize_complexity(
                    existing_game.complexity
                )
                existing_game.mechanics = self.game_service.normalize_mechanics(
                    existing_game.mechanics
                )
                
                db.commit()
                result.updated += 1
                logger.debug(f"Updated game: {game_data.name} (BGG ID: {game_data.bgg_id})")
            
            elif merge_strategy == "replace":
                # Delete and recreate
                db.delete(existing_game)
                db.flush()
                
                new_game = self.game_service.create(db, game_data)
                result.updated += 1
                logger.debug(f"Replaced game: {game_data.name} (BGG ID: {game_data.bgg_id})")
        
        else:
            # Create new game
            self.game_service.create(db, game_data)
            result.imported += 1
            logger.debug(f"Imported new game: {game_data.name} (BGG ID: {game_data.bgg_id})")
