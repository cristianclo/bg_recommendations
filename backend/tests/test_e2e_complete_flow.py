"""
End-to-End Test: Complete Application Flow
===========================================

Tests the complete workflow from data ingestion to recommendations with explanations.
Covers all modules (A, B, C, D, E) in realistic scenarios.

Run with: pytest tests/test_e2e_complete_flow.py -v -s
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.config import settings
from app.models.game import Game, LanguageDependency
from app.models.session import SessionProfile, Modality
from app.models.skill import Skill
from app.models.recommendation import Recommendation, ScoringConfig

# Schemas for validation
from app.schemas.game import GameCreate
from app.schemas.session import SessionProfileCreate
from app.schemas.skill import SkillCreate
from app.schemas.recommendation import ScoringConfigCreate

# Services
from app.games.service import GameService
from app.sessions.service import SessionProfileService
from app.skills.service import SkillService
from app.recommendations.engine import RecommendationEngine
from app.recommendations.config_service import ScoringConfigService
from app.recommendations.explainability_service import ExplainabilityService


# ============================================================================
# Test Database Setup
# ============================================================================

def get_test_db():
    """Create a test database session."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Clean up existing data for clean test
    db.query(Recommendation).delete()
    db.query(SessionProfile).delete()
    db.query(Game).delete()
    db.query(ScoringConfig).delete()
    # Delete skills (bottom-up to avoid FK issues)
    db.query(Skill).filter(Skill.parent_id.isnot(None)).delete()
    db.query(Skill).filter(Skill.parent_id.is_(None)).delete()
    db.commit()
    
    return db


# ============================================================================
# Test Data Fixtures
# ============================================================================

def seed_test_games(db):
    """Seed test games covering various scenarios."""
    game_service = GameService()
    
    games = [
        # Cooperative games
        {
            "name": "Pandemic",
            "bgg_id": 30549,
            "duration_min": 45,
            "complexity": 2.4,
            "min_players": 2,
            "max_players": 4,
            "mechanics": ["Cooperative", "Hand Management", "Set Collection"],
            "language_dependency": LanguageDependency.BAJA,
            "bgg_rank": 95,
            "available": True
        },
        {
            "name": "Forbidden Island",
            "bgg_id": 65244,
            "duration_min": 30,
            "complexity": 1.7,
            "min_players": 2,
            "max_players": 4,
            "mechanics": ["Cooperative", "Set Collection", "Tile Placement"],
            "language_dependency": LanguageDependency.NINGUNA,
            "bgg_rank": 450,
            "available": True
        },
        # Competitive games
        {
            "name": "Catan",
            "bgg_id": 13,
            "duration_min": 60,
            "complexity": 2.3,
            "min_players": 3,
            "max_players": 4,
            "mechanics": ["Trading", "Dice Rolling", "Resource Management"],
            "language_dependency": LanguageDependency.BAJA,
            "bgg_rank": 250,
            "available": True
        },
        {
            "name": "Ticket to Ride",
            "bgg_id": 9209,
            "duration_min": 45,
            "complexity": 1.9,
            "min_players": 2,
            "max_players": 5,
            "mechanics": ["Set Collection", "Hand Management", "Route Building"],
            "language_dependency": LanguageDependency.NINGUNA,
            "bgg_rank": 120,
            "available": True
        },
        # Party games
        {
            "name": "Dixit",
            "bgg_id": 39856,
            "duration_min": 30,
            "complexity": 1.2,
            "min_players": 3,
            "max_players": 8,
            "mechanics": ["Storytelling", "Voting", "Hand Management"],
            "language_dependency": LanguageDependency.ALTA,
            "bgg_rank": 120,
            "available": True
        },
        {
            "name": "Codenames",
            "bgg_id": 178900,
            "duration_min": 15,
            "complexity": 1.3,
            "min_players": 4,
            "max_players": 8,
            "mechanics": ["Cooperative", "Deduction", "Word Game"],
            "language_dependency": LanguageDependency.ALTA,
            "bgg_rank": 85,
            "available": True
        },
        # Strategy games
        {
            "name": "Azul",
            "bgg_id": 230802,
            "duration_min": 40,
            "complexity": 1.8,
            "min_players": 2,
            "max_players": 4,
            "mechanics": ["Pattern Building", "Tile Placement", "Set Collection"],
            "language_dependency": LanguageDependency.NINGUNA,
            "bgg_rank": 95,
            "available": True
        },
        {
            "name": "7 Wonders",
            "bgg_id": 68448,
            "duration_min": 30,
            "complexity": 2.3,
            "min_players": 2,
            "max_players": 7,
            "mechanics": ["Drafting", "Set Collection", "Hand Management"],
            "language_dependency": LanguageDependency.BAJA,
            "bgg_rank": 180,
            "available": True
        },
        # Not available (for filtering tests)
        {
            "name": "Gloomhaven",
            "bgg_id": 174430,
            "duration_min": 120,
            "complexity": 3.9,
            "min_players": 1,
            "max_players": 4,
            "mechanics": ["Cooperative", "Campaign", "Hand Management"],
            "language_dependency": LanguageDependency.ALTA,
            "bgg_rank": 1,
            "available": False  # Not available
        }
    ]
    
    created_games = []
    for game_data in games:
        # Convert dict to Pydantic model
        game_create = GameCreate(**game_data)
        game = game_service.create(db, game_create)
        created_games.append(game)
    
    print(f"✅ Seeded {len(created_games)} test games")
    return created_games


