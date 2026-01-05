"""
Pydantic schemas for SessionProfile API requests and responses (Module B).
Implements validation for RF-CTX-01 requirements.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

from ..models.session import Modality
from ..models.game import LanguageDependency


class ValidationWarning(BaseModel):
    """
    Validation warning for operational coherence (RF-CTX-02).
    """
    code: str = Field(..., description="Warning code (e.g., LARGE_GROUP)")
    message: str = Field(..., description="Human-readable warning message")
    severity: str = Field("warning", description="Severity: warning, info, critical")
    suggestions: list[str] = Field(default_factory=list, description="Actionable suggestions")
    
    model_config = ConfigDict(from_attributes=True)


class SessionProfileBase(BaseModel):
    """Base schema with common session profile attributes."""
    
    session_name: Optional[str] = Field(None, max_length=255, description="Optional session name")
    objectives: list[str] = Field(
        ...,
        min_length=1,
        description="Class objectives (at least 1 required)"
    )
    primary_skill_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Primary skill to work on (required)"
    )
    secondary_skill_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Secondary skill to work on (optional)"
    )
    available_time_min: int = Field(
        ...,
        ge=15,
        le=240,
        description="Available time in minutes (15-240)"
    )
    group_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Group size (1-100)"
    )
    max_language_dependency: LanguageDependency = Field(
        LanguageDependency.MEDIA,
        description="Maximum acceptable language dependency"
    )
    preferred_modality: Modality = Field(
        Modality.ANY,
        description="Preferred game modality"
    )
    additional_constraints: Optional[dict] = Field(
        None,
        description="Additional constraints as key-value pairs"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Free text notes"
    )
    created_by_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Name of person creating session (temporary)"
    )
    
    @field_validator('objectives')
    @classmethod
    def validate_objectives_not_empty(cls, v):
        """Ensure objectives list is not empty and items are not blank."""
        if not v:
            raise ValueError('At least one objective is required')
        
        # Remove empty strings and validate
        non_empty = [obj.strip() for obj in v if obj.strip()]
        if not non_empty:
            raise ValueError('At least one non-empty objective is required')
        
        return non_empty
    
    @field_validator('primary_skill_name')
    @classmethod
    def validate_primary_skill_not_empty(cls, v):
        """Ensure primary skill is not blank."""
        if not v or not v.strip():
            raise ValueError('Primary skill is required and cannot be empty')
        return v.strip()
    
    @field_validator('secondary_skill_name')
    @classmethod
    def validate_secondary_skill(cls, v):
        """Clean up secondary skill if provided."""
        if v:
            return v.strip() if v.strip() else None
        return None


class SessionProfileCreate(SessionProfileBase):
    """Schema for creating a new session profile."""
    pass


class SessionProfileUpdate(BaseModel):
    """Schema for updating an existing session profile. All fields are optional."""
    
    session_name: Optional[str] = Field(None, max_length=255)
    objectives: Optional[list[str]] = Field(None, min_length=1)
    primary_skill_name: Optional[str] = Field(None, min_length=1, max_length=255)
    secondary_skill_name: Optional[str] = Field(None, max_length=255)
    available_time_min: Optional[int] = Field(None, ge=15, le=240)
    group_size: Optional[int] = Field(None, ge=1, le=100)
    max_language_dependency: Optional[LanguageDependency] = None
    preferred_modality: Optional[Modality] = None
    additional_constraints: Optional[dict] = None
    notes: Optional[str] = Field(None, max_length=2000)
    
    model_config = ConfigDict(extra='forbid')


class SessionProfile(SessionProfileBase):
    """Schema for session profile responses (includes database fields)."""
    
    id: int = Field(..., description="Database ID")
    validation_warnings: list[ValidationWarning] = Field(
        default_factory=list,
        description="Validation warnings from coherence check (RF-CTX-02)"
    )
    has_warnings: bool = Field(False, description="Quick flag for warnings presence")
    has_recommendations: bool = Field(False, description="Has generated recommendations")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('validation_warnings', mode='before')
    @classmethod
    def parse_warnings(cls, v):
        """Parse warnings from JSON if needed."""
        if not v:
            return []
        
        # If already list of ValidationWarning objects, return as is
        if isinstance(v, list) and all(isinstance(w, ValidationWarning) for w in v):
            return v
        
        # If list of dicts, convert to ValidationWarning objects
        if isinstance(v, list) and v:
            if isinstance(v[0], dict):
                return [ValidationWarning(**w) for w in v]
        
        return v


class SessionProfileList(BaseModel):
    """Paginated list of session profiles."""
    
    items: list[SessionProfile]
    total: int = Field(..., description="Total number of session profiles")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(from_attributes=True)


class SessionProfileSummary(BaseModel):
    """
    Summary of a session profile for lists/quick views.
    Lighter weight than full SessionProfile.
    """
    id: int
    session_name: Optional[str]
    objectives: list[str]
    primary_skill_name: str
    group_size: int
    available_time_min: int
    has_warnings: bool
    warning_count: int = 0
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
