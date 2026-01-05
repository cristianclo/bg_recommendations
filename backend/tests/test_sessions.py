"""
Tests for Module B - Session Profile functionality (RF-CTX-01, RF-CTX-02).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.session import SessionProfile

# Use PostgreSQL test database
# You can override with TEST_DATABASE_URL environment variable
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL + "_test" if "_test" not in settings.DATABASE_URL else settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop tables for each test."""
    # Create all tables (including session_profiles)
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up: delete all session profile records but keep table structure
    db = TestingSessionLocal()
    try:
        db.query(SessionProfile).delete()
        db.commit()
    finally:
        db.close()


def test_create_session_profile():
    """Test creating a basic session profile (RF-CTX-01)."""
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Develop critical thinking", "Team collaboration"],
            "primary_skill_name": "Critical Thinking",
            "available_time_min": 60,
            "group_size": 15,
            "max_language_dependency": "media",
            "preferred_modality": "cooperative"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["objectives"] == ["Develop critical thinking", "Team collaboration"]
    assert data["primary_skill_name"] == "Critical Thinking"
    assert data["group_size"] == 15
    assert data["available_time_min"] == 60


def test_validation_required_fields():
    """Test that required fields are validated (RF-CTX-01)."""
    # Missing objectives
    response = client.post(
        "/api/sessions",
        json={
            "primary_skill_name": "Critical Thinking",
            "available_time_min": 60,
            "group_size": 15
        }
    )
    assert response.status_code == 422
    
    # Missing primary skill
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Some objective"],
            "available_time_min": 60,
            "group_size": 15
        }
    )
    assert response.status_code == 422


def test_time_constraints_validation():
    """Test time constraints (15-240 minutes) (RF-CTX-01)."""
    # Time too short
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Test"],
            "primary_skill_name": "Test Skill",
            "available_time_min": 10,  # Below minimum (15)
            "group_size": 15
        }
    )
    assert response.status_code == 422
    
    # Time too long
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Test"],
            "primary_skill_name": "Test Skill",
            "available_time_min": 300,  # Above maximum (240)
            "group_size": 15
        }
    )
    assert response.status_code == 422


def test_group_size_constraints():
    """Test group size constraints (1-100) (RF-CTX-01)."""
    # Group size zero
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Test"],
            "primary_skill_name": "Test Skill",
            "available_time_min": 60,
            "group_size": 0  # Below minimum (1)
        }
    )
    assert response.status_code == 422
    
    # Group size too large
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Test"],
            "primary_skill_name": "Test Skill",
            "available_time_min": 60,
            "group_size": 150  # Above maximum (100)
        }
    )
    assert response.status_code == 422


def test_large_group_warning(setup_database):
    """Test that large groups (>20) generate warnings (RF-CTX-02)."""
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Team building"],
            "primary_skill_name": "Collaboration",
            "available_time_min": 60,
            "group_size": 25,  # >20, should trigger LARGE_GROUP warning
            "max_language_dependency": "media",
            "preferred_modality": "any"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["has_warnings"] is True
    assert len(data["validation_warnings"]) > 0
    
    # Check for LARGE_GROUP warning
    warning_codes = [w["code"] for w in data["validation_warnings"]]
    assert "LARGE_GROUP" in warning_codes


def test_very_large_group_warning(setup_database):
    """Test that very large groups (>30) generate stronger warnings (RF-CTX-02)."""
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Workshop"],
            "primary_skill_name": "Communication",
            "available_time_min": 90,
            "group_size": 35,  # >30, should trigger VERY_LARGE_GROUP warning
            "max_language_dependency": "baja",
            "preferred_modality": "any"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["has_warnings"] is True
    
    # Check for VERY_LARGE_GROUP warning
    warning_codes = [w["code"] for w in data["validation_warnings"]]
    assert "VERY_LARGE_GROUP" in warning_codes
    
    # Verify suggestions include stations
    very_large_warning = next(w for w in data["validation_warnings"] if w["code"] == "VERY_LARGE_GROUP")
    suggestions_text = " ".join(very_large_warning["suggestions"]).lower()
    assert "station" in suggestions_text


def test_limited_time_warning(setup_database):
    """Test that limited time (<30min) generates warnings (RF-CTX-02)."""
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Quick activity"],
            "primary_skill_name": "Problem Solving",
            "available_time_min": 20,  # <30, should trigger LIMITED_TIME warning
            "group_size": 10,
            "max_language_dependency": "baja",
            "preferred_modality": "any"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["has_warnings"] is True
    
    # Check for LIMITED_TIME warning
    warning_codes = [w["code"] for w in data["validation_warnings"]]
    assert "LIMITED_TIME" in warning_codes
    
    # Verify suggestions mention complexity
    limited_time_warning = next(w for w in data["validation_warnings"] if w["code"] == "LIMITED_TIME")
    suggestions_text = " ".join(limited_time_warning["suggestions"]).lower()
    assert "complexity" in suggestions_text


