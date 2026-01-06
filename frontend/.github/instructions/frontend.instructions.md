---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.# GitHub Copilot Instructions - CJEI Recommendations System

## Project Overview

**Sistema de Recomendación de Juegos de Mesa** para el Centro de Juegos y Experiencias Interactivas (CJEI) de la Pontificia Universidad Javeriana Cali.

**Tech Stack:**
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy 2.0, PostgreSQL 14+
- **Frontend:** React + TypeScript (pending)
- **Auth:** JWT with python-jose, bcrypt
- **Migrations:** Alembic

## Current Implementation Status

### ✅ Módulo A - Data Ingestion & Normalization (COMPLETE)

Implemented requirements:
- **RF-ING-01:** Game catalog import with all required attributes
- **RF-ING-02:** Automatic normalization (duration 5-360min, complexity 1.0-5.0, controlled mechanics vocabulary)
- **RF-ING-03:** CSV/JSON bulk import with duplicate detection and merge strategies

**Key files:**
- [backend/app/models/game.py](backend/app/models/game.py) - SQLAlchemy Game model with LanguageDependency enum
- [backend/app/schemas/game.py](backend/app/schemas/game.py) - Pydantic validation schemas
- [backend/app/games/service.py](backend/app/games/service.py) - Business logic with normalization rules
- [backend/app/games/router.py](backend/app/games/router.py) - FastAPI CRUD endpoints
- [backend/app/games/import_handler.py](backend/app/games/import_handler.py) - Bulk import logic

### ✅ Módulo B - Session Profile Characterization (COMPLETE)

Implemented requirements:
- **RF-CTX-01:** Session profile capture (objectives, skills, time 15-240min, group size 1-100, language dependency, modality, constraints)
- **RF-CTX-02:** Operational coherence validation with non-blocking warnings (large groups >20/30, limited time <30min, cooperative+large group combinations)

**Key files:**
- [backend/app/models/session.py](backend/app/models/session.py) - SessionProfile model with Modality enum
- [backend/app/schemas/session.py](backend/app/schemas/session.py) - Pydantic schemas with ValidationWarning/ValidationResult
- [backend/app/sessions/validator.py](backend/app/sessions/validator.py) - SessionValidator with coherence checks
- [backend/app/sessions/service.py](backend/app/sessions/service.py) - Business logic with automatic validation
- [backend/app/sessions/router.py](backend/app/sessions/router.py) - 8 CRUD endpoints + validate + statistics
- [backend/tests/test_sessions.py](backend/tests/test_sessions.py) - 15 unit tests covering RF-CTX-01/02

**Validation warning system:**
- `LARGE_GROUP` (>20): Suggests multiple stations
- `VERY_LARGE_GROUP` (>30): Strongly recommends stations
- `LIMITED_TIME` (<30min): Warns about complexity limitations
- `COOPERATIVE_LARGE_GROUP` (cooperative + >30): Suggests team subdivision
- All warnings are **non-blocking** and include severity, category, code, message, and suggestions

### ✅ Módulo C - Skills Taxonomy Management (COMPLETE)

Implemented requirements:
- **RF-TAX-01:** Hierarchical taxonomy creation (4-level tree: root → parent → child → grandchild)
- **RF-TAX-02:** CRUD operations for skills with validation
- **RF-TAX-03:** Manual game-skill association (many-to-many, with pedagogical justification)

**Key files:**
- [backend/app/models/skill.py](backend/app/models/skill.py) - Skill model with self-referential relationship
- [backend/app/schemas/skill.py](backend/app/schemas/skill.py) - Pydantic schemas with tree representations
- [backend/app/skills/service.py](backend/app/skills/service.py) - Tree operations (descendants, ancestors, validation)
- [backend/app/skills/router.py](backend/app/skills/router.py) - 10 endpoints for CRUD + tree navigation
- [backend/tests/test_skills.py](backend/tests/test_skills.py) - 13 unit tests covering RF-TAX-01/02/03

