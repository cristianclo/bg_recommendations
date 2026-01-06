"""Admin schemas for Module H - Administration System."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


# ===========================
# Audit Log Schemas
# ===========================

class AuditLogBase(BaseModel):
    """Base schema for audit logs."""
    
    entity_type: str = Field(..., description="Type of entity (game, skill, session, etc.)")
    entity_id: Optional[int] = Field(None, description="ID of affected entity (NULL for bulk ops)")
    action: str = Field(..., description="Action performed (create, update, delete, etc.)")
    user_id: str = Field(..., description="ID or name of user who performed action")
    user_role: Optional[str] = Field(None, description="Role of user (admin, asesor)")
    description: Optional[str] = Field(None, description="Human-readable description")
    changes_summary: Optional[str] = Field(None, description="JSON snapshot of changes")
    affected_count: int = Field(1, ge=1, description="Number of records affected")
    ip_address: Optional[str] = Field(None, description="IP address of user")
    session_id: Optional[str] = Field(None, description="User session ID")


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log entries."""
    pass


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""
    
    id: int
    timestamp: datetime
    
    model_config = {"from_attributes": True}


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    action: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)


class AuditLogStatistics(BaseModel):
    """Statistics for audit logs."""
    
    total_entries: int
    total_by_entity: Dict[str, int]
    total_by_action: Dict[str, int]
    total_by_user: Dict[str, int]
    most_active_users: List[Dict[str, Any]]
    recent_activity: List[AuditLogResponse]


# ===========================
# Taxonomy Snapshot Schemas
# ===========================

class TaxonomySnapshotBase(BaseModel):
    """Base schema for taxonomy snapshots."""
    
    version: str = Field(..., description="Version identifier (e.g., v1.0, v1.1)")
    description: Optional[str] = Field(None, description="Description of changes")
    created_by: str = Field(..., description="User who created snapshot")


class TaxonomySnapshotCreate(TaxonomySnapshotBase):
    """Schema for creating taxonomy snapshots."""
    
    snapshot_data: str = Field(..., description="JSON-serialized taxonomy tree")
    skill_count: int = Field(..., ge=0, description="Total skills in snapshot")


class TaxonomySnapshotResponse(TaxonomySnapshotBase):
    """Schema for taxonomy snapshot responses."""
    
    id: int
    created_at: datetime
    skill_count: int
    is_active: bool
    
    model_config = {"from_attributes": True}


class TaxonomySnapshotDetail(TaxonomySnapshotResponse):
    """Detailed schema including snapshot data."""
    
    snapshot_data: str


class TaxonomyExportFormat(BaseModel):
    """Schema for taxonomy export configuration."""
    
    format: str = Field("json", description="Export format: json or pdf")
    include_descriptions: bool = Field(True, description="Include skill descriptions")
    include_examples: bool = Field(True, description="Include examples")
    version: Optional[str] = Field(None, description="Specific version to export (default: current)")


# ===========================
# Catalog Management Schemas
# ===========================

class CatalogStatistics(BaseModel):
    """Statistics for game catalog."""
    
    total_games: int
    available_games: int
    unavailable_games: int
    games_by_complexity: Dict[str, int]  # e.g., {"1-2": 10, "3-4": 25, "5": 5}
    games_by_player_count: Dict[str, int]  # e.g., {"1-2": 15, "3-4": 30}
    recent_additions: List[Dict[str, Any]]
    most_recommended: List[Dict[str, Any]]
    least_recommended: List[Dict[str, Any]]


class TaxonomyImpactAnalysis(BaseModel):
    """Analysis of impact before deleting a skill."""
    
    skill_id: int
    skill_name: str
    can_delete: bool
    assigned_games_count: int
    assigned_games: List[Dict[str, Any]]  # Game ID, name, association count
    has_children: bool
    children_count: int
    recommendation: str


class BulkOperationResult(BaseModel):
    """Result of bulk operations."""
    
    success: bool
    operation: str
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    summary: str


# ===========================
# Admin Dashboard Schemas
# ===========================

class AdminDashboard(BaseModel):
    """Comprehensive admin dashboard data."""
    
    catalog_stats: CatalogStatistics
    audit_summary: Dict[str, int]  # Recent activity counts by action
    taxonomy_info: Dict[str, Any]  # Current version, skill count, last update
    system_health: Dict[str, Any]  # DB size, response times, error rates
    recent_feedback: List[Dict[str, Any]]  # Latest feedback summary
