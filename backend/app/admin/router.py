"""Admin router for Module H - Administration System."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.admin import (
    AuditLogCreate,
    AuditLogResponse,
    AuditLogFilter,
    AuditLogStatistics,
    TaxonomySnapshotCreate,
    TaxonomySnapshotResponse,
    TaxonomySnapshotDetail,
    TaxonomyExportFormat,
    CatalogStatistics,
    TaxonomyImpactAnalysis,
    AdminDashboard,
)
from ..admin.service import AdminService


router = APIRouter(prefix="/admin", tags=["admin"])


# ==========================================
# Audit Log Endpoints
# ==========================================

@router.post("/audit-logs", response_model=AuditLogResponse, status_code=201)
def create_audit_log(
    audit_data: AuditLogCreate,
    db: Session = Depends(get_db),
):
    """Create audit log entry.
    
    **RF-ADM-01, RF-ADM-02:** Tracks all administrative actions.
    """
    audit_log = AdminService.create_audit_log(db, audit_data)
    return audit_log


@router.get("/audit-logs", response_model=dict)
def list_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """List audit logs with filters and pagination.
    
    **RF-ADM-01, RF-ADM-02:** View audit trail.
    """
    filters = AuditLogFilter(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    
    logs, total = AdminService.list_audit_logs(db, filters)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": logs,
    }


@router.get("/audit-logs/statistics", response_model=AuditLogStatistics)
def get_audit_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description="End date (default: now)"),
    db: Session = Depends(get_db),
):
    """Get audit log statistics.
    
    **RF-ADM-01, RF-ADM-02:** Analyze administrative activity patterns.
    """
    return AdminService.get_audit_statistics(db, start_date, end_date)


# ==========================================
# Catalog Management Endpoints (RF-ADM-01)
# ==========================================

@router.get("/catalog/statistics", response_model=CatalogStatistics)
def get_catalog_statistics(db: Session = Depends(get_db)):
    """Get comprehensive catalog statistics.
    
    **RF-ADM-01:** Provides overview of game catalog for administrative dashboard.
    
    Returns statistics including:
    - Total games (available/unavailable)
    - Distribution by complexity and player count
    - Recent additions
    - Most/least recommended games
    """
    return AdminService.get_catalog_statistics(db)


# ==========================================
# Taxonomy Management Endpoints (RF-ADM-02)
# ==========================================

@router.get("/taxonomy/impact/{skill_id}", response_model=TaxonomyImpactAnalysis)
def analyze_skill_deletion_impact(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """Analyze impact of deleting a skill.
    
    **RF-ADM-02:** Checks dependencies before skill deletion.
    
    Returns analysis including:
    - Assigned games count and list
    - Child skills count
    - Whether deletion is safe
    - Recommendations for action
    """
    return AdminService.analyze_skill_deletion_impact(db, skill_id)


@router.post("/taxonomy/snapshots", response_model=TaxonomySnapshotResponse, status_code=201)
def create_taxonomy_snapshot(
    snapshot_data: TaxonomySnapshotCreate,
    db: Session = Depends(get_db),
):
    """Create taxonomy version snapshot.
    
    **RF-ADM-02:** Creates versioned snapshot of complete taxonomy.
    
    Use this before making significant taxonomy changes to preserve history.
    """
    return AdminService.create_taxonomy_snapshot(db, snapshot_data)


@router.get("/taxonomy/snapshots", response_model=List[TaxonomySnapshotResponse])
def list_taxonomy_snapshots(db: Session = Depends(get_db)):
    """List all taxonomy snapshots.
    
    **RF-ADM-02:** View taxonomy version history.
    """
    return AdminService.list_taxonomy_snapshots(db)


@router.get("/taxonomy/snapshots/{version}", response_model=TaxonomySnapshotDetail)
def get_taxonomy_snapshot(
    version: str,
    db: Session = Depends(get_db),
):
    """Get specific taxonomy snapshot with full data.
    
    **RF-ADM-02:** Retrieve complete taxonomy state for a version.
    """
    return AdminService.get_taxonomy_snapshot(db, version)


@router.post("/taxonomy/snapshots/{version}/activate", response_model=TaxonomySnapshotResponse)
def set_active_taxonomy_version(
    version: str,
    db: Session = Depends(get_db),
):
    """Set active taxonomy version.
    
    **RF-ADM-02:** Mark a specific version as the current active taxonomy.
    """
    return AdminService.set_active_taxonomy_version(db, version)


@router.post("/taxonomy/export", response_model=dict)
def export_taxonomy(
    export_config: TaxonomyExportFormat,
    db: Session = Depends(get_db),
):
    """Export taxonomy in specified format.
    
    **RF-ADM-02:** Export complete taxonomy to JSON or PDF.
    
    Supports:
    - JSON format (ready for import)
    - PDF format (for documentation)
    - Include/exclude descriptions and examples
    - Export specific version or current state
    """
    return AdminService.export_taxonomy(db, export_config)


# ==========================================
# Admin Dashboard
# ==========================================

@router.get("/dashboard", response_model=AdminDashboard)
def get_admin_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive admin dashboard data.
    
    **RF-ADM-01, RF-ADM-02:** Provides complete system overview.
    
    Includes:
    - Catalog statistics
    - Recent audit activity
    - Taxonomy information
    - System health metrics
    - Recent feedback summary
    """
    return AdminService.get_admin_dashboard(db)