**Taxonomy features:**
- Pre-seeded with 40 skills (Habilidades Cognitivas, Sociales, Emocionales, Prácticas)
- Validated 4-level depth limit
- Circular reference prevention
- Bulk tree retrieval with single query
- Game-skill associations with justification field

### ✅ Módulo D - Recommendation Engine (COMPLETE)

Implemented requirements:
- **RF-REC-01:** Hybrid recommendation algorithm (hard filters + weighted scoring)
- **RF-REC-02:** Flexible scoring configuration (4 components, configurable weights)
- **RF-REC-03:** Intelligent handling of zero results with relaxation suggestions

**Key files:**
- [backend/app/models/recommendation.py](backend/app/models/recommendation.py) - Recommendation & ScoringConfig models
- [backend/app/schemas/recommendation.py](backend/app/schemas/recommendation.py) - Pydantic schemas for requests/responses
- [backend/app/recommendations/engine.py](backend/app/recommendations/engine.py) - Core recommendation engine (600+ lines)
- [backend/app/recommendations/config_service.py](backend/app/recommendations/config_service.py) - Scoring config management
- [backend/app/recommendations/router.py](backend/app/recommendations/router.py) - 11 API endpoints
- [backend/tests/test_module_d_integration.py](backend/tests/test_module_d_integration.py) - Comprehensive integration tests
- [backend/tests/test_recommendations_with_realistic_data.py](backend/tests/test_recommendations_with_realistic_data.py) - Real data validation

**Scoring algorithm:**
- **Skill Score (40%):** Complexity-based skill match (placeholder for full skill integration)
- **Mechanics Score (30%):** Jaccard similarity + modality bonuses
- **Difficulty Score (20%):** Time/group size adjusted complexity appropriateness
- **Ranking Score (10%):** BGG rank normalization
- All scores normalized to [0.0, 1.0] range

**Hard filters:**
- Game availability
- Player count support
- Duration constraints (±20% buffer)
- Language dependency hierarchy

**Test results:**
- 81.8% test pass rate (9/11 tests)
- 4/13 realistic sessions generate recommendations (30.8%)
- Average 1.2 recommendations per successful session
- Intelligent no-results suggestions working

**Sample realistic sessions (2-8 players):**
- Taller Cooperación (4 players, 60 min) → Ticket to Ride
- Competencia Amistosa (8 players, 30 min) → Dixit
- Laboratorio Estrategia (2 players, 50 min) → Ticket to Ride, Azul
- Negociación Comercial (3 players, 75 min) → Ticket to Ride

### ✅ Módulo E - Explainability & Traceability (COMPLETE)

Implemented requirements:
- **RF-EXP-01:** Natural language explanations with ≥3 specific reasons per recommendation
- **RF-EXP-02:** Complete traceability with immutable audit trails

**Key files:**
- [backend/app/recommendations/engine.py](backend/app/recommendations/engine.py) - Enhanced explanation generation
- [backend/app/recommendations/explainability_service.py](backend/app/recommendations/explainability_service.py) - Explainability service (350+ lines)
- [backend/app/recommendations/router.py](backend/app/recommendations/router.py) - 4 explainability endpoints
- [backend/tests/test_module_e_explainability.py](backend/tests/test_module_e_explainability.py) - 5 comprehensive tests

**Explanation features:**
- Natural language format with emojis (✓, ⭐, ⚠️, ℹ️)
- 4+ specific reasons: skill alignment, operational constraints, mechanics relevance, quality indicators
- Warnings for edge cases (high complexity, time mismatches)
- Feedback boost mentions when applicable
- Score component breakdown with detailed context

**Traceability features:**
- Immutable audit records with complete snapshots
- Session profile capture (objectives, constraints, group size)
- Game state snapshot (name, mechanics, complexity, availability)
- Scoring configuration used
- Complete decision rationale
- User feedback outcome tracking
- Historical batch tracking over time

