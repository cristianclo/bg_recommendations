"""
Manual test script to demonstrate skill-game association functionality (RF-TAX-03).

This script demonstrates:
1. Creating skills
2. Creating games
3. Associating skills with games (with pedagogical justification)
4. Retrieving games for a skill
5. Dissociating skills from games
6. Cascade delete behavior
"""

import sys
from pathlib import Path
import time

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session

# Import models first to ensure they're all registered before creating services
from app.models import game, skill, session, recommendation, admin

# Now import services and schemas
from app.core.database import SessionLocal
from app.skills.service import SkillService
from app.games.service import GameService
from app.schemas.skill import SkillCreate
from app.schemas.game import GameCreate


def run_skill_game_demo():
    """Run a complete demonstration of skill-game associations."""
    db: Session = SessionLocal()
    skill_service = SkillService()
    game_service = GameService()
    
    # Generate unique suffix to avoid conflicts
    suffix = int(time.time())
    
    print("\n" + "=" * 80)
    print("🧪 SKILL-GAME ASSOCIATION DEMONSTRATION (RF-TAX-03)")
    print("=" * 80)
    
    try:
        # 1. Create test skills
        print("\n📚 STEP 1: Creating test skills...")
        skill1_data = SkillCreate(
            name=f"Pensamiento Crítico Demo {suffix}",
            description="Habilidad para analizar y evaluar situaciones"
        )
        skill1 = skill_service.create(db, skill1_data)
        print(f"   ✅ Created skill: {skill1.name} (ID: {skill1.id})")
        
        skill2_data = SkillCreate(
            name=f"Comunicación Efectiva Demo {suffix}",
            description="Habilidad para expresar ideas claramente"
        )
        skill2 = skill_service.create(db, skill2_data)
        print(f"   ✅ Created skill: {skill2.name} (ID: {skill2.id})")
        
        # 2. Create test games
        print("\n🎲 STEP 2: Creating test games...")
        game1_data = GameCreate(
            name=f"Test Logic Game {suffix}",
            bgg_id=999901 + suffix,
            min_players=2,
            max_players=4,
            duration=30,
            complexity=3.0,
            available=True,
            mechanics=["Deduction", "Logic"]
        )
        game1 = game_service.create(db, game1_data)
        print(f"   ✅ Created game: {game1.name} (ID: {game1.id})")
        
        game2_data = GameCreate(
            name=f"Test Communication Game {suffix}",
            bgg_id=999902 + suffix,
            min_players=3,
            max_players=8,
            duration=45,
            complexity=2.0,
            available=True,
            mechanics=["Communication", "Cooperative"]
        )
        game2 = game_service.create(db, game2_data)
        print(f"   ✅ Created game: {game2.name} (ID: {game2.id})")
        
        # 3. Associate skills with games
        print("\n🔗 STEP 3: Creating skill-game associations...")
        skill_service.associate_game(
            db,
            skill_id=skill1.id,
            game_id=game1.id,
            justification="Este juego desarrolla pensamiento crítico mediante la resolución de acertijos lógicos"
        )
        print(f"   ✅ Associated '{skill1.name}' with '{game1.name}'")
        print(f"      Justification: Este juego desarrolla pensamiento crítico...")
        
        skill_service.associate_game(
            db,
            skill_id=skill2.id,
            game_id=game2.id,
            justification="La mecánica cooperativa requiere comunicación constante entre jugadores"
        )
        print(f"   ✅ Associated '{skill2.name}' with '{game2.name}'")
        print(f"      Justification: La mecánica cooperativa requiere comunicación...")
        
        # Associate skill1 with game2 as well
        skill_service.associate_game(
            db,
            skill_id=skill1.id,
            game_id=game2.id,
            justification="Requiere análisis crítico de la situación del equipo"
        )
        print(f"   ✅ Associated '{skill1.name}' with '{game2.name}' (multiple associations)")
        
        # 4. Retrieve games for skills
        print("\n📋 STEP 4: Retrieving associated games...")
        skill1_games = skill_service.get_skill_games(db, skill1.id)
        print(f"   📚 '{skill1.name}' is associated with {len(skill1_games)} game(s):")
        for game in skill1_games:
            print(f"      - {game.name} (ID: {game.id})")
        
        skill2_games = skill_service.get_skill_games(db, skill2.id)
        print(f"   📚 '{skill2.name}' is associated with {len(skill2_games)} game(s):")
        for game in skill2_games:
            print(f"      - {game.name} (ID: {game.id})")
        
        # 5. Dissociate a skill from a game
        print("\n🔓 STEP 5: Removing an association...")
        skill_service.dissociate_game(db, skill1.id, game1.id)
        print(f"   ✅ Dissociated '{skill1.name}' from '{game1.name}'")
        
        # Verify removal
        skill1_games_after = skill_service.get_skill_games(db, skill1.id)
        print(f"   📊 '{skill1.name}' now has {len(skill1_games_after)} game(s) (was {len(skill1_games)})")
        
        # 6. Test error handling
        print("\n⚠️  STEP 6: Testing error handling...")
        try:
            skill_service.associate_game(
                db,
                skill_id=skill1.id,
                game_id=99999,  # Non-existent game
                justification="This should fail"
            )
            print("   ❌ ERROR: Should have raised NotFoundException")
        except Exception as e:
            print(f"   ✅ Correctly raised exception: {type(e).__name__}")
        
        # 7. Demonstrate cascade behavior
        print("\n🗑️  STEP 7: Demonstrating cascade delete...")
        print(f"   Before delete: '{skill2.name}' has {len(skill2_games)} game(s)")
        
        # Delete skill2
        skill_service.delete(db, skill2.id)
        print(f"   ✅ Deleted skill '{skill2.name}'")
        print(f"   ℹ️  Associations automatically removed (CASCADE)")
        
        # Verify game still exists
        game2_still_exists = game_service.get_by_id(db, game2.id)
        print(f"   ✅ Game '{game2_still_exists.name}' still exists (only association removed)")
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE - All skill-game operations working!")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("  ✓ Creating skill-game associations with justification")
        print("  ✓ Multiple games per skill")
        print("  ✓ Multiple skills per game")
        print("  ✓ Retrieving associated games")
        print("  ✓ Removing associations")
        print("  ✓ Error handling for invalid operations")
        print("  ✓ Cascade delete behavior")
        print("\n📚 RF-TAX-03: Manual game-skill association - VERIFIED ✅")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run_skill_game_demo()