def test_cooperative_large_group_warning(setup_database):
    """Test cooperative + large group combination warning (RF-CTX-02)."""
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Teamwork"],
            "primary_skill_name": "Collaboration",
            "available_time_min": 60,
            "group_size": 35,  # >30
            "max_language_dependency": "media",
            "preferred_modality": "cooperative"  # Cooperative + large group
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["has_warnings"] is True
    
    # Check for COOPERATIVE_LARGE_GROUP warning
    warning_codes = [w["code"] for w in data["validation_warnings"]]
    assert "COOPERATIVE_LARGE_GROUP" in warning_codes
    
    # Verify suggestions mention teams/subdivision
    coop_warning = next(w for w in data["validation_warnings"] if w["code"] == "COOPERATIVE_LARGE_GROUP")
    suggestions_text = " ".join(coop_warning["suggestions"]).lower()
    assert "team" in suggestions_text or "subdivid" in suggestions_text


def test_no_warnings_normal_session(setup_database):
    """Test that normal sessions don't generate warnings (RF-CTX-02)."""
    response = client.post(
        "/api/sessions",
        json={
            "objectives": ["Standard class"],
            "primary_skill_name": "Critical Thinking",
            "available_time_min": 60,  # Normal time
            "group_size": 15,  # Normal group size
            "max_language_dependency": "media",
            "preferred_modality": "any"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["has_warnings"] is False
    assert len(data["validation_warnings"]) == 0


def test_list_sessions_with_filters(setup_database):
    """Test listing sessions with filters."""
    # Create sessions with different characteristics
    client.post("/api/sessions", json={
        "objectives": ["Test 1"],
        "primary_skill_name": "Skill A",
        "available_time_min": 60,
        "group_size": 10
    })
    
    client.post("/api/sessions", json={
        "objectives": ["Test 2"],
        "primary_skill_name": "Skill B",
        "available_time_min": 60,
        "group_size": 35  # Will have warnings
    })
    
    # Filter by warnings
    response = client.get("/api/sessions?has_warnings=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


def test_get_session_by_id(setup_database):
    """Test retrieving a session by ID."""
    # Create session
    create_response = client.post("/api/sessions", json={
        "session_name": "Test Session",
        "objectives": ["Objective 1"],
        "primary_skill_name": "Test Skill",
        "available_time_min": 60,
        "group_size": 15
    })
    session_id = create_response.json()["id"]
    
    # Retrieve session
    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_name"] == "Test Session"
    assert data["id"] == session_id


def test_update_session_revalidates(setup_database):
    """Test that updating key fields triggers revalidation (RF-CTX-02)."""
    # Create session without warnings
    create_response = client.post("/api/sessions", json={
        "objectives": ["Test"],
        "primary_skill_name": "Test Skill",
        "available_time_min": 60,
        "group_size": 15  # No warnings
    })
    session_id = create_response.json()["id"]
    assert create_response.json()["has_warnings"] is False
    
    # Update to trigger warnings
    update_response = client.put(
        f"/api/sessions/{session_id}",
        json={"group_size": 35}  # >30, should trigger warnings
    )
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["has_warnings"] is True
    assert data["group_size"] == 35


def test_delete_session(setup_database):
    """Test deleting a session."""
    # Create session
    create_response = client.post("/api/sessions", json={
        "objectives": ["Test"],
        "primary_skill_name": "Test Skill",
        "available_time_min": 60,
        "group_size": 15
    })
    session_id = create_response.json()["id"]
    
    # Delete session
    response = client.delete(f"/api/sessions/{session_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/sessions/{session_id}")
    assert get_response.status_code == 404


def test_get_session_statistics(setup_database):
    """Test getting session statistics."""
    # Create some sessions
    client.post("/api/sessions", json={
        "objectives": ["Test 1"],
        "primary_skill_name": "Skill A",
        "available_time_min": 60,
        "group_size": 10
    })
    
    client.post("/api/sessions", json={
        "objectives": ["Test 2"],
        "primary_skill_name": "Skill B",
        "available_time_min": 20,  # Will have LIMITED_TIME warning
        "group_size": 15
    })
    
    # Get statistics
    response = client.get("/api/sessions/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 2
    assert data["sessions_with_warnings"] == 1
    assert data["warning_rate"] == 50.0
