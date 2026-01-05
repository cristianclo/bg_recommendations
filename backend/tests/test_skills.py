"""
Unit tests for Skills taxonomy (Module C).
Tests RF-TAX-01, RF-TAX-02, and RF-TAX-03 requirements.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Use test database
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL + "_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


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
    """Create and clean tables for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean up: delete all skills between tests
    db = TestingSessionLocal()
    try:
        from app.models.skill import Skill
        db.query(Skill).delete()
        db.commit()
    finally:
        db.close()


# RF-TAX-02: CRUD operations

def test_create_root_skill():
    """Test creating a root-level skill (no parent)."""
    response = client.post(
        "/api/skills",
        json={
            "name": "Root Skill",
            "description": "A root skill",
            "parent_id": None,
            "is_active": True
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Root Skill"
    assert data["description"] == "A root skill"
    assert data["parent_id"] is None
    assert data["is_active"] is True
    assert data["is_root"] is True
    assert data["level"] == 0
    assert data["full_path"] == "Root Skill"


def test_create_child_skill():
    """Test creating a child skill with parent."""
    # Create parent first
    parent_response = client.post(
        "/api/skills",
        json={"name": "Parent Skill", "description": "Parent", "parent_id": None}
    )
    parent_id = parent_response.json()["id"]
    
    # Create child
    response = client.post(
        "/api/skills",
        json={
            "name": "Child Skill",
            "description": "Child of parent",
            "parent_id": parent_id
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Child Skill"
    assert data["parent_id"] == parent_id
    assert data["is_root"] is False
    assert data["level"] == 1
    assert data["full_path"] == "Parent Skill > Child Skill"


def test_create_skill_duplicate_name():
    """Test that duplicate skill names are rejected."""
    client.post("/api/skills", json={"name": "Unique Skill", "description": "First"})
    
    # Try to create with same name
    response = client.post("/api/skills", json={"name": "Unique Skill", "description": "Second"})
    
    assert response.status_code in [400, 422]  # Can be either validation or business logic error
    assert "already exists" in response.json()["detail"].lower()


def test_list_skills():
    """Test listing all skills."""
    # Create some skills
    client.post("/api/skills", json={"name": "Skill 1", "description": "First"})
    client.post("/api/skills", json={"name": "Skill 2", "description": "Second"})
    
    response = client.get("/api/skills")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(s["name"] == "Skill 1" for s in data)
    assert any(s["name"] == "Skill 2" for s in data)


def test_list_skills_root_only():
    """Test filtering to only root-level skills."""
    # Create root and child
    parent_response = client.post("/api/skills", json={"name": "Root", "description": "Root skill"})
    parent_id = parent_response.json()["id"]
    client.post("/api/skills", json={"name": "Child", "description": "Child skill", "parent_id": parent_id})
    
    response = client.get("/api/skills?root_only=true")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Root"
    assert data[0]["is_root"] is True


def test_list_skills_by_parent():
    """Test filtering skills by parent_id."""
    # Create hierarchy
    parent_response = client.post("/api/skills", json={"name": "Parent", "description": "Parent"})
    parent_id = parent_response.json()["id"]
    
    client.post("/api/skills", json={"name": "Child 1", "description": "First child", "parent_id": parent_id})
    client.post("/api/skills", json={"name": "Child 2", "description": "Second child", "parent_id": parent_id})
    
    response = client.get(f"/api/skills?parent_id={parent_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(s["parent_id"] == parent_id for s in data)


def test_list_skills_search():
    """Test searching skills by name and description."""
    client.post("/api/skills", json={"name": "Strategy", "description": "Strategic thinking"})
    client.post("/api/skills", json={"name": "Tactics", "description": "Tactical execution"})
    
    response = client.get("/api/skills?search=strategy")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("strategy" in s["name"].lower() or "strategy" in (s["description"] or "").lower() for s in data)


def test_get_skill_by_id():
    """Test retrieving a skill by ID."""
    create_response = client.post(
        "/api/skills",
        json={"name": "Test Skill", "description": "For testing"}
    )
    skill_id = create_response.json()["id"]
    
    response = client.get(f"/api/skills/{skill_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == skill_id
    assert data["name"] == "Test Skill"


def test_get_nonexistent_skill():
    """Test that getting non-existent skill returns 404."""
    response = client.get("/api/skills/99999")
    
    assert response.status_code == 404


def test_update_skill_name():
    """Test updating a skill's name."""
    create_response = client.post("/api/skills", json={"name": "Original", "description": "Original"})
    skill_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/skills/{skill_id}",
        json={"name": "Updated Name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Original"  # Unchanged


def test_update_skill_parent():
    """Test changing a skill's parent."""
    # Create two roots and one child
    root1 = client.post("/api/skills", json={"name": "Root 1", "description": "First root"}).json()
    root2 = client.post("/api/skills", json={"name": "Root 2", "description": "Second root"}).json()
    child = client.post("/api/skills", json={"name": "Child", "description": "Child", "parent_id": root1["id"]}).json()
    
    # Move child to root2
    response = client.put(
        f"/api/skills/{child['id']}",
        json={"parent_id": root2["id"]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["parent_id"] == root2["id"]
    assert data["full_path"] == "Root 2 > Child"


def test_update_skill_activate_deactivate():
    """Test activating/deactivating a skill."""
    create_response = client.post("/api/skills", json={"name": "Test", "description": "Test", "is_active": True})
    skill_id = create_response.json()["id"]
    
    # Deactivate
    response = client.put(f"/api/skills/{skill_id}", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Reactivate
    response = client.put(f"/api/skills/{skill_id}", json={"is_active": True})
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_delete_skill():
    """Test deleting a skill."""
    create_response = client.post("/api/skills", json={"name": "To Delete", "description": "Will be deleted"})
    skill_id = create_response.json()["id"]
    
    response = client.delete(f"/api/skills/{skill_id}")
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/skills/{skill_id}")
    assert get_response.status_code == 404


def test_delete_skill_cascade():
    """Test that deleting a parent cascades to children."""
    # Create parent with children
    parent = client.post("/api/skills", json={"name": "Parent", "description": "Parent"}).json()
    child1 = client.post("/api/skills", json={"name": "Child 1", "description": "First", "parent_id": parent["id"]}).json()
    child2 = client.post("/api/skills", json={"name": "Child 2", "description": "Second", "parent_id": parent["id"]}).json()
    
    # Delete parent
    response = client.delete(f"/api/skills/{parent['id']}")
    assert response.status_code == 204
    
    # Verify children are also deleted
    assert client.get(f"/api/skills/{child1['id']}").status_code == 404
    assert client.get(f"/api/skills/{child2['id']}").status_code == 404


# RF-TAX-01: Hierarchical taxonomy

def test_get_skill_tree():
    """Test retrieving the complete skill tree."""
    # Create hierarchy
    root = client.post("/api/skills", json={"name": "Root", "description": "Root"}).json()
    child1 = client.post("/api/skills", json={"name": "Child 1", "description": "First", "parent_id": root["id"]}).json()
    child2 = client.post("/api/skills", json={"name": "Child 2", "description": "Second", "parent_id": root["id"]}).json()
    grandchild = client.post("/api/skills", json={"name": "Grandchild", "description": "Grand", "parent_id": child1["id"]}).json()
    
    response = client.get("/api/skills/tree")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # One root
    assert data[0]["name"] == "Root"
    assert len(data[0]["children"]) == 2  # Two children
    
    # Check nested structure
    child1_data = next(c for c in data[0]["children"] if c["name"] == "Child 1")
    assert len(child1_data["children"]) == 1
    assert child1_data["children"][0]["name"] == "Grandchild"


def test_hierarchical_paths():
    """Test that full_path reflects hierarchy correctly."""
    root = client.post("/api/skills", json={"name": "A", "description": "Root"}).json()
    level1 = client.post("/api/skills", json={"name": "B", "description": "L1", "parent_id": root["id"]}).json()
    level2 = client.post("/api/skills", json={"name": "C", "description": "L2", "parent_id": level1["id"]}).json()
    
    assert level2["full_path"] == "A > B > C"
    assert level2["level"] == 2


def test_statistics():
    """Test skill statistics endpoint."""
    # Create some skills
    root1 = client.post("/api/skills", json={"name": "Root 1", "description": "R1"}).json()
    root2 = client.post("/api/skills", json={"name": "Root 2", "description": "R2"}).json()
    child1 = client.post("/api/skills", json={"name": "Child 1", "description": "C1", "parent_id": root1["id"]}).json()
    child2 = client.post("/api/skills", json={"name": "Child 2", "description": "C2", "parent_id": root1["id"], "is_active": False}).json()
    
    response = client.get("/api/skills/statistics")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_skills"] == 4
    assert data["active_skills"] == 3
    assert data["inactive_skills"] == 1
    assert data["root_skills"] == 2
    assert data["max_depth"] == 1
    assert data["leaf_skills"] >= 2  # At least child1 and child2


# RF-TAX-03: Hierarchy integrity validation

def test_circular_reference_prevention():
    """Test that circular references are prevented."""
    # Create grandparent > parent > child
    grandparent = client.post("/api/skills", json={"name": "Grandparent", "description": "GP"}).json()
    parent = client.post("/api/skills", json={"name": "Parent", "description": "P", "parent_id": grandparent["id"]}).json()
    child = client.post("/api/skills", json={"name": "Child", "description": "C", "parent_id": parent["id"]}).json()
    
    # Try to make grandparent a child of child (circular reference)
    response = client.put(
        f"/api/skills/{grandparent['id']}",
        json={"parent_id": child["id"]}
    )
    
    assert response.status_code in [400, 422]
    assert "circular" in response.json()["detail"].lower()


def test_self_parent_prevention():
    """Test that a skill cannot be its own parent."""
    skill = client.post("/api/skills", json={"name": "Self", "description": "Test"}).json()
    
    response = client.put(
        f"/api/skills/{skill['id']}",
        json={"parent_id": skill["id"]}
    )
    
    assert response.status_code in [400, 422]
    assert "own parent" in response.json()["detail"].lower()


def test_max_depth_enforcement():
    """Test that maximum hierarchy depth is enforced."""
    # Create chain up to max depth
    current_id = None
    for i in range(5):  # MAX_HIERARCHY_DEPTH is 5
        response = client.post(
            "/api/skills",
            json={"name": f"Level {i}", "description": f"L{i}", "parent_id": current_id}
        )
        assert response.status_code == 201
        current_id = response.json()["id"]
    
    # Try to create one more level (should fail)
    response = client.post(
        "/api/skills",
        json={"name": "Too Deep", "description": "Beyond max", "parent_id": current_id}
    )
    
    assert response.status_code in [400, 422]
    assert "maximum depth" in response.json()["detail"].lower()


def test_validate_hierarchy_endpoint():
    """Test the hierarchy validation endpoint."""
    # Create valid hierarchy
    root = client.post("/api/skills", json={"name": "Root", "description": "R"}).json()
    child = client.post("/api/skills", json={"name": "Child", "description": "C", "parent_id": root["id"]}).json()
    
    response = client.get("/api/skills/validate")
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["total_skills_checked"] == 2
    assert len(data["errors"]) == 0


def test_nonexistent_parent_validation():
    """Test that referencing non-existent parent fails."""
    response = client.post(
        "/api/skills",
        json={"name": "Orphan", "description": "Has invalid parent", "parent_id": 99999}
    )
    
    assert response.status_code == 404
