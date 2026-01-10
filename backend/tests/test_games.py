"""
Basic tests for Game API (Module A - RF-ING-01, RF-ING-02).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.game import LanguageDependency

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_game():
    """Test creating a game (RF-ING-01)."""
    response = client.post(
        "/api/games",
        json={
            "name": "Test Game",
            "bgg_id": 999,
            "duration_min": 60,
            "complexity": 2.5,
            "min_players": 2,
            "max_players": 4,
            "mechanics": ["Dice Rolling", "Hand Management"],
            "language_dependency": "baja",
            "available": True
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Game"
    assert data["bgg_id"] == 999
    assert data["id"] is not None


def test_normalization_duration(setup_database):
    """Test duration normalization (RF-ING-02)."""
    # Duration below minimum
    response = client.post(
        "/api/games",
        json={
            "name": "Quick Game",
            "bgg_id": 1001,
            "duration_min": 2,  # Below minimum (5)
            "complexity": 2.0,
            "min_players": 2,
            "max_players": 4,
            "mechanics": [],
            "language_dependency": "baja"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["duration_min"] == 5  # Clamped to minimum


def test_normalization_complexity(setup_database):
    """Test complexity normalization (RF-ING-02)."""
    # Complexity above maximum
    response = client.post(
        "/api/games",
        json={
            "name": "Complex Game",
            "bgg_id": 1002,
            "duration_min": 120,
            "complexity": 6.0,  # Above maximum (5.0)
            "min_players": 2,
            "max_players": 4,
            "mechanics": [],
            "language_dependency": "alta"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["complexity"] == 5.0  # Clamped to maximum


def test_list_games_with_filters(setup_database):
    """Test listing games with filters."""
    # Create test games
    games_data = [
        {"name": "Short Game", "bgg_id": 2001, "duration_min": 30, "complexity": 1.5, "min_players": 2, "max_players": 4},
        {"name": "Long Game", "bgg_id": 2002, "duration_min": 180, "complexity": 3.5, "min_players": 2, "max_players": 6},
    ]
    
    for game in games_data:
        game["mechanics"] = []
        game["language_dependency"] = "baja"
        client.post("/api/games", json=game)
    
    # Filter by duration
    response = client.get("/api/games?max_duration=60")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Short Game"


def test_duplicate_bgg_id(setup_database):
    """Test that duplicate BGG IDs are rejected."""
    game_data = {
        "name": "Original Game",
        "bgg_id": 3001,
        "duration_min": 60,
        "complexity": 2.0,
        "min_players": 2,
        "max_players": 4,
        "mechanics": [],
        "language_dependency": "baja"
    }
    
    # Create first game
    response1 = client.post("/api/games", json=game_data)
    assert response1.status_code == 201
    
    # Try to create duplicate
    game_data["name"] = "Duplicate Game"
    response2 = client.post("/api/games", json=game_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


def test_get_game_by_id(setup_database):
    """Test retrieving a game by ID."""
    # Create game
    create_response = client.post(
        "/api/games",
        json={
            "name": "Retrievable Game",
            "bgg_id": 4001,
            "duration_min": 90,
            "complexity": 2.8,
            "min_players": 3,
            "max_players": 5,
            "mechanics": ["Worker Placement"],
            "language_dependency": "media"
        }
    )
    game_id = create_response.json()["id"]
    
    # Retrieve game
    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Retrievable Game"
    assert data["bgg_id"] == 4001


def test_update_game(setup_database):
    """Test updating a game."""
    # Create game
    create_response = client.post(
        "/api/games",
        json={
            "name": "Original Name",
            "bgg_id": 5001,
            "duration_min": 60,
            "complexity": 2.0,
            "min_players": 2,
            "max_players": 4,
            "mechanics": [],
            "language_dependency": "baja"
        }
    )
    game_id = create_response.json()["id"]
    
    # Update game
    response = client.put(
        f"/api/games/{game_id}",
        json={"name": "Updated Name", "complexity": 3.0}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["complexity"] == 3.0
    assert data["bgg_id"] == 5001  # Unchanged


def test_delete_game(setup_database):
    """Test deleting a game."""
    # Create game
    create_response = client.post(
        "/api/games",
        json={
            "name": "To Be Deleted",
            "bgg_id": 6001,
            "duration_min": 45,
            "complexity": 2.0,
            "min_players": 2,
            "max_players": 4,
            "mechanics": [],
            "language_dependency": "baja"
        }
    )
    game_id = create_response.json()["id"]
    
    # Delete game
    response = client.delete(f"/api/games/{game_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/games/{game_id}")
    assert get_response.status_code == 404


def test_mechanics_vocabulary(setup_database):
    """Test getting mechanics vocabulary."""
    # Create games with different mechanics
    client.post(
        "/api/games",
        json={
            "name": "Game 1",
            "bgg_id": 7001,
            "mechanics": ["Dice Rolling", "Trading"],
            "duration_min": 60,
            "complexity": 2.0,
            "min_players": 2,
            "max_players": 4,
            "language_dependency": "baja"
        }
    )
    
    client.post(
        "/api/games",
        json={
            "name": "Game 2",
            "bgg_id": 7002,
            "mechanics": ["Worker Placement", "Trading"],
            "duration_min": 90,
            "complexity": 3.0,
            "min_players": 2,
            "max_players": 4,
            "language_dependency": "media"
        }
    )
    
    # Get vocabulary
    response = client.get("/api/games/mechanics")
    assert response.status_code == 200
    mechanics = response.json()
    assert "Dice Rolling" in mechanics
    assert "Trading" in mechanics
    assert "Worker Placement" in mechanics