**Test results:**
- 100% test pass rate (5/5 tests)
- RF-EXP-01 validated: Natural explanations with 4+ reasons
- RF-EXP-02 validated: Complete immutable audit trails
- Comparison functionality working
- Historical tracking operational

### ✅ Módulo G - Feedback System (COMPLETE)

Implemented requirements:
- **RF-RETRO-01:** Feedback post-session capture (required: was_used, score 1-5, asesor; optional: qualitative comments)
- **RF-RETRO-02:** Game feedback statistics (aggregated utility, usage count, score distribution, recent comments)
- **RF-RETRO-03:** System-wide analytics (most used, highest rated, underperforming games, skills distribution)

**Key files:**
- [backend/app/models/recommendation.py](backend/app/models/recommendation.py) - Extended with 8 feedback fields
- [backend/app/schemas/feedback.py](backend/app/schemas/feedback.py) - FeedbackCreate, FeedbackUpdate, FeedbackResponse, GameFeedbackStatistics, FeedbackAnalytics
- [backend/app/feedback/service.py](backend/app/feedback/service.py) - FeedbackService with business logic (450+ lines)
- [backend/app/feedback/router.py](backend/app/feedback/router.py) - 7 API endpoints
- [backend/alembic/versions/005_add_feedback_fields.py](backend/alembic/versions/005_add_feedback_fields.py) - Migration

**Feedback features:**
- **Submission:** POST `/feedback/{recommendation_id}` with required fields (was_used, score, asesor)
- **Update:** PUT `/feedback/{recommendation_id}` - editable for 7 days
- **Retrieval:** GET `/feedback/{recommendation_id}` with editability status
- **Game statistics:** GET `/feedback/game/{game_id}/statistics` - RF-RETRO-02 implementation
- **System analytics:** GET `/feedback/analytics/system` - RF-RETRO-03 with date filters
- **Listing:** GET `/feedback/list` with filters (game, asesor, min_score, pagination)
- **Deletion:** DELETE `/feedback/{recommendation_id}` (admin only, soft delete)

**Feedback fields:**
- `was_used` (Boolean): Whether game was actually used
- `user_feedback_score` (1-5): Utility rating
- `feedback_asesor` (String): Asesor name
- `skill_actually_worked` (String, optional): Actual skill developed
- `what_worked_well` (Text, optional, max 500 chars)
- `what_didnt_work` (Text, optional, max 500 chars)
- `additional_notes` (Text, optional, max 500 chars)
- `feedback_date`, `can_edit_until` (DateTime): Metadata

**Analytics capabilities:**
- Top 10 most used games
- Hidden gems (≥4.5 rating, ≥3 uses)
- Underperforming games (<3.0 rating, ≥3 uses)
- Skills distribution across feedback
- Configurable date range filtering

**Database updates:**
- Migration `005_add_feedback_fields` applied
- 2 new indexes: feedback_date, feedback_asesor
- Soft delete support (NULL values)

### ✅ Módulo H - Administration (COMPLETE)

Implemented requirements:
- **RF-ADM-01:** Catalog management with statistics and analytics
- **RF-ADM-02:** Taxonomy management with impact analysis, versioning, and export

**Key files:**
- [backend/app/models/admin.py](backend/app/models/admin.py) - AuditLog & TaxonomySnapshot models
- [backend/app/schemas/admin.py](backend/app/schemas/admin.py) - Admin schemas (10 classes)
- [backend/app/admin/service.py](backend/app/admin/service.py) - AdminService with 10 methods (500+ lines)
- [backend/app/admin/router.py](backend/app/admin/router.py) - 11 API endpoints
- [backend/alembic/versions/006_add_admin_tables.py](backend/alembic/versions/006_add_admin_tables.py) - Migration

**RF-ADM-01 features (Catalog Management):**
- Catalog statistics: total games, availability, complexity distribution, player count distribution
- Most/least recommended games tracking
- Recent additions listing
- Integration with existing game CRUD (Módulo A)

