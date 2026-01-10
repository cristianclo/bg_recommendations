# GitHub Copilot Instructions - CJEI Board Game Recommendation System

## Project Overview

**Project Name:** `cjei-recommendations`  
**Purpose:** Sistema de recomendación de juegos de mesa para asesores pedagógicos del Centro de Juegos y Experiencias Interactivas (CJEI) de la Pontificia Universidad Javeriana Cali. El sistema recomienda juegos según objetivos de aprendizaje, habilidades a desarrollar y restricciones operativas de clase.

**Key Technologies:**
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy 2.0, PostgreSQL 14+
- **Authentication:** JWT with python-jose, bcrypt
- **Validation:** Pydantic v2
- **Migrations:** Alembic
- **Deployment:** Docker + Docker Compose

**Target Environment:** Docker containers (development), cloud deployment ready (production)

**MVP Scope:** Implementar únicamente los 19 requerimientos funcionales con prioridad MUST según documento de especificaciones.

---

## Architecture

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── core/                        # Core utilities and configuration
│   │   ├── config.py                # Settings with pydantic-settings
│   │   ├── database.py              # SQLAlchemy setup, SessionLocal, Base
│   │   ├── security.py              # JWT creation/validation, password hashing
│   │   ├── dependencies.py          # FastAPI dependencies (get_db, get_current_user, require_admin)
│   │   └── exceptions.py            # Custom HTTP exceptions
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── user.py                  # User model with UserRole enum
│   │   ├── game.py                  # Game model with LanguageDependency enum
│   │   ├── skill.py                 # Skill + SkillAssignment models
│   │   ├── session.py               # SessionProfile model
│   │   ├── recommendation.py        # Recommendation + RecommendationConfig models
│   │   └── feedback.py              # Feedback model
│   ├── schemas/                     # Pydantic schemas (request/response models)
│   │   ├── user.py                  # UserCreate, User, LoginRequest, Token
│   │   ├── game.py                  # GameCreate, GameUpdate, Game, GameList
│   │   ├── skill.py                 # SkillCreate, Skill, AssignSkillsRequest
│   │   ├── session.py               # SessionProfileCreate, ValidationWarning
│   │   ├── recommendation.py        # RecommendationResult, RecommendationExplanation
│   │   └── feedback.py              # FeedbackCreate, FeedbackSummary
│   ├── auth/                        # Authentication module
│   │   ├── router.py                # Endpoints: /login, /me, /register
│   │   └── service.py               # Business logic: authenticate_user, create_token
│   ├── games/                       # Games management module
│   │   ├── router.py                # CRUD endpoints for games
│   │   ├── service.py               # Game business logic + normalization
│   │   └── import_handler.py        # CSV/JSON import logic
│   ├── skills/                      # Skills taxonomy module
│   │   ├── router.py                # CRUD endpoints for skills + assignment
│   │   └── service.py               # Skill business logic + validation
│   ├── recommendations/             # Recommendation engine module
│   │   ├── router.py                # Endpoints: /generate, /sessions/{id}, /config
│   │   ├── engine.py                # Core algorithm: filters, scoring, explanations
│   │   ├── validator.py             # SessionProfile validation + warnings
│   │   ├── service.py               # Orchestration layer
│   │   └── config.py                # RecommendationConfig management
│   ├── feedback/                    # Feedback module
│   │   ├── router.py                # CRUD endpoints + summary
│   │   └── service.py               # Feedback aggregation + skill discrepancy detection
│   └── admin/                       # Admin utilities (optional)
│       └── router.py                # Admin-only endpoints
├── alembic/                         # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                           # Pytest test suite
│   ├── conftest.py                  # Test fixtures
│   ├── test_auth.py
│   ├── test_games.py
│   ├── test_recommendations.py
│   └── test_feedback.py
├── scripts/                         # Utility scripts
│   ├── seed_data.py                 # Initial data seeding (users, skills, games)
│   └── import_bgg.py                # BoardGameGeek import script
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

### Key Components

**1. Core Layer (app/core/)**
- `config.py`: Centralized settings using pydantic-settings, loads from `.env`
- `database.py`: SQLAlchemy engine, SessionLocal factory, Base declarative
- `security.py`: JWT token creation/validation, bcrypt password hashing
- `dependencies.py`: FastAPI dependency injection (database sessions, auth)
- `exceptions.py`: Custom HTTP exceptions (NotFoundException, ForbiddenException)

