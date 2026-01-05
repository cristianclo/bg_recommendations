"""
Script to seed initial game data and session profiles for testing.
Run with: python -m backend.scripts.seed_data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.game import Game, LanguageDependency, Base
from app.models.session import SessionProfile, Modality
from app.models.skill import Skill
from app.games.service import GameService
from app.sessions.service import SessionProfileService
from app.skills.service import SkillService

# Sample games for testing
SAMPLE_GAMES = [
    {
        "name": "Catan",
        "bgg_id": 13,
        "duration_min": 120,
        "complexity": 2.3,
        "min_players": 3,
        "max_players": 4,
        "mechanics": ["Trading", "Dice Rolling", "Route Building"],
        "language_dependency": LanguageDependency.BAJA,
        "bgg_rank": 15,
        "description": "Players try to be the dominant force on the island of Catan by building settlements, cities, and roads.",
        "year_published": 1995,
        "available": True
    },
    {
        "name": "Pandemic",
        "bgg_id": 30549,
        "duration_min": 45,
        "complexity": 2.4,
        "min_players": 2,
        "max_players": 4,
        "mechanics": ["Cooperative Play", "Hand Management", "Set Collection"],
        "language_dependency": LanguageDependency.MEDIA,
        "bgg_rank": 50,
        "description": "Players work together as disease-fighting specialists to treat disease hotspots while researching cures.",
        "year_published": 2008,
        "available": True
    },
    {
        "name": "Dixit",
        "bgg_id": 39856,
        "duration_min": 30,
        "complexity": 1.2,
        "min_players": 3,
        "max_players": 8,
        "mechanics": ["Storytelling", "Voting", "Hand Management"],
        "language_dependency": LanguageDependency.BAJA,
        "bgg_rank": 120,
        "description": "A creative and imaginative game where players give clues using beautiful illustrated cards.",
        "year_published": 2008,
        "available": True
    },
    {
        "name": "Codenames",
        "bgg_id": 178900,
        "duration_min": 15,
        "complexity": 1.3,
        "min_players": 2,
        "max_players": 8,
        "mechanics": ["Cooperative Play", "Deduction", "Partnerships"],
        "language_dependency": LanguageDependency.ALTA,
        "bgg_rank": 45,
        "description": "Two teams compete to identify their agents using one-word clues from their spymaster.",
        "year_published": 2015,
        "available": True
    },
    {
        "name": "Azul",
        "bgg_id": 230802,
        "duration_min": 40,
        "complexity": 1.8,
        "min_players": 2,
        "max_players": 4,
        "mechanics": ["Pattern Building", "Set Collection", "Tile Placement"],
        "language_dependency": LanguageDependency.NINGUNA,
        "bgg_rank": 80,
        "description": "Players compete as artisans to decorate the walls of the Royal Palace of Evora.",
        "year_published": 2017,
        "available": True
    },
    {
        "name": "7 Wonders",
        "bgg_id": 68448,
        "duration_min": 30,
        "complexity": 2.3,
        "min_players": 2,
        "max_players": 7,
        "mechanics": ["Card Drafting", "Set Collection", "Simultaneous Action Selection"],
        "language_dependency": LanguageDependency.MEDIA,
        "bgg_rank": 100,
        "description": "Build your city and erect an architectural wonder which will transcend future times.",
        "year_published": 2010,
        "available": True
    },
    {
        "name": "Ticket to Ride",
        "bgg_id": 9209,
        "duration_min": 60,
        "complexity": 1.9,
        "min_players": 2,
        "max_players": 5,
        "mechanics": ["Set Collection", "Route Building", "Hand Management"],
        "language_dependency": LanguageDependency.BAJA,
        "bgg_rank": 70,
        "description": "Collect cards and claim railway routes connecting cities across North America.",
        "year_published": 2004,
        "available": True
    },
    {
        "name": "Coup",
        "bgg_id": 131357,
        "duration_min": 15,
        "complexity": 1.4,
        "min_players": 2,
        "max_players": 6,
        "mechanics": ["Bluffing", "Hidden Roles", "Player Elimination"],
        "language_dependency": LanguageDependency.BAJA,
        "bgg_rank": 150,
        "description": "A game of influence, deduction and bluffing in a dystopian universe.",
        "year_published": 2012,
        "available": True
    }
]

# Sample session profiles for testing
SAMPLE_SESSIONS = [
    {
        "session_name": "Clase Trabajo en Equipo - Grupo Pequeño",
        "objectives": ["Desarrollar comunicación efectiva", "Fomentar cooperación"],
        "primary_skill_name": "Trabajo en equipo",
        "secondary_skill_name": "Comunicación",
        "available_time_min": 60,
        "group_size": 15,
        "max_language_dependency": LanguageDependency.MEDIA,
        "preferred_modality": Modality.COOPERATIVE,
        "notes": "Sesión introductoria para estudiantes de primer semestre",
        "created_by_name": "Prof. María García"
    },
    {
        "session_name": "Taller Pensamiento Estratégico",
        "objectives": ["Desarrollar pensamiento crítico", "Mejorar toma de decisiones"],
        "primary_skill_name": "Pensamiento estratégico",
        "secondary_skill_name": "Análisis",
        "available_time_min": 90,
        "group_size": 8,
        "max_language_dependency": LanguageDependency.BAJA,
        "preferred_modality": Modality.COMPETITIVE,
        "notes": "Grupo avanzado de administración",
        "created_by_name": "Prof. Carlos Rodríguez"
    },
    {
        "session_name": "Sesión Rompehielo - Primer Día",
        "objectives": ["Integración grupal", "Crear ambiente positivo"],
        "primary_skill_name": "Socialización",
        "secondary_skill_name": "Comunicación",
        "available_time_min": 20,  # Tiempo limitado - generará warning
        "group_size": 12,
        "max_language_dependency": LanguageDependency.BAJA,
        "preferred_modality": Modality.ANY,
        "notes": "Actividad corta para inicio de semestre",
        "created_by_name": "Prof. Ana Martínez"
    },
    {
        "session_name": "Evento Masivo - Feria Estudiantil",
        "objectives": ["Promover trabajo colaborativo", "Gestión de proyectos"],
        "primary_skill_name": "Trabajo en equipo",
        "secondary_skill_name": "Liderazgo",
        "available_time_min": 120,
        "group_size": 45,  # Grupo muy grande - generará warning
        "max_language_dependency": LanguageDependency.NINGUNA,
        "preferred_modality": Modality.COOPERATIVE,
        "notes": "Feria anual con múltiples grupos participando",
        "created_by_name": "Coordinación Académica"
    },
    {
        "session_name": "Competencia Intergrupal",
        "objectives": ["Desarrollar competitividad sana", "Pensamiento rápido"],
        "primary_skill_name": "Agilidad mental",
        "secondary_skill_name": "Trabajo bajo presión",
        "available_time_min": 45,
        "group_size": 24,  # Grupo grande - generará warning
        "max_language_dependency": LanguageDependency.ALTA,
        "preferred_modality": Modality.COMPETITIVE,
        "notes": "Torneo entre equipos de diferentes carreras",
        "created_by_name": "Prof. Luis Herrera"
    },
    {
        "session_name": "Laboratorio de Negociación",
        "objectives": ["Desarrollar habilidades de negociación", "Pensamiento estratégico"],
        "primary_skill_name": "Negociación",
        "secondary_skill_name": "Persuasión",
        "available_time_min": 75,
        "group_size": 6,
        "max_language_dependency": LanguageDependency.MEDIA,
        "preferred_modality": Modality.COMPETITIVE,
        "notes": "Sesión práctica para estudiantes de negocios",
        "created_by_name": "Prof. Diana Castro"
    },
    {
        "session_name": "Taller Creatividad e Innovación",
        "objectives": ["Fomentar pensamiento creativo", "Promover innovación"],
        "primary_skill_name": "Creatividad",
        "secondary_skill_name": "Innovación",
        "available_time_min": 100,
        "group_size": 10,
        "max_language_dependency": LanguageDependency.BAJA,
        "preferred_modality": Modality.ANY,
        "notes": "Taller para programa de emprendimiento",
        "created_by_name": "Prof. Roberto Silva"
    },
    {
        "session_name": "Sesión Express - Break Académico",
        "objectives": ["Reducir estrés", "Integración social"],
        "primary_skill_name": "Bienestar",
        "secondary_skill_name": "Socialización",
        "available_time_min": 15,  # Muy corto - generará warning
        "group_size": 8,
        "max_language_dependency": LanguageDependency.NINGUNA,
        "preferred_modality": Modality.ANY,
        "notes": "Pausa activa durante jornada de exámenes",
        "created_by_name": "Bienestar Universitario"
    }
]

# Sample skills taxonomy for testing
# Format: (name, description, parent_name)
SAMPLE_SKILLS = [
    # Root skills (no parent)
    ("Habilidades Cognitivas", "Capacidades mentales y de pensamiento", None),
    ("Habilidades Sociales", "Capacidades de interacción y relación con otros", None),
    ("Habilidades Emocionales", "Capacidades de gestión emocional y bienestar", None),
    ("Habilidades Prácticas", "Capacidades de ejecución y acción", None),
    
    # Level 1: Children of Habilidades Cognitivas
    ("Pensamiento Estratégico", "Capacidad para planificar y anticipar", "Habilidades Cognitivas"),
    ("Pensamiento Crítico", "Análisis y evaluación de información", "Habilidades Cognitivas"),
    ("Creatividad", "Generación de ideas novedosas", "Habilidades Cognitivas"),
    ("Memoria", "Retención y recuperación de información", "Habilidades Cognitivas"),
    
    # Level 2: Children of Pensamiento Estratégico
    ("Planificación", "Organización de acciones futuras", "Pensamiento Estratégico"),
    ("Toma de decisiones", "Selección entre alternativas", "Pensamiento Estratégico"),
    ("Análisis de riesgos", "Evaluación de consecuencias", "Pensamiento Estratégico"),
    
    # Level 2: Children of Pensamiento Crítico
    ("Razonamiento lógico", "Aplicación de principios lógicos", "Pensamiento Crítico"),
    ("Resolución de problemas", "Solución de situaciones complejas", "Pensamiento Crítico"),
    ("Análisis de información", "Interpretación de datos", "Pensamiento Crítico"),
    
    # Level 2: Children of Creatividad
    ("Innovación", "Creación de soluciones novedosas", "Creatividad"),
    ("Pensamiento divergente", "Generación de múltiples soluciones", "Creatividad"),
    ("Imaginación", "Visualización de posibilidades", "Creatividad"),
    
    # Level 1: Children of Habilidades Sociales
    ("Trabajo en equipo", "Colaboración efectiva con otros", "Habilidades Sociales"),
    ("Comunicación", "Transmisión efectiva de información", "Habilidades Sociales"),
    ("Liderazgo", "Guía e influencia sobre otros", "Habilidades Sociales"),
    ("Negociación", "Búsqueda de acuerdos beneficiosos", "Habilidades Sociales"),
    
    # Level 2: Children of Trabajo en equipo
    ("Cooperación", "Trabajo conjunto hacia objetivos comunes", "Trabajo en equipo"),
    ("Coordinación", "Sincronización de esfuerzos", "Trabajo en equipo"),
    ("Construcción de consenso", "Logro de acuerdos grupales", "Trabajo en equipo"),
    
    # Level 2: Children of Comunicación
    ("Comunicación verbal", "Expresión oral efectiva", "Comunicación"),
    ("Comunicación no verbal", "Uso de lenguaje corporal", "Comunicación"),
    ("Escucha activa", "Atención y comprensión", "Comunicación"),
    
    # Level 2: Children of Liderazgo
    ("Motivación de equipos", "Inspiración y energización", "Liderazgo"),
    ("Delegación", "Asignación efectiva de tareas", "Liderazgo"),
    ("Toma de iniciativa", "Proactividad y autonomía", "Liderazgo"),
    
    # Level 1: Children of Habilidades Emocionales
    ("Inteligencia emocional", "Reconocimiento y gestión de emociones", "Habilidades Emocionales"),
    ("Resiliencia", "Adaptación a adversidades", "Habilidades Emocionales"),
    ("Empatía", "Comprensión de emociones ajenas", "Habilidades Emocionales"),
    
    # Level 2: Children of Inteligencia emocional
    ("Autoconocimiento", "Comprensión de propias emociones", "Inteligencia emocional"),
    ("Autorregulación", "Control de impulsos y emociones", "Inteligencia emocional"),
    ("Motivación intrínseca", "Impulso interno hacia metas", "Inteligencia emocional"),
    
    # Level 1: Children of Habilidades Prácticas
    ("Gestión de recursos", "Administración eficiente de recursos", "Habilidades Prácticas"),
    ("Gestión del tiempo", "Organización temporal efectiva", "Habilidades Prácticas"),
    ("Adaptabilidad", "Flexibilidad ante cambios", "Habilidades Prácticas"),
    ("Perseverancia", "Persistencia hacia objetivos", "Habilidades Prácticas"),
]


def seed_database():
    """Seed database with sample games, session profiles, and skills."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    game_service = GameService()
    session_service = SessionProfileService()
    skill_service = SkillService()
    
    try:
        # Seed skills first (needed for sessions)
        print("\n🧠 Seeding skills taxonomy...")
        skills_created = 0
        skill_map = {}  # Map name to skill object for parent references
        
        # First pass: create root skills
        for name, description, parent_name in SAMPLE_SKILLS:
            if parent_name is None:
                existing = skill_service.get_by_name(db, name)
                if existing:
                    print(f"  ⏭️  Skipping '{name}' (already exists)")
                    skill_map[name] = existing
                    continue
                
                from app.schemas.skill import SkillCreate
                skill_create = SkillCreate(
                    name=name,
                    description=description,
                    parent_id=None,
                    is_active=True
                )
                skill = skill_service.create(db, skill_create)
                skill_map[name] = skill
                skills_created += 1
                print(f"  ✅ Created root: {name}")
        
        # Second pass: create child skills
        for name, description, parent_name in SAMPLE_SKILLS:
            if parent_name is not None:
                existing = skill_service.get_by_name(db, name)
                if existing:
                    print(f"  ⏭️  Skipping '{name}' (already exists)")
                    skill_map[name] = existing
                    continue
                
                parent_skill = skill_map.get(parent_name)
                if not parent_skill:
                    print(f"  ⚠️  Warning: Parent '{parent_name}' not found for '{name}'")
                    continue
                
                from app.schemas.skill import SkillCreate
                skill_create = SkillCreate(
                    name=name,
                    description=description,
                    parent_id=parent_skill.id,
                    is_active=True
                )
                skill = skill_service.create(db, skill_create)
                skill_map[name] = skill
                skills_created += 1
                level = skill.get_level()
                print(f"  ✅ Created (L{level}): {name} → {parent_name}")
        
        print(f"\n   Total skills created: {skills_created}")
        print(f"   Total skills in database: {db.query(Skill).count()}")
        
        # Validate hierarchy
        validation_result = skill_service.validate_hierarchy(db)
        if validation_result.is_valid:
            print(f"   ✅ Hierarchy validation: PASSED")
        else:
            print(f"   ⚠️  Hierarchy validation: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings")
        
        # Seed games
        print("\n📦 Seeding games...")
        games_created = 0
        for game_data in SAMPLE_GAMES:
            # Check if game already exists
            existing = game_service.get_by_bgg_id(db, game_data["bgg_id"])
            if existing:
                print(f"  ⏭️  Skipping {game_data['name']} (already exists)")
                continue
            
            # Create game using Pydantic schema
            from app.schemas.game import GameCreate
            game_create = GameCreate(**game_data)
            game = game_service.create(db, game_create)
            games_created += 1
            print(f"  ✅ Created: {game.name} (BGG ID: {game.bgg_id})")
        
        print(f"\n   Total games created: {games_created}")
        print(f"   Total games in database: {db.query(Game).count()}")
        
        # Seed session profiles
        print("\n🎯 Seeding session profiles...")
        sessions_created = 0
        for session_data in SAMPLE_SESSIONS:
            # Check if session already exists by name
            existing = db.query(SessionProfile).filter(
                SessionProfile.session_name == session_data["session_name"]
            ).first()
            if existing:
                print(f"  ⏭️  Skipping '{session_data['session_name']}' (already exists)")
                continue
            
            # Create session using Pydantic schema
            from app.schemas.session import SessionProfileCreate
            session_create = SessionProfileCreate(**session_data)
            session = session_service.create(db, session_create)
            sessions_created += 1
            
            # Show warnings if any
            warning_indicator = "⚠️ " if session.has_warnings else ""
            print(f"  ✅ {warning_indicator}Created: {session.session_name}")
            if session.has_warnings and session.validation_warnings:
                for warning in session.validation_warnings:
                    print(f"     └─ {warning['severity'].upper()}: {warning['message']}")
        
        print(f"\n   Total sessions created: {sessions_created}")
        print(f"   Total sessions in database: {db.query(SessionProfile).count()}")
        
        print(f"\n✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