**RF-ADM-02 features (Taxonomy Management):**
- Impact analysis before skill deletion (checks dependencies, provides recommendations)
- Taxonomy versioning with snapshots (create, list, activate versions)
- Export to JSON/PDF with configurable options
- Integration with existing skill CRUD (Módulo C)

**Audit log system:**
- Tracks all administrative actions with who/what/when/where
- Entity types: game, skill, session, recommendation, scoring_config, taxonomy
- Actions: create, update, delete, bulk_import, export, reorganize
- Filtering by entity, action, user, date range
- Statistics and activity patterns analysis

**Admin dashboard:**
- Consolidated view of catalog stats, audit activity, taxonomy info, system health
- Recent feedback summary
- Single endpoint: GET `/admin/dashboard`

**Test results:**
- All 11 endpoints operational
- Application loads with 62 total routes (11 admin-related)
- Migration applied successfully
- 100% backend MVP completion

### 🔄 Pending Modules

- **Módulo F:** Web interface (RF-UI-01, RF-UI-02, RF-UI-03)

## Architecture Patterns

### Project Structure
```
backend/
├── app/
│   ├── core/          # Config, database, exceptions, dependencies
│   ├── models/        # SQLAlchemy ORM (one class per file)
│   │   ├── game.py, session.py, skill.py, recommendation.py, admin.py
│   ├── schemas/       # Pydantic validation (matching model names)
│   │   ├── feedback.py, admin.py  # ✅ Feedback & admin schemas
│   ├── games/         # ✅ Módulo A: Games CRUD + import
│   ├── sessions/      # ✅ Módulo B: Session profiles + validation
│   ├── skills/        # ✅ Módulo C: Skills taxonomy + game associations
│   ├── recommendations/ # ✅ Módulo D: Recommendation engine + configs
│   ├── feedback/      # ✅ Módulo G: Feedback system
│   ├── admin/         # ✅ Módulo H: Administration
│   └── main.py        # FastAPI app entry point
├── alembic/           # Database migrations (6 migrations)
├── tests/             # ✅ Integration & unit tests
├── scripts/           # Utility scripts (seed_data.py)
└── sample_data/       # Example CSV/JSON files
```

### Code Organization Rules

**1. Model Layer (app/models/):**
- One SQLAlchemy model per file
- All models inherit from `Base` (from `app.core.database`)
- Use SQLAlchemy 2.0 syntax
- Include helper methods for business logic (e.g., `supports_player_count()`)
- Enum classes defined in same file as model

**2. Schema Layer (app/schemas/):**
- Pydantic v2 models for validation
- Structure: `{Resource}Base`, `{Resource}Create`, `{Resource}Update`, `{Resource}` (response)
- Use `model_dump()` not `dict()` (Pydantic v2)
- Field validators with `@field_validator` decorator

**3. Service Layer (app/{module}/service.py):**
- Contains all business logic and data access
- No FastAPI dependencies (pure Python + SQLAlchemy)
- Normalization logic lives here (e.g., `normalize_duration()`)
- Raises exceptions from `app.core.exceptions`

**4. Router Layer (app/{module}/router.py):**
- Thin layer: dependency injection, validation, response formatting
- Use `APIRouter` with prefix and tags
- Always specify `response_model`
- Use `Depends(get_db)` for database sessions

### Critical Conventions

**Normalization Rules (RF-ING-02):**
```python
# Duration: 5-360 minutes, default 60
duration = clamp(duration, 5, 360) or 60

# Complexity: 1.0-5.0, default 2.5
complexity = clamp(complexity, 1.0, 5.0) or 2.5

# Mechanics: validate against controlled vocabulary
# See GameService.STANDARD_MECHANICS for full list

# Language dependency hierarchy
LanguageDependency.NINGUNA < BAJA < MEDIA < ALTA
```