**2. Data Layer (app/models/)**
All models inherit from `Base` and use SQLAlchemy 2.0 syntax:
- **User**: Authentication and authorization (roles: asesor, admin)
- **Game**: Board game catalog with normalized attributes
- **Skill**: Taxonomy of educational skills (cognitive, social, emotional)
- **SkillAssignment**: Audit trail of skill-to-game mappings
- **SessionProfile**: Class context (objectives, time, group size, constraints)
- **Recommendation**: Generated recommendations with explanations (traceability)
- **RecommendationConfig**: Scoring weights configuration
- **Feedback**: Post-session feedback from advisors

**3. API Layer (app/routers/)**
All routers use FastAPI with automatic OpenAPI documentation:
- **Auth**: Login, token generation, user management
- **Games**: CRUD + import/export + mechanics vocabulary
- **Skills**: CRUD + assignment to games
- **Recommendations**: Generate recommendations + config management
- **Feedback**: Submit feedback + view summaries

**4. Business Logic Layer (app/services/)**
- **GameService**: Normalization, validation, CRUD operations
- **SkillService**: Taxonomy management, assignment logic
- **RecommendationEngine**: Core algorithm (filters → scoring → ranking)
- **SessionValidator**: Context validation with warnings
- **FeedbackService**: Aggregation, summaries, skill discrepancy detection

### Data Flow Patterns

**Recommendation Generation Flow:**
```
User Request (SessionProfileCreate)
    ↓
SessionValidator (warnings)
    ↓
SessionProfile saved to DB
    ↓
RecommendationEngine.generate_recommendations()
    ↓
    ├─ Apply hard filters (available, players, time, language)
    ├─ Calculate scores (skill + mechanics + difficulty + rank)
    ├─ Generate explanations
    └─ Sort and return Top-N
    ↓
Save Recommendations to DB (traceability)
    ↓
Return RecommendationResult[] to client
```

**Feedback Loop:**
```
Advisor uses recommended game in class
    ↓
Submits Feedback (utility rating, what worked/didn't work)
    ↓
FeedbackService aggregates by game
    ↓
Summary includes: avg utility, rating distribution, skill discrepancies
    ↓
Future recommendations can use feedback for boosting (post-MVP)
```

---

## Development Workflow

### Setup
```bash
# Clone repository
git clone <repository-url>
cd cjei-recommendations/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration (DATABASE_URL, SECRET_KEY)

# Initialize database
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

### Build & Run

**Development (local):**
```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access:
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

**Development (Docker):**
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

**Production:**
```bash
# Build production image
docker build -t cjei-recommendations:latest .

# Run with proper secrets
docker run -p 8000:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e SECRET_KEY=$SECRET_KEY \
  cjei-recommendations:latest
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_recommendations.py

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "not slow"
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

---

## Conventions & Patterns

### Code Style

**Python:**
- Follow PEP 8 style guide
- Use Black formatter (line length: 100)
- Use isort for import sorting
- Type hints required for function signatures
- Docstrings for public functions (Google style)

**Naming:**
- **Files/Modules:** `snake_case` (e.g., `recommendation_engine.py`)
- **Classes:** `PascalCase` (e.g., `RecommendationEngine`)
- **Functions/Variables:** `snake_case` (e.g., `generate_recommendations`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RECOMMENDATIONS`)
- **Private methods:** `_leading_underscore` (e.g., `_apply_hard_filters`)

**File Organization:**
- One model class per file in `models/`
- Corresponding schemas in `schemas/` with same filename
- Routers, services, and business logic in feature modules
- Shared utilities in `core/`

**Import Order:**
1. Standard library imports
2. Third-party imports (fastapi, sqlalchemy, pydantic)
3. Local application imports (relative imports within module, absolute for cross-module)

Example:
```python
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.game import Game
from ..schemas.game import GameCreate
```

### Common Patterns

**Error Handling:**
```python
# Use custom exceptions from core.exceptions
from ..core.exceptions import NotFoundException

# In services:
def get_by_id(self, db: Session, id: UUID) -> Model:
    obj = db.query(Model).filter(Model.id == id).first()
    if not obj:
        raise NotFoundException("ResourceName", str(id))
    return obj

# FastAPI automatically converts to proper HTTP responses
```

**Database Sessions:**
```python
# Always use dependency injection for database sessions
from fastapi import Depends
from sqlalchemy.orm import Session
from ..core.dependencies import get_db

@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    # Session automatically closes after request
    return db.query(Item).all()
```

**Authentication:**
```python
# For authenticated endpoints:
from ..core.dependencies import get_current_user
from ..models.user import User

@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is automatically validated and injected
    return {"user": current_user.email}

# For admin-only endpoints:
from ..core.dependencies import require_admin

@router.post("/admin-only")
def admin_route(admin_user: User = Depends(require_admin)):
    # Automatically returns 403 if user is not admin
    return {"message": "Admin access granted"}
```