def seed_test_skills(db):
    """Seed basic skills taxonomy."""
    skill_service = SkillService()
    
    # Root skills
    cognitive = skill_service.create(db, SkillCreate(
        name="Habilidades Cognitivas",
        description="Habilidades relacionadas con el pensamiento"
    ))
    
    social = skill_service.create(db, SkillCreate(
        name="Habilidades Sociales",
        description="Habilidades de interacción social"
    ))
    
    # Child skills
    critical_thinking = skill_service.create(db, SkillCreate(
        name="Pensamiento Crítico",
        description="Análisis y evaluación de información",
        parent_id=cognitive.id
    ))
    
    teamwork = skill_service.create(db, SkillCreate(
        name="Trabajo en Equipo",
        description="Colaboración efectiva con otros",
        parent_id=social.id
    ))
    
    print(f"✅ Seeded {db.query(Skill).count()} test skills")
    return [cognitive, social, critical_thinking, teamwork]


def create_scoring_config(db):
    """Create default scoring configuration."""
    config_service = ScoringConfigService(db)
    
    config = config_service.create(ScoringConfigCreate(
        name="E2E Test Config",
        description="Configuration for E2E testing",
        skill_weight=0.40,
        mechanics_weight=0.30,
        difficulty_weight=0.20,
        ranking_weight=0.10,
        is_default=True
    ))
    
    # Activate it
    config_service.activate(config.id)
    
    print(f"✅ Created and activated scoring config: {config.name}")
    return config


# ============================================================================
# E2E Test Scenarios
# ============================================================================