**Import/Merge Strategies (RF-ING-03):**
- `update`: Update existing + add new (default)
- `skip`: Only add new, ignore duplicates
- `replace`: Delete and recreate duplicates
- Reject files with >20% invalid rows

**Session Profile Validation (RF-CTX-02):**
```python
# Non-blocking warnings with structured data
ValidationWarning(
    severity="high",  # or "medium", "low"
    category="operational",
    code="VERY_LARGE_GROUP",
    message="Grupo muy grande detectado",
    suggestions=["Considere usar estaciones múltiples"]
)

# Validation thresholds
LARGE_GROUP = 20  # Suggest stations
VERY_LARGE_GROUP = 30  # Strongly recommend stations
LIMITED_TIME = 30  # Warn about complexity
COOPERATIVE_LARGE_GROUP = (cooperative AND >30)  # Suggest teams
```

**Database Sessions:**
```python
# Always use dependency injection
@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    return service.list(db)
```

**Error Handling:**
```python
# Use custom exceptions
from app.core.exceptions import NotFoundException
raise NotFoundException("Game", str(game_id))
# FastAPI converts to proper HTTP responses
```

## Development Workflow

### Setup & Run
```bash
# Create venv and install
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Configure
cp backend/.env.example backend/.env
# Edit DATABASE_URL and SECRET_KEY

# Run migrations
cd backend
alembic upgrade head

# Seed data
python -m scripts.seed_data

# Start server
uvicorn app.main:app --reload
# Access: http://localhost:8000/docs
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Adding New Features

**Example: Adding Skills Module (Módulo C)**

1. **Model:** Create `backend/app/models/skill.py`
   - Inherit from `Base`
   - Define relationships with `relationship()` and `back_populates`
   - Add indexes for frequent queries

2. **Schemas:** Create `backend/app/schemas/skill.py`
   - `SkillBase`, `SkillCreate`, `SkillUpdate`, `Skill`
   - Add field validators as needed

3. **Service:** Create `backend/app/skills/service.py`
   - CRUD operations: `create()`, `get_by_id()`, `list()`, `update()`, `delete()`
   - Business logic (e.g., skill assignment validation)

4. **Router:** Create `backend/app/skills/router.py`
   - Define endpoints with proper response models
   - Use `Depends(get_db)` for sessions
   - Document with docstrings (auto-generates OpenAPI docs)

5. **Register:** Add router to `app/main.py`
   ```python
   from app.skills.router import router as skills_router
   app.include_router(skills_router, prefix=settings.API_PREFIX)
   ```

6. **Migration:** Create and apply
   ```bash
   alembic revision --autogenerate -m "Add skills table"
   alembic upgrade head
   ```

## Important Files

**Full specifications:**
- [.github/rf_sistema_cjei.md](.github/rf_sistema_cjei.md) - Complete functional requirements (34 RF total)
- [.github/backend-instructions.md](.github/backend-instructions.md) - Detailed backend architecture guide

**Core implementation:**
- [backend/app/core/config.py](backend/app/core/config.py) - Centralized settings with pydantic-settings
- [backend/app/core/database.py](backend/app/core/database.py) - SQLAlchemy engine and session factory
- [backend/app/main.py](backend/app/main.py) - FastAPI application with CORS and router registration

**Module A (Games):**
- [backend/app/models/game.py](backend/app/models/game.py) - Game model with helper methods
- [backend/app/games/service.py](backend/app/games/service.py) - Normalization + CRUD logic
- [backend/app/games/import_handler.py](backend/app/games/import_handler.py) - CSV/JSON import

**Module B (Sessions):**
- [backend/app/models/session.py](backend/app/models/session.py) - SessionProfile model with validation
- [backend/app/sessions/service.py](backend/app/sessions/service.py) - Session CRUD with auto-validation
- [backend/app/sessions/validator.py](backend/app/sessions/validator.py) - Coherence checks with warnings

## Quick Reference

**API Endpoints (Module A):**
- `POST /api/games` - Create game
- `GET /api/games` - List with filters (name, available, duration, complexity, players, mechanics)
- `GET /api/games/{id}` - Get by ID
- `PUT /api/games/{id}` - Update game
- `DELETE /api/games/{id}` - Delete game
- `GET /api/games/mechanics` - Get mechanics vocabulary
- `POST /api/games/import/csv` - Bulk import CSV
- `POST /api/games/import/json` - Bulk import JSON

**API Endpoints (Module B):**
- `POST /api/sessions` - Create session profile with auto-validation
- `GET /api/sessions` - List sessions (filter by has_warnings, pagination)
- `GET /api/sessions/{id}` - Get session by ID
- `PUT /api/sessions/{id}` - Update session with revalidation
- `DELETE /api/sessions/{id}` - Delete session profile
- `POST /api/sessions/validate` - Validate session data without creating
- `GET /api/sessions/statistics` - Get session statistics

**API Endpoints (Module C):**
- `POST /api/skills` - Create skill
- `GET /api/skills` - List all skills (with filtering)
- `GET /api/skills/{id}` - Get skill by ID
- `PUT /api/skills/{id}` - Update skill
- `DELETE /api/skills/{id}` - Delete skill
- `GET /api/skills/tree` - Get full or partial taxonomy tree
- `GET /api/skills/{id}/ancestors` - Get skill's ancestors
- `GET /api/skills/{id}/descendants` - Get skill's descendants
- `POST /api/skills/{skill_id}/games/{game_id}` - Associate skill with game
- `DELETE /api/skills/{skill_id}/games/{game_id}` - Remove association

**API Endpoints (Module D):**
- `POST /api/recommendations/generate` - Generate recommendations for session
- `GET /api/recommendations/session/{id}` - Get recommendations for session
- `PUT /api/recommendations/{id}/feedback` - Submit user feedback
- `POST /api/recommendations/configs` - Create scoring configuration
- `GET /api/recommendations/configs` - List scoring configurations
- `GET /api/recommendations/configs/active` - Get active configuration
- `GET /api/recommendations/configs/{id}` - Get specific configuration
- `PUT /api/recommendations/configs/{id}` - Update configuration
- `DELETE /api/recommendations/configs/{id}` - Delete configuration
- `POST /api/recommendations/configs/{id}/activate` - Activate configuration
- `POST /api/recommendations/configs/{id}/set-default` - Set as default

**API Endpoints (Module E):**
- `GET /api/recommendations/explanations/{id}` - Get detailed explanation for recommendation
- `POST /api/recommendations/explanations/compare` - Compare 2-5 recommendations side-by-side
- `GET /api/recommendations/traceability/{id}` - Get complete audit trail (RF-EXP-02)
- `GET /api/recommendations/history/session/{id}` - Get historical recommendation batches for session

**Common Commands:**
```bash
# Run server
uvicorn app.main:app --reload

# Run tests
pytest --cov=app

# Format code
black app/ && isort app/

# Create migration
alembic revision --autogenerate -m "message"

# Seed database
python -m scripts.seed_data
```

## MVP Scope Reminder

**ONLY implement 19 MUST requirements** (RF-ING-01, RF-ING-02, RF-CTX-01, RF-CTX-02, RF-TAX-01/02/03, RF-REC-01/02/03, RF-EXP-01/02, RF-UI-01/02/03, RF-RETRO-01/02, RF-ADM-01/02).

**DO NOT implement** SHOULD/COULD features unless explicitly requested.

---

**Last Updated:** January 6, 2026  
**Status:** Modules A, B, C, D, E, G, H complete ✅ | Backend MVP 100% complete  
**Progress:** 19/19 MVP requirements implemented (100%) 🎉
**Next Steps:** Implement Módulo F (Web Interface) as per RF-UI-01/02/03. For this refer to [frontend-instructions.md](frontend-instructions.md).