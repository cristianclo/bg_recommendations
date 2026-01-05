"""
Skills API router (Module C).
Implements RF-TAX-01, RF-TAX-02, and RF-TAX-03 endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import settings
from ..skills.service import SkillService
from ..schemas.skill import (
    Skill, SkillCreate, SkillUpdate, SkillSimple,
    SkillWithChildren, SkillTreeNode, SkillStatistics,
    HierarchyValidationResult
)

router = APIRouter(
    prefix="/skills",
    tags=["skills"]
)

skill_service = SkillService()


@router.post("", response_model=Skill, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new skill in the taxonomy (RF-TAX-02).
    
    - **name**: Unique skill name (required)
    - **description**: Detailed description (optional)
    - **parent_id**: Parent skill ID for hierarchy (optional, NULL for root)
    - **is_active**: Active status (default: true)
    
    Validates:
    - Name uniqueness
    - Parent existence
    - No circular references
    - Maximum hierarchy depth
    """
    skill = skill_service.create(db, skill_data)
    
    # Add computed fields for response
    return Skill(
        **skill.__dict__,
        full_path=skill.get_full_path(),
        level=skill.get_level(),
        children_count=len(skill.children),
        descendants_count=len(skill.get_descendants()),
        has_children=len(skill.children) > 0,
        is_root=skill.is_root()
    )


@router.get("", response_model=List[Skill])
def list_skills(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    active_only: bool = Query(False, description="Filter only active skills"),
    root_only: bool = Query(False, description="Filter only root-level skills"),
    parent_id: Optional[int] = Query(None, description="Filter by parent ID"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: Session = Depends(get_db)
):
    """
    List skills with filters (RF-TAX-02).
    
    Supports filtering by:
    - Active status
    - Root level only
    - Specific parent
    - Search term
    
    Returns paginated results.
    """
    skills = skill_service.list(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only,
        root_only=root_only,
        parent_id=parent_id,
        search=search
    )
    
    # Add computed fields for each skill
    return [
        Skill(
            **skill.__dict__,
            full_path=skill.get_full_path(),
            level=skill.get_level(),
            children_count=len(skill.children),
            descendants_count=len(skill.get_descendants()),
            has_children=len(skill.children) > 0,
            is_root=skill.is_root()
        )
        for skill in skills
    ]


@router.get("/tree", response_model=List[SkillTreeNode])
def get_skill_tree(
    root_id: Optional[int] = Query(None, description="Start from specific root skill"),
    active_only: bool = Query(False, description="Include only active skills"),
    db: Session = Depends(get_db)
):
    """
    Get hierarchical tree of skills (RF-TAX-01).
    
    Returns complete skill hierarchy with nested children.
    Can be filtered to start from a specific root or show only active skills.
    
    Useful for:
    - Displaying skill taxonomy in UI
    - Navigation through skill hierarchy
    - Understanding skill relationships
    """
    return skill_service.get_tree(db, root_id=root_id, active_only=active_only)


@router.get("/statistics", response_model=SkillStatistics)
def get_statistics(db: Session = Depends(get_db)):
    """
    Get taxonomy statistics (RF-TAX-01).
    
    Returns metrics about the skill taxonomy including:
    - Total/active/inactive counts
    - Root skills count
    - Maximum hierarchy depth
    - Average children per parent
    - Leaf skills count
    """
    return skill_service.get_statistics(db)


@router.get("/validate", response_model=HierarchyValidationResult)
def validate_hierarchy(db: Session = Depends(get_db)):
    """
    Validate entire hierarchy integrity (RF-TAX-03).
    
    Checks for:
    - Circular references
    - Orphaned skills (invalid parent_id)
    - Maximum depth violations
    
    Returns validation result with warnings and errors.
    """
    return skill_service.validate_hierarchy(db)


@router.get("/{skill_id}", response_model=Skill)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """
    Get skill by ID with full details (RF-TAX-02).
    
    Returns:
    - Basic skill information
    - Hierarchical path
    - Level in hierarchy
    - Children/descendants counts
    """
    skill = skill_service.get_by_id(db, skill_id)
    
    return Skill(
        **skill.__dict__,
        full_path=skill.get_full_path(),
        level=skill.get_level(),
        children_count=len(skill.children),
        descendants_count=len(skill.get_descendants()),
        has_children=len(skill.children) > 0,
        is_root=skill.is_root()
    )


@router.put("/{skill_id}", response_model=Skill)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a skill (RF-TAX-02, RF-TAX-03).
    
    All fields are optional. Validates:
    - Name uniqueness (if changing)
    - Parent existence (if changing)
    - No circular references (if changing parent)
    - Maximum depth (if changing parent)
    
    Can be used to:
    - Rename skill
    - Change description
    - Move to different parent
    - Activate/deactivate
    """
    skill = skill_service.update(db, skill_id, skill_data)
    
    return Skill(
        **skill.__dict__,
        full_path=skill.get_full_path(),
        level=skill.get_level(),
        children_count=len(skill.children),
        descendants_count=len(skill.get_descendants()),
        has_children=len(skill.children) > 0,
        is_root=skill.is_root()
    )


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a skill (RF-TAX-02).
    
    WARNING: This will cascade delete all child skills due to foreign key constraint.
    
    Use with caution for skills with children.
    """
    skill_service.delete(db, skill_id)
    return None