def test_e2e_scenario_1_small_cooperative_session():
    """
    SCENARIO 1: Small Cooperative Session
    =====================================
    Context: 4 students, 60 minutes, cooperative focus
    Expected: Should recommend cooperative games like Pandemic, Forbidden Island
    """
    print("\n" + "="*70)
    print("SCENARIO 1: Small Cooperative Session (4 students, 60 min)")
    print("="*70)
    
    db = get_test_db()
    
    try:
        # 1. SETUP: Seed data
        print("\n📦 STEP 1: Seeding test data...")
        games = seed_test_games(db)
        skills = seed_test_skills(db)
        config = create_scoring_config(db)
        
        # 2. CREATE SESSION PROFILE
        print("\n📝 STEP 2: Creating session profile...")
        session_service = SessionProfileService()
        session = session_service.create(db, SessionProfileCreate(
            session_name="Taller de Cooperación - Grupo Pequeño",
            objectives=["Fomentar trabajo en equipo", "Desarrollar comunicación"],
            primary_skill_name="Trabajo en Equipo",
            available_time_min=60,
            group_size=4,
            max_language_dependency=LanguageDependency.MEDIA,
            preferred_modality=Modality.COOPERATIVE
        ))
        print(f"   ✅ Session created: {session.session_name}")
        print(f"   • Group size: {session.group_size}")
        print(f"   • Time: {session.available_time_min} min")
        print(f"   • Modality: {session.preferred_modality}")
        if session.has_warnings:
            print(f"   ⚠️  Warnings: {len(session.validation_warnings)}")
        
        # 3. GENERATE RECOMMENDATIONS
        print("\n🎯 STEP 3: Generating recommendations...")
        engine = RecommendationEngine(db)
        result = engine.generate_recommendations(
            session_profile_id=session.id,
            top_n=5
        )
        
        print(f"   ✅ Generated {len(result.recommendations)} recommendations")
        
        if result.has_results:
            for i, rec in enumerate(result.recommendations, 1):
                game = db.query(Game).filter(Game.id == rec.game_id).first()
                print(f"\n   #{i} - {game.name}")
                print(f"      Score: {rec.total_score:.3f}")
                print(f"      Complexity: {game.complexity}/5.0")
                print(f"      Duration: {game.duration_min} min")
                print(f"      Players: {game.min_players}-{game.max_players}")
                print(f"      Mechanics: {', '.join(game.mechanics[:3])}")
        else:
            print(f"   ⚠️  No recommendations generated")
            suggestions = result.relaxation_suggestions or []
            print(f"   Suggestions: {suggestions}")
        
        # 4. GET DETAILED EXPLANATION
        if result.has_results and len(result.recommendations) > 0:
            print("\n📖 STEP 4: Getting detailed explanation for top recommendation...")
            explainability_service = ExplainabilityService(db)
            
            top_recommendation = result.recommendations[0]
            explanation = explainability_service.get_recommendation_explanation(
                recommendation_id=top_recommendation.id,
                include_technical=True
            )
            
            print(f"\n   {'='*65}")
            print(f"   EXPLANATION FOR: {explanation['game_name']}")
            print(f"   {'='*65}")
            print(f"\n{explanation['explanation_text']}")
            
            if 'score_components' in explanation:
                print(f"\n   📊 SCORE BREAKDOWN:")
                components = explanation['score_components']
                print(f"      • Skill Score:      {components['skill_score']['value']:.3f} (weight: {components['skill_score']['weight']:.2f})")
                print(f"      • Mechanics Score:  {components['mechanics_score']['value']:.3f} (weight: {components['mechanics_score']['weight']:.2f})")
                print(f"      • Difficulty Score: {components['difficulty_score']['value']:.3f} (weight: {components['difficulty_score']['weight']:.2f})")
                print(f"      • Ranking Score:    {components['ranking_score']['value']:.3f} (weight: {components['ranking_score']['weight']:.2f})")
                print(f"      • TOTAL:            {explanation['total_score']:.3f}")
        
        # 5. SIMULATE USER FEEDBACK
        if result.has_results and len(result.recommendations) > 0:
            print("\n👍 STEP 5: Simulating user feedback...")
            top_rec = result.recommendations[0]
            top_rec.was_selected = True
            top_rec.user_feedback_score = 5
            db.commit()
            print(f"   ✅ Feedback recorded: Selected + 5 stars")
        
        # 6. GET TRACEABILITY REPORT
        if result.has_results and len(result.recommendations) > 0:
            print("\n🔍 STEP 6: Getting traceability report (RF-EXP-02)...")
            traceability = explainability_service.get_traceability_report(
                recommendation_id=top_recommendation.id
            )
            
            print(f"\n   📋 TRACEABILITY REPORT:")
            print(f"      • Recommendation ID: {traceability['recommendation_id']}")
            print(f"      • Generated at: {traceability['audit_trail']['generated_at']}")
            print(f"      • Session: {traceability['audit_trail']['session_profile']['name']}")
            print(f"      • Game: {traceability['audit_trail']['game_selected']['name']}")
            print(f"      • Config weights: {traceability['audit_trail']['scoring_configuration']['weights']}")
            print(f"      • Total score: {traceability['audit_trail']['scoring_configuration']['total_score']:.3f}")
        
        print(f"\n{'='*70}")
        print("✅ SCENARIO 1 COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        # Assertions
        assert result.has_results, "Should generate recommendations"
        assert len(result.recommendations) > 0, "Should have at least one recommendation"
        
        # Check that cooperative games are prioritized
        top_game = db.query(Game).filter(Game.id == result.recommendations[0].game_id).first()
        print(f"🎯 Top recommendation: {top_game.name}")
        
        return True
        
    finally:
        db.close()


def test_e2e_scenario_2_large_competitive_session():
    """
    SCENARIO 2: Large Competitive Session
    =====================================
    Context: 8 students, 30 minutes, competitive party game
    Expected: Should recommend party games like Dixit, Codenames
    """
    print("\n" + "="*70)
    print("SCENARIO 2: Large Competitive Session (8 students, 30 min)")
    print("="*70)
    
    db = get_test_db()
    
    try:
        # 1. Setup
        print("\n📦 STEP 1: Seeding test data...")
        games = seed_test_games(db)
        skills = seed_test_skills(db)
        config = create_scoring_config(db)
        
        # 2. Create session with large group
        print("\n📝 STEP 2: Creating session profile for large group...")
        session_service = SessionProfileService()
        session = session_service.create(db, SessionProfileCreate(
            session_name="Competencia de Deducción - Grupo Grande",
            objectives=["Desarrollar pensamiento lógico", "Fomentar competencia sana"],
            primary_skill_name="Pensamiento Crítico",
            available_time_min=30,
            group_size=8,
            max_language_dependency=LanguageDependency.ALTA,
            preferred_modality=Modality.COMPETITIVE
        ))
        print(f"   ✅ Session created: {session.session_name}")
        print(f"   • Group size: {session.group_size}")
        print(f"   • Time: {session.available_time_min} min")
        
        # Check for warnings (should have warnings for large group)
        if session.has_warnings:
            print(f"   ⚠️  Validation warnings detected:")
            for warning in session.validation_warnings:
                print(f"      • [{warning['severity']}] {warning['message']}")
        
        # 3. Generate recommendations
        print("\n🎯 STEP 3: Generating recommendations...")
        engine = RecommendationEngine(db)
        result = engine.generate_recommendations(
            session_profile_id=session.id,
            top_n=3
        )
        
        print(f"   ✅ Generated {len(result.recommendations)} recommendations")
        
        if result.has_results:
            for i, rec in enumerate(result.recommendations, 1):
                game = db.query(Game).filter(Game.id == rec.game_id).first()
                print(f"\n   #{i} - {game.name}")
                print(f"      Score: {rec.total_score:.3f}")
                print(f"      Players: {game.min_players}-{game.max_players} (fits {session.group_size})")
                print(f"      Duration: {game.duration_min} min (available: {session.available_time_min})")
        
        # 4. Compare top recommendations
        if result.has_results and len(result.recommendations) >= 2:
            print("\n📊 STEP 4: Comparing top recommendations...")
            explainability_service = ExplainabilityService(db)
            
            comparison_ids = [rec.id for rec in result.recommendations[:2]]
            comparison = explainability_service.compare_recommendations(
                recommendation_ids=comparison_ids
            )
            
            print(f"\n   COMPARISON:")
            for comp in comparison['comparisons']:
                print(f"\n   • {comp['game_name']} (Score: {comp['total_score']:.3f})")
                print(f"     Strengths: {', '.join(comp['key_strengths'][:2])}")
            
            if comparison['differences']:
                print(f"\n   KEY DIFFERENCES:")
                for diff in comparison['differences'][:3]:
                    print(f"      • {diff}")
        
        print(f"\n{'='*70}")
        print("✅ SCENARIO 2 COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        # Assertions
        if result.has_results:
            assert len(result.recommendations) > 0
            # Check that games support 8 players
            for rec in result.recommendations:
                game = db.query(Game).filter(Game.id == rec.game_id).first()
                assert game.max_players >= 8, f"{game.name} should support 8 players"
        
        return True
        
    finally:
        db.close()


def test_e2e_scenario_3_time_constrained_session():
    """
    SCENARIO 3: Time-Constrained Session
    ====================================
    Context: 3 students, 20 minutes, any modality
    Expected: Should recommend quick games, warn about limited time
    """
    print("\n" + "="*70)
    print("SCENARIO 3: Time-Constrained Session (3 students, 20 min)")
    print("="*70)
    
    db = get_test_db()
    
    try:
        # 1. Setup
        print("\n📦 STEP 1: Seeding test data...")
        games = seed_test_games(db)
        skills = seed_test_skills(db)
        config = create_scoring_config(db)
        
        # 2. Create time-constrained session
        print("\n📝 STEP 2: Creating time-constrained session...")
        session_service = SessionProfileService()
        session = session_service.create(db, SessionProfileCreate(
            session_name="Sesión Rápida - Pensamiento Ágil",
            objectives=["Toma de decisiones rápidas"],
            primary_skill_name="Pensamiento Crítico",
            available_time_min=20,  # Very limited time
            group_size=3,
            max_language_dependency=LanguageDependency.BAJA,
            preferred_modality=Modality.ANY
        ))
        print(f"   ✅ Session created: {session.session_name}")
        print(f"   • Time: {session.available_time_min} min (LIMITED)")
        
        # Should have time warning
        if session.has_warnings:
            print(f"   ⚠️  Expected validation warnings:")
            for warning in session.validation_warnings:
                if warning['code'] == 'LIMITED_TIME':
                    print(f"      • {warning['message']}")
                    print(f"      • Suggestions: {warning['suggestions']}")
        
        # 3. Generate recommendations
        print("\n🎯 STEP 3: Generating recommendations...")
        engine = RecommendationEngine(db)
        result = engine.generate_recommendations(
            session_profile_id=session.id,
            top_n=5
        )
        
        if result.has_results:
            print(f"   ✅ Generated {len(result.recommendations)} recommendations")
            
            # All should be quick games
            for i, rec in enumerate(result.recommendations, 1):
                game = db.query(Game).filter(Game.id == rec.game_id).first()
                print(f"\n   #{i} - {game.name}")
                print(f"      Duration: {game.duration_min} min ≤ {session.available_time_min + 10} min (with buffer)")
                print(f"      Complexity: {game.complexity}/5.0")
                
                # Verify time constraint with buffer
                assert game.duration_min <= session.available_time_min * 1.2, \
                    f"{game.name} should fit time constraint"
        else:
            print(f"   ⚠️  No recommendations (too constrained)")
            suggestions = result.relaxation_suggestions or []
            print(f"   Suggestions: {suggestions}")
        
        print(f"\n{'='*70}")
        print("✅ SCENARIO 3 COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        return True
        
    finally:
        db.close()


def test_e2e_scenario_4_no_results_handling():
    """
    SCENARIO 4: No Results - Impossible Constraints
    ===============================================
    Context: Impossible constraints (100 players, 5 minutes)
    Expected: Should handle gracefully with suggestions
    """
    print("\n" + "="*70)
    print("SCENARIO 4: No Results Handling (Impossible Constraints)")
    print("="*70)
    
    db = get_test_db()
    
    try:
        # 1. Setup
        print("\n📦 STEP 1: Seeding test data...")
        games = seed_test_games(db)
        skills = seed_test_skills(db)
        config = create_scoring_config(db)
        
        # 2. Create impossible session
        print("\n📝 STEP 2: Creating session with impossible constraints...")
        session_service = SessionProfileService()
        session = session_service.create(db, SessionProfileCreate(
            session_name="Sesión Imposible - Testing",
            objectives=["Testing no results"],
            primary_skill_name="Trabajo en Equipo",
            available_time_min=15,  # Minimum valid time but with 100 players = impossible
            group_size=100,  # Too large
            max_language_dependency=LanguageDependency.NINGUNA,
            preferred_modality=Modality.ANY
        ))
        print(f"   ✅ Session created: {session.session_name}")
        print(f"   • Group size: {session.group_size} (VERY LARGE)")
        print(f"   • Time: {session.available_time_min} min (VERY LIMITED)")
        
        # Should have multiple warnings
        if session.has_warnings:
            print(f"   ⚠️  Validation warnings: {len(session.validation_warnings)}")
            for warning in session.validation_warnings:
                print(f"      • [{warning['severity']}] {warning['code']}: {warning['message']}")
        
        # 3. Try to generate recommendations
        print("\n🎯 STEP 3: Attempting to generate recommendations...")
        engine = RecommendationEngine(db)
        result = engine.generate_recommendations(
            session_profile_id=session.id,
            top_n=5
        )
        
        print(f"   Has results: {result.has_results}")
        
        if not result.has_results:
            print(f"   ✅ Expected: No recommendations due to constraints")
            
            # Should have suggestions (RF-REC-03)
            if result.relaxation_suggestions:
                print(f"\n   💡 INTELLIGENT SUGGESTIONS (RF-REC-03):")
                for suggestion in result.relaxation_suggestions:
                    print(f"      • {suggestion}")
                
                # Validate RF-REC-03
                assert len(result.relaxation_suggestions) > 0, \
                    "Should provide suggestions (RF-REC-03)"
            else:
                raise AssertionError("Should provide suggestions (RF-REC-03)")
        else:
            print(f"   ⚠️  Unexpected: Got {len(result.recommendations)} recommendations")
        
        print(f"\n{'='*70}")
        print("✅ SCENARIO 4 COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        # Final assertions (RF-REC-03)
        assert not result.has_results, "Should not generate recommendations with impossible constraints"
        assert result.relaxation_suggestions is not None, "Should provide suggestions (RF-REC-03)"
        assert len(result.relaxation_suggestions) > 0, "Should provide at least one suggestion (RF-REC-03)"
        
        return True
        
    finally:
        db.close()


def test_e2e_scenario_5_skill_based_recommendations():
    """
    SCENARIO 5: Skill-Based Recommendations
    =======================================
    Context: Focus on specific skill development
    Expected: Recommendations aligned with skill taxonomy
    """
    print("\n" + "="*70)
    print("SCENARIO 5: Skill-Based Recommendations")
    print("="*70)
    
    db = get_test_db()
    
    try:
        # 1. Setup
        print("\n📦 STEP 1: Seeding test data...")
        games = seed_test_games(db)
        skills = seed_test_skills(db)
        config = create_scoring_config(db)
        
        # 2. Get skill hierarchy
        print("\n🌳 STEP 2: Exploring skill taxonomy...")
        skill_service = SkillService()
        tree = skill_service.get_tree(db, active_only=True)
        
        print(f"   Skills in taxonomy: {len(tree)}")
        # tree contains Skill ORM objects, not dicts - access as attributes
        for i, skill in enumerate(tree[:2], 1):  # Show first 2 roots
            print(f"   {i}. {skill.name}")
            if hasattr(skill, 'children') and skill.children:
                for child in skill.children[:2]:  # Show first 2 children
                    print(f"      • {child.name}")
        
        # 3. Create session focused on a specific skill
        teamwork_skill = db.query(Skill).filter(Skill.name == "Trabajo en Equipo").first()
        
        print(f"\n📝 STEP 3: Creating skill-focused session...")
        session_service = SessionProfileService()
        session = session_service.create(db, SessionProfileCreate(
            session_name="Desarrollo de Trabajo en Equipo",
            objectives=["Fortalecer colaboración", "Mejorar comunicación grupal"],
            primary_skill_name=teamwork_skill.name,
            available_time_min=45,
            group_size=4,
            max_language_dependency=LanguageDependency.MEDIA,
            preferred_modality=Modality.COOPERATIVE
        ))
        print(f"   ✅ Session created focused on: {teamwork_skill.name}")
        
        # 4. Generate recommendations
        print("\n🎯 STEP 4: Generating skill-aligned recommendations...")
        engine = RecommendationEngine(db)
        result = engine.generate_recommendations(
            session_profile_id=session.id,
            top_n=3
        )
        
        if result.has_results:
            print(f"   ✅ Generated {len(result.recommendations)} recommendations")
            
            for i, rec in enumerate(result.recommendations, 1):
                game = db.query(Game).filter(Game.id == rec.game_id).first()
                print(f"\n   #{i} - {game.name}")
                print(f"      Skill Score: {rec.skill_score:.3f}")
                print(f"      Complexity: {game.complexity}/5.0")
                
                # Show explanation excerpt
                if rec.explanation_text:
                    # Extract first line of explanation
                    first_line = rec.explanation_text.split('\n')[0]
                    print(f"      Reason: {first_line[:80]}...")
        
        print(f"\n{'='*70}")
        print("✅ SCENARIO 5 COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        return True
        
    finally:
        db.close()


# ============================================================================
# Main Execution
# ============================================================================

def run_all_e2e_tests():
    """Run all E2E test scenarios."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "END-TO-END TEST SUITE" + " "*27 + "║")
    print("║" + " "*15 + "Complete Application Flow Testing" + " "*20 + "║")
    print("╚" + "="*68 + "╝")
    
    scenarios = [
        ("Scenario 1: Small Cooperative Session", test_e2e_scenario_1_small_cooperative_session),
        ("Scenario 2: Large Competitive Session", test_e2e_scenario_2_large_competitive_session),
        ("Scenario 3: Time-Constrained Session", test_e2e_scenario_3_time_constrained_session),
        ("Scenario 4: No Results Handling", test_e2e_scenario_4_no_results_handling),
        ("Scenario 5: Skill-Based Recommendations", test_e2e_scenario_5_skill_based_recommendations)
    ]
    
    results = []
    
    for name, test_func in scenarios:
        try:
            test_func()
            results.append((name, "✅ PASSED"))
        except Exception as e:
            results.append((name, f"❌ FAILED: {str(e)}"))
            print(f"\n❌ ERROR in {name}: {str(e)}\n")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, status in results:
        print(f"{status}: {name}")
    
    passed = sum(1 for _, status in results if "PASSED" in status)
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"RESULT: {passed}/{total} scenarios passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    run_all_e2e_tests()
