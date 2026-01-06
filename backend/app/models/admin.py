"""Admin models for Module H - Administration System."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class AuditLogAction(str, enum.Enum):
    """Enum for audit log action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BULK_IMPORT = "bulk_import"
    EXPORT = "export"
    REORGANIZE = "reorganize"


class AuditLogEntity(str, enum.Enum):
    """Enum for audited entity types."""
    GAME = "game"
    SKILL = "skill"
    SESSION = "session"
    RECOMMENDATION = "recommendation"
    SCORING_CONFIG = "scoring_config"
    TAXONOMY = "taxonomy"


class AuditLog(Base):
    """Audit log for administrative actions (RF-ADM-01, RF-ADM-02).
    
    Tracks all CRUD operations on critical entities with who/what/when details.
    """
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # What was changed
    entity_type = Column(SQLEnum(AuditLogEntity), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)  # NULL for bulk operations
    action = Column(SQLEnum(AuditLogAction), nullable=False, index=True)
    
    # Who made the change
    user_id = Column(String(100), nullable=False, index=True)  # Asesor name or admin ID
    user_role = Column(String(50), nullable=True)  # "admin", "asesor", etc.
    
    # When
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Details
    description = Column(Text, nullable=True)  # Human-readable description
    changes_summary = Column(Text, nullable=True)  # JSON-serialized before/after snapshot
    affected_count = Column(Integer, default=1, nullable=False)  # Number of records affected
    
    # Context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    session_id = Column(String(100), nullable=True)  # For tracking user sessions
    
    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, entity={self.entity_type.value}, "
            f"action={self.action.value}, user={self.user_id}, "
            f"timestamp={self.timestamp.isoformat()})>"
        )


class TaxonomySnapshot(Base):
    """Taxonomy version snapshots for RF-ADM-02.
    
    Stores complete taxonomy state at significant change points.
    """
    
    __tablename__ = "taxonomy_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Versioning
    version = Column(String(50), nullable=False, unique=True, index=True)  # e.g., "v1.0", "v1.1"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    
    # Snapshot data
    snapshot_data = Column(Text, nullable=False)  # JSON-serialized complete taxonomy tree
    description = Column(Text, nullable=True)  # Change description
    
    # Metadata
    skill_count = Column(Integer, nullable=False)  # Total skills in this version
    is_active = Column(Integer, default=0, nullable=False)  # Boolean flag for current version
    
    def __repr__(self):
        return (
            f"<TaxonomySnapshot(id={self.id}, version={self.version}, "
            f"created_at={self.created_at.isoformat()}, skills={self.skill_count})>"
        )