**Response Models:**
```python
# Always specify response_model for type safety and docs
from ..schemas.game import Game

@router.get("/games/{id}", response_model=Game)
def get_game(id: UUID, db: Session = Depends(get_db)):
    return game_service.get_by_id(db, id)

# For lists with pagination:
from ..schemas.game import GameList

@router.get("/games", response_model=GameList)
def list_games(...):
    return GameList(items=games, total=total, page=page, ...)
```

**Logging:**
```python
import logging

logger = logging.getLogger(__name__)

# In services:
logger.info(f"Generating recommendations for session {session_id}")
logger.warning(f"Only {count} games passed filters")
logger.error(f"Failed to import game: {error}", exc_info=True)
```

**Configuration:**
```python
# Always use settings from core.config
from ..core.config import settings

# Access settings:
database_url = settings.DATABASE_URL
secret_key = settings.SECRET_KEY
```

---

## Important Notes

### Critical Constraints

**1. MVP Scope - MUST Requirements Only:**
Implement ONLY these 19 requirements marked as MUST:
- RF-ING-01, RF-ING-02 (Games import & normalization)
- RF-CTX-01, RF-CTX-02 (Session profile & validation)
- RF-TAX-01, RF-TAX-02, RF-TAX-03 (Skills taxonomy & assignment)
- RF-REC-01, RF-REC-02, RF-REC-03 (Recommendation engine)
- RF-EXP-01, RF-EXP-02 (Explanations & traceability)
- RF-UI-01, RF-UI-02, RF-UI-03 (Auth & basic UI endpoints)
- RF-RETRO-01, RF-RETRO-02 (Feedback system)
- RF-ADM-01, RF-ADM-02 (Admin CRUD)

Do NOT implement Should/Could requirements (e.g., NLP skill suggestion, templates, advanced analytics).

**2. Algorithm Specifications:**

**Recommendation Engine Must:**
- Apply hard filters in order: `available=True` → `players` → `time` → `language`
- Calculate score from 4 weighted components (default: 40-30-20-10):
  - Skill similarity: 1.0 if primary matches, 0.5 if secondary matches
  - Mechanics relevance: heuristic based (MVP uses simple rules)
  - Difficulty appropriateness: optimal range 2.0-3.5 complexity
  - BGG rank: normalized 0-1 (lower rank = higher score)
- Return Top-N (default 10) sorted by score descending
- Generate structured explanation with ≥3 reasons per recommendation
- If <3 results, invoke `_handle_no_results()` with relaxation suggestions

**Session Validation Must:**
- Emit warnings (not errors) for:
  - Group >20: suggest stations/multiple tables
  - Group >30: strongly recommend stations
  - Time <30min: warn about complexity limitations
  - Cooperative + group >30: suggest team subdivision
- Never block query based on warnings

**3. Data Normalization Rules:**

**Game Attributes:**
- `duration_min`: clamp to 5-360, default 60 if missing
- `complexity`: clamp to 1.0-5.0, default 2.5 if missing
- `mechanics`: validate against controlled vocabulary (18 standard mechanics)
- `language_dependency`: enum ["ninguna", "baja", "media", "alta"]
- `bgg_rank`: nullable, used for scoring if present

**Skill Assignment:**
- Every game MUST have `primary_skill_id` (required)
- `secondary_skill_id` is optional
- Audit trail in `SkillAssignment` table (who assigned, when, notes)

**4. Security Requirements:**

**Authentication:**
- JWT tokens expire after 120 minutes (configurable)
- Passwords hashed with bcrypt
- Tokens include: `sub` (email), `role`, `exp`
- Never return passwords in responses

**Authorization:**
- Asesores can: create sessions, view recommendations, submit feedback
- Admins can: all asesor actions + CRUD games/skills + modify config
- Use `get_current_user` dependency for auth, `require_admin` for admin routes

**CORS:**
- Allow origins: `["http://localhost:3000", "http://localhost:5173"]` (React dev servers)
- Allow credentials: True
- Configure properly for production deployment

**5. Database Best Practices:**

**Indexing:**
Create indexes on frequently queried fields:
- `users.email` (unique)
- `games.bgg_id` (unique)
- `games.name`
- `games.available`
- `skills.name` (unique)

**Relationships:**
- Use `relationship()` for ORM navigation (e.g., `game.primary_skill`)
- Use `back_populates` for bidirectional relationships if needed
- Lazy loading by default (joinedload for eager loading when needed)

**Migrations:**
- Always use Alembic for schema changes
- Never modify database directly
- Test migrations with both upgrade and downgrade

**6. Testing Requirements:**

