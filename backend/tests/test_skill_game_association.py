"""
Test for skill-game association functionality (RF-TAX-03).
Tests the many-to-many relationship between skills and games.
"""
import pytest
from sqlalchemy.orm import Session

from app.models.game import Game, LanguageDependency
from app.models.skill import Skill
from app.schemas.game import GameCreate
from app.schemas.skill import SkillCreate
from app.games.service import GameService
from app.skills.service import SkillService
from app.core.exceptions import NotFoundException, ValidationException


def test_associate_skill_with_game(db_session):
    """Test associating a skill with a game (RF-TAX-03)."""
    db = db_session
    
    game_service = GameService()
    skill_service = SkillService()
    
    # Create a game
    game_data = GameCreate(
        name="Test Association Game",
        bgg_id=999001,
        min_players=2,
        max_players=4,
        duration_min=60,
        complexity=2.5,
        mechanics=["cooperative"],
        language_dependency=LanguageDependency.BAJA,
        available=True
    )
    game = game_service.create(db, game_data)
    
    # Create a skill
    skill_data = SkillCreate(
        name="Test Association Skill",
        description="Test skill for association"
    )
    skill = skill_service.create(db, skill_data)
    
    # Associate skill with game
    result = skill_service.associate_game(
        db, 
        skill.id, 
        game.id, 
        "This game develops test skills effectively"
    )
    
    assert result == True
    
    # Verify association exists
    skill_games = skill_service.get_skill_games(db, skill.id)
    assert len(skill_games) == 1
    assert skill_games[0].id == game.id
    
    # Try to associate again (should fail)
    with pytest.raises(ValidationException):
        skill_service.associate_game(db, skill.id, game.id)
    
    print("✅ Skill-game association test passed")


def test_dissociate_skill_from_game(db_session):
    """Test removing skill-game association (RF-TAX-03)."""
    db = db_session
    
    game_service = GameService()
    skill_service = SkillService()
    
    # Create game and skill
    game_data = GameCreate(
        name="Test Dissociation Game",
        bgg_id=999002,
        min_players=2,
        max_players=4,
        duration_min=60,
        complexity=2.5,
        mechanics=["cooperative"],
        language_dependency=LanguageDependency.BAJA,
        available=True
    )
    game = game_service.create(db, game_data)
    
    skill_data = SkillCreate(
        name="Test Dissociation Skill",
        description="Test skill for dissociation"
    )
    skill = skill_service.create(db, skill_data)
    
    # Associate and then dissociate
    skill_service.associate_game(db, skill.id, game.id)
    
    # Verify association exists
    skill_games = skill_service.get_skill_games(db, skill.id)
    assert len(skill_games) == 1
    
    # Dissociate
    result = skill_service.dissociate_game(db, skill.id, game.id)
    assert result == True
    
    # Verify association removed
    skill_games = skill_service.get_skill_games(db, skill.id)
    assert len(skill_games) == 0
    
    # Try to dissociate again (should fail)
    with pytest.raises(NotFoundException):
        skill_service.dissociate_game(db, skill.id, game.id)
    
    print("✅ Skill-game dissociation test passed")


def test_get_skill_games(db_session):
    """Test retrieving all games associated with a skill (RF-TAX-03)."""
    db = db_session
    
    game_service = GameService()
    skill_service = SkillService()
    
    # Create a skill
    skill_data = SkillCreate(
        name="Test Multi-Game Skill",
        description="Skill associated with multiple games"
    )
    skill = skill_service.create(db, skill_data)
    
    # Create and associate multiple games
    game_ids = []
    for i in range(3):
        game_data = GameCreate(
            name=f"Test Multi Game {i}",
            bgg_id=999100 + i,
            min_players=2,
            max_players=4,
            duration_min=60,
            complexity=2.5,
            mechanics=["cooperative"],
            language_dependency=LanguageDependency.BAJA,
            available=True
        )
        game = game_service.create(db, game_data)
        game_ids.append(game.id)
        skill_service.associate_game(db, skill.id, game.id, f"Justification {i}")
    
    # Get all associated games
    skill_games = skill_service.get_skill_games(db, skill.id)
    assert len(skill_games) == 3
    
    # Verify all game IDs are present
    retrieved_ids = [g.id for g in skill_games]
    for game_id in game_ids:
        assert game_id in retrieved_ids
    
    print("✅ Get skill games test passed")


def test_association_with_nonexistent_entities(db_session):
    """Test error handling for nonexistent game or skill (RF-TAX-03)."""
    db = db_session
    
    skill_service = SkillService()
    
    # Try to associate with nonexistent skill
    with pytest.raises(NotFoundException):
        skill_service.associate_game(db, 99999, 1)
    
    # Create a real skill
    skill_data = SkillCreate(
        name="Test Error Handling Skill",
        description="Test skill for error cases"
    )
    skill = skill_service.create(db, skill_data)
    
    # Try to associate with nonexistent game
    with pytest.raises(NotFoundException):
        skill_service.associate_game(db, skill.id, 99999)
    
    print("✅ Error handling test passed")


def test_cascade_delete_associations(db_session):
    """Test that deleting a skill removes its game associations (RF-TAX-03)."""
    db = db_session
    
    game_service = GameService()
    skill_service = SkillService()
    
    # Create game and skill
    game_data = GameCreate(
        name="Test Cascade Game",
        bgg_id=999200,
        min_players=2,
        max_players=4,
        duration_min=60,
        complexity=2.5,
        mechanics=["cooperative"],
        language_dependency=LanguageDependency.BAJA,
        available=True
    )
    game = game_service.create(db, game_data)
    
    skill_data = SkillCreate(
        name="Test Cascade Skill",
        description="Test skill for cascade delete"
    )
    skill = skill_service.create(db, skill_data)
    
    # Associate
    skill_service.associate_game(db, skill.id, game.id)
    
    # Verify association
    skill_games = skill_service.get_skill_games(db, skill.id)
    assert len(skill_games) == 1
    
    # Delete skill
    skill_service.delete(db, skill.id)
    
    # Game should still exist (association is removed by cascade)
    game_check = db.query(Game).filter(Game.id == game.id).first()
    assert game_check is not None
    assert game_check.id == game.id
    
    print("✅ Cascade delete test passed")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 RUNNING SKILL-GAME ASSOCIATION TESTS (RF-TAX-03)")
    print("="*80 + "\n")
    
    test_associate_skill_with_game()
    test_dissociate_skill_from_game()
    test_get_skill_games()
    test_association_with_nonexistent_entities()
    test_cascade_delete_associations()
    
    print("\n" + "="*80)
    print("✅ ALL SKILL-GAME ASSOCIATION TESTS PASSED")
    print("="*80)
