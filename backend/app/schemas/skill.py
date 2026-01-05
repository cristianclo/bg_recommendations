"""
Pydantic schemas for Skill model (Module C).
Implements validation for RF-TAX-01, RF-TAX-02, RF-TAX-03.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SkillBase(BaseModel):
    """Base schema for Skill with common attributes."""
    name: str = Field(..., min_length=1, max_length=255, description="Skill name (unique)")
    description: Optional[str] = Field(None, description="Detailed description of the skill")
    parent_id: Optional[int] = Field(None, description="ID of parent skill for hierarchy")
    is_active: bool = Field(True, description="Whether the skill is active/visible")
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that name is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Skill name cannot be empty or whitespace')
        return v.strip()


class SkillCreate(SkillBase):
    """Schema for creating a new skill."""
    pass


class SkillUpdate(BaseModel):
    """Schema for updating an existing skill. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that name is not just whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Skill name cannot be empty or whitespace')
        return v.strip() if v else None


class SkillSimple(BaseModel):
    """Simplified skill representation (without relationships)."""
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SkillWithPath(SkillSimple):
    """Skill with full hierarchical path."""
    full_path: str
    level: int
    
    model_config = {"from_attributes": True}


class SkillWithChildren(SkillSimple):
    """Skill with its immediate children."""
    children: List['SkillSimple'] = []
    
    model_config = {"from_attributes": True}


class SkillTreeNode(SkillSimple):
    """Skill node for complete tree representation (recursive)."""
    children: List['SkillTreeNode'] = []
    
    model_config = {"from_attributes": True}


class Skill(SkillWithPath):
    """
    Complete skill response with metadata.
    Includes full path and hierarchy level.
    """
    children_count: int = Field(0, description="Number of direct children")
    descendants_count: int = Field(0, description="Total number of descendants")
    has_children: bool = Field(False, description="Whether skill has children")
    is_root: bool = Field(False, description="Whether skill is at root level")
    
    model_config = {"from_attributes": True}


class SkillStatistics(BaseModel):
    """Statistics about the skills taxonomy."""
    total_skills: int
    active_skills: int
    inactive_skills: int
    root_skills: int
    max_depth: int
    avg_children_per_parent: float
    leaf_skills: int  # Skills without children


class HierarchyValidationWarning(BaseModel):
    """Warning message for hierarchy validation issues."""
    skill_id: int
    skill_name: str
    issue_type: str  # 'circular_reference', 'orphaned', 'max_depth_exceeded', etc.
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class HierarchyValidationResult(BaseModel):
    """Result of hierarchy integrity validation."""
    is_valid: bool
    warnings: List[HierarchyValidationWarning] = []
    errors: List[HierarchyValidationWarning] = []
    total_skills_checked: int
    
    def has_issues(self) -> bool:
        """Check if there are any warnings or errors."""
        return len(self.warnings) > 0 or len(self.errors) > 0
