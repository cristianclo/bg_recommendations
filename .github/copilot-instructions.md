# GitHub Copilot Instructions - CJEI Recommendations System

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
- [backend/app/sessions/router.py](backend/app/sessions/router.py) - 6 CRUD endpoints + validate + statistics
- [backend/tests/test_sessions.py](backend/tests/test_sessions.py) - 15 unit tests covering RF-CTX-01/02

**Validation warning system:**
- `LARGE_GROUP` (>20): Suggests multiple stations
- `VERY_LARGE_GROUP` (>30): Strongly recommends stations
- `LIMITED_TIME` (<30min): Warns about complexity limitations
- `COOPERATIVE_LARGE_GROUP` (cooperative + >30): Suggests team subdivision
- All warnings are **non-blocking** and include severity, category, code, message, and suggestions

### 🔄 Pending Modules

- **Módulo C:** Skills taxonomy management (RF-TAX-01, RF-TAX-02, RF-TAX-03)
- **Módulo D:** Recommendation engine (RF-REC-01, RF-REC-02, RF-REC-03)
- **Módulo E:** Explainability & traceability (RF-EXP-01, RF-EXP-02)
- **Módulo F:** Web interface (RF-UI-01, RF-UI-02, RF-UI-03)
- **Módulo G:** Feedback system (RF-RETRO-01, RF-RETRO-02)
- **Módulo H:** Administration (RF-ADM-01, RF-ADM-02)

## Architecture Patterns

### Project Structure
```
backend/
├── app/
│   ├── core/          # Config, database, exceptions, dependencies
│   ├── models/        # SQLAlchemy ORM (one class per file)
│   ├── schemas/       # Pydantic validation (matching model names)
│   ├── games/         # Feature module (router + service + handlers)
│   ├── sessions/      # Session profile module (router + service + validator)
│   └── main.py        # FastAPI app entry point
├── alembic/           # Database migrations
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

**Last Updated:** January 5, 2026  
**Status:** Module A complete, Module B complete, ready for Module C (Skills Taxonomy)