**Minimum Coverage:**
- 70%+ coverage on business logic (services, engine, validators)
- 100% coverage on security functions (JWT, password hashing)
- Test happy paths and error cases

**Critical Tests:**
- Authentication: login success/failure, token validation
- Recommendation engine: various profiles, edge cases, no results
- Normalization: out-of-range values, missing data
- Skill assignment: audit trail, validation
- Feedback: editability window, skill discrepancies

**7. Performance Targets:**

- Recommendation generation: <5 seconds (95th percentile)
- API response time: <500ms for CRUD operations
- Database queries: <100ms for single-record lookups
- Pagination: max 100 items per page

**8. Environment-Specific Considerations:**

**Development:**
- SQLite acceptable for quick local development
- PostgreSQL recommended even in dev for compatibility
- Auto-reload enabled
- Verbose logging

**Production:**
- PostgreSQL required
- Proper SECRET_KEY (cryptographically secure)
- HTTPS only
- Rate limiting (future enhancement)
- Monitoring and logging aggregation

### Gotchas and Non-Obvious Behaviors

**1. Pydantic v2 Changes:**
- Use `model_dump()` instead of `dict()`
- Use `model_validate()` instead of `parse_obj()`
- Use `ConfigDict` instead of inner `Config` class in newer Pydantic patterns

**2. SQLAlchemy 2.0 Patterns:**
- Use `select()` for queries in 2.0 style (MVP can use legacy Query API for simplicity)
- Always use `session.commit()` explicitly (no autocommit)
- Use `session.refresh()` after commit to get updated object

**3. FastAPI Specifics:**
- Dependency functions must be sync or async consistently
- Use `Depends()` for injection, not manual instantiation
- Response models automatically exclude None fields unless configured

**4. Language Dependency Hierarchy:**
```python
LANGUAGE_HIERARCHY = {
    "ninguna": 0,  # No text, only images/numbers
    "baja": 1,     # Minimal text (card names, simple instructions)
    "media": 2,    # Moderate text (flavor text, abilities)
    "alta": 3      # Heavy text (storytelling, complex rules)
}
# Filter: game.language_dependency <= profile.language_restriction
```

**5. Feedback Edit Window:**
- Feedback editable for 7 days after creation
- Use `feedback.is_editable()` method to check
- Enforce in update endpoint with 403 if expired

**6. Skill Discrepancy Detection:**
- Only flag if <50% of feedback reports match assigned primary skill
- Requires minimum 3 feedback entries to be meaningful
- Display in game feedback summary, not blocking

**7. Import/Export:**
- CSV import validates structure before processing
- Reject entire file if >20% rows invalid
- Report: imported, updated, rejected counts
- Duplicate detection by `bgg_id`

### Key Dependencies and Purposes

- **fastapi**: Web framework, automatic OpenAPI docs
- **uvicorn**: ASGI server for running FastAPI
- **sqlalchemy**: ORM for database operations
- **alembic**: Database migration management
- **pydantic**: Data validation and serialization
- **pydantic-settings**: Environment configuration management
- **python-jose**: JWT token generation/validation
- **passlib**: Password hashing with bcrypt
- **psycopg2-binary**: PostgreSQL adapter
- **pytest**: Testing framework
- **httpx**: HTTP client for testing API endpoints

---

## Quick Reference

### Common Commands Cheat Sheet

```bash
# Start development server
uvicorn app.main:app --reload

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py

# Format code
black app/
isort app/

# Docker quick start
docker-compose up --build

# Access container shell
docker-compose exec backend bash

# View logs
docker-compose logs -f backend
```

### API Endpoints Quick Reference

**Authentication:**
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Get current user info

**Games:**
- `GET /api/games` - List games (paginated, filterable)
- `POST /api/games` - Create game (admin)
- `PUT /api/games/{id}` - Update game (admin)
- `DELETE /api/games/{id}` - Delete game (admin)

**Skills:**
- `GET /api/skills` - List all skills
- `POST /api/skills` - Create skill (admin)
- `POST /api/skills/games/{id}/assign` - Assign skills to game

**Recommendations:**
- `POST /api/recommendations/generate` - Generate recommendations
- `GET /api/recommendations/sessions/{id}` - Get saved recommendations
- `GET /api/recommendations/config` - Get scoring weights
- `PUT /api/recommendations/config` - Update weights (admin)

**Feedback:**
- `POST /api/feedback` - Submit feedback
- `PUT /api/feedback/{id}` - Update feedback (7-day window)
- `GET /api/feedback/games/{id}/summary` - Get game feedback summary

---

**Last Updated:** January 2026  
**Project Version:** MVP 1.0  
**Python Version:** 3.11+  
**FastAPI Version:** 0.104+