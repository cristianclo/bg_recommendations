"""Admin service layer for Module H - Administration System."""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..models.admin import AuditLog, TaxonomySnapshot, AuditLogAction, AuditLogEntity
from ..models.game import Game
from ..models.skill import Skill
from ..models.recommendation import Recommendation
from ..schemas.admin import (
    AuditLogCreate,
    AuditLogFilter,
    AuditLogStatistics,
    TaxonomySnapshotCreate,
    TaxonomyExportFormat,
    CatalogStatistics,
    TaxonomyImpactAnalysis,
    AdminDashboard,
)
from ..core.exceptions import NotFoundException, ValidationException


class AdminService:
    """Service for administrative operations (RF-ADM-01, RF-ADM-02)."""
    
    # ==========================================
    # Audit Log Operations
    # ==========================================
    
    @staticmethod
    def create_audit_log(db: Session, audit_data: AuditLogCreate) -> AuditLog:
        """Create audit log entry.
        
        Args:
            db: Database session
            audit_data: Audit log data
            
        Returns:
            Created audit log entry
        """
        audit_log = AuditLog(
            entity_type=audit_data.entity_type,
            entity_id=audit_data.entity_id,
            action=audit_data.action,
            user_id=audit_data.user_id,
            user_role=audit_data.user_role,
            description=audit_data.description,
            changes_summary=audit_data.changes_summary,
            affected_count=audit_data.affected_count,
            ip_address=audit_data.ip_address,
            session_id=audit_data.session_id,
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def list_audit_logs(db: Session, filters: AuditLogFilter) -> tuple[List[AuditLog], int]:
        """List audit logs with filters and pagination.
        
        Args:
            db: Database session
            filters: Filter criteria
            
        Returns:
            Tuple of (logs list, total count)
        """
        query = db.query(AuditLog)
        
        # Apply filters
        if filters.entity_type:
            query = query.filter(AuditLog.entity_type == filters.entity_type)
        if filters.entity_id is not None:
            query = query.filter(AuditLog.entity_id == filters.entity_id)
        if filters.action:
            query = query.filter(AuditLog.action == filters.action)
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        if filters.start_date:
            query = query.filter(AuditLog.timestamp >= filters.start_date)
        if filters.end_date:
            query = query.filter(AuditLog.timestamp <= filters.end_date)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(AuditLog.timestamp)).offset(filters.skip).limit(filters.limit).all()
        
        return logs, total
    
    @staticmethod
    def get_audit_statistics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AuditLogStatistics:
        """Get audit log statistics.
        
        Args:
            db: Database session
            start_date: Start of date range (default: 30 days ago)
            end_date: End of date range (default: now)
            
        Returns:
            Audit log statistics
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        query = db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        )
        
        total_entries = query.count()
        
        # Count by entity type
        entity_counts = db.query(
            AuditLog.entity_type,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        ).group_by(AuditLog.entity_type).all()
        
        total_by_entity = {str(entity): count for entity, count in entity_counts}
        
        # Count by action
        action_counts = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        ).group_by(AuditLog.action).all()
        
        total_by_action = {str(action): count for action, count in action_counts}
        
        # Count by user
        user_counts = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        ).group_by(AuditLog.user_id).all()
        
        total_by_user = {user: count for user, count in user_counts}
        
        # Most active users (top 10)
        most_active = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        ).group_by(AuditLog.user_id).order_by(desc("count")).limit(10).all()
        
        most_active_users = [
            {"user_id": user, "action_count": count}
            for user, count in most_active
        ]
        
        # Recent activity (last 20)
        recent = query.order_by(desc(AuditLog.timestamp)).limit(20).all()
        
        return AuditLogStatistics(
            total_entries=total_entries,
            total_by_entity=total_by_entity,
            total_by_action=total_by_action,
            total_by_user=total_by_user,
            most_active_users=most_active_users,
            recent_activity=recent,
        )
    
    # ==========================================
    # Catalog Management (RF-ADM-01)
    # ==========================================
    
    @staticmethod
    def get_catalog_statistics(db: Session) -> CatalogStatistics:
        """Get comprehensive catalog statistics for RF-ADM-01.
        
        Args:
            db: Database session
            
        Returns:
            Catalog statistics
        """
        # Total games
        total_games = db.query(func.count(Game.id)).scalar()
        
        # Available/unavailable
        available = db.query(func.count(Game.id)).filter(Game.available == True).scalar()
        unavailable = total_games - available
        
        # Games by complexity (grouped)
        complexity_ranges = {
            "1.0-2.0": (1.0, 2.0),
            "2.0-3.0": (2.0, 3.0),
            "3.0-4.0": (3.0, 4.0),
            "4.0-5.0": (4.0, 5.0),
        }
        
        games_by_complexity = {}
        for range_name, (min_val, max_val) in complexity_ranges.items():
            count = db.query(func.count(Game.id)).filter(
                Game.complexity >= min_val,
                Game.complexity < max_val,
            ).scalar()
            games_by_complexity[range_name] = count
        
        # Games by player count (grouped)
        player_ranges = {
            "1-2": (1, 2),
            "3-4": (3, 4),
            "5-6": (5, 6),
            "7+": (7, 100),
        }
        
        games_by_player_count = {}
        for range_name, (min_val, max_val) in player_ranges.items():
            count = db.query(func.count(Game.id)).filter(
                Game.min_players <= max_val,
                Game.max_players >= min_val,
            ).scalar()
            games_by_player_count[range_name] = count
        
        # Recent additions (last 10, if we had created_at field)
        # For now, use last 10 by ID as proxy
        recent = db.query(Game).order_by(desc(Game.id)).limit(10).all()
        recent_additions = [
            {"id": game.id, "name": game.name, "complexity": game.complexity}
            for game in recent
        ]
        
        # Most recommended (top 10)
        most_recommended_query = db.query(
            Game.id,
            Game.name,
            func.count(Recommendation.id).label("rec_count")
        ).join(
            Recommendation, Game.id == Recommendation.game_id
        ).group_by(Game.id, Game.name).order_by(desc("rec_count")).limit(10).all()
        
        most_recommended = [
            {"id": game_id, "name": name, "recommendation_count": count}
            for game_id, name, count in most_recommended_query
        ]
        
        # Least recommended (games with 0 or few recommendations)
        all_game_ids = {game.id for game in db.query(Game.id).all()}
        recommended_game_ids = {
            rec[0] for rec in db.query(Recommendation.game_id).distinct().all()
        }
        never_recommended_ids = all_game_ids - recommended_game_ids
        
        never_recommended = db.query(Game).filter(
            Game.id.in_(list(never_recommended_ids)[:10])
        ).all()
        
        least_recommended = [
            {"id": game.id, "name": game.name, "recommendation_count": 0}
            for game in never_recommended
        ]
        
        return CatalogStatistics(
            total_games=total_games,
            available_games=available,
            unavailable_games=unavailable,
            games_by_complexity=games_by_complexity,
            games_by_player_count=games_by_player_count,
            recent_additions=recent_additions,
            most_recommended=most_recommended,
            least_recommended=least_recommended,
        )
    
    # ==========================================
    # Taxonomy Management (RF-ADM-02)
    # ==========================================
    
    @staticmethod
    def analyze_skill_deletion_impact(db: Session, skill_id: int) -> TaxonomyImpactAnalysis:
        """Analyze impact of deleting a skill (RF-ADM-02).
        
        Args:
            db: Database session
            skill_id: ID of skill to analyze
            
        Returns:
            Impact analysis
            
        Raises:
            NotFoundException: If skill not found
        """
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise NotFoundException("Skill", str(skill_id))
        
        # Check assigned games
        assigned_games_count = len(skill.games)
        assigned_games = [
            {"id": game.id, "name": game.name}
            for game in skill.games
        ]
        
        # Check children
        children_count = db.query(func.count(Skill.id)).filter(
            Skill.parent_id == skill_id
        ).scalar()
        
        has_children = children_count > 0
        
        # Determine if can delete
        can_delete = assigned_games_count == 0 and not has_children
        
        # Generate recommendation
        if can_delete:
            recommendation = f"Safe to delete. Skill '{skill.name}' has no dependencies."
        elif has_children:
            recommendation = (
                f"Cannot delete. Skill has {children_count} child skill(s). "
                f"Reorganize children first."
            )
        else:
            recommendation = (
                f"Cannot delete. Skill is assigned to {assigned_games_count} game(s). "
                f"Remove associations first or reassign games."
            )
        
        return TaxonomyImpactAnalysis(
            skill_id=skill_id,
            skill_name=skill.name,
            can_delete=can_delete,
            assigned_games_count=assigned_games_count,
            assigned_games=assigned_games,
            has_children=has_children,
            children_count=children_count,
            recommendation=recommendation,
        )
    
    @staticmethod
    def create_taxonomy_snapshot(
        db: Session,
        snapshot_data: TaxonomySnapshotCreate,
    ) -> TaxonomySnapshot:
        """Create taxonomy snapshot (RF-ADM-02).
        
        Args:
            db: Database session
            snapshot_data: Snapshot data
            
        Returns:
            Created snapshot
            
        Raises:
            ValidationException: If version already exists
        """
        # Check if version exists
        existing = db.query(TaxonomySnapshot).filter(
            TaxonomySnapshot.version == snapshot_data.version
        ).first()
        
        if existing:
            raise ValidationException(f"Version '{snapshot_data.version}' already exists")
        
        # Create snapshot
        snapshot = TaxonomySnapshot(
            version=snapshot_data.version,
            created_by=snapshot_data.created_by,
            snapshot_data=snapshot_data.snapshot_data,
            description=snapshot_data.description,
            skill_count=snapshot_data.skill_count,
            is_active=0,  # New snapshots are not active by default
        )
        
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        return snapshot
    
    @staticmethod
    def set_active_taxonomy_version(db: Session, version: str) -> TaxonomySnapshot:
        """Set active taxonomy version (RF-ADM-02).
        
        Args:
            db: Database session
            version: Version identifier
            
        Returns:
            Activated snapshot
            
        Raises:
            NotFoundException: If version not found
        """
        snapshot = db.query(TaxonomySnapshot).filter(
            TaxonomySnapshot.version == version
        ).first()
        
        if not snapshot:
            raise NotFoundException("TaxonomySnapshot", version)
        
        # Deactivate all versions
        db.query(TaxonomySnapshot).update({"is_active": 0})
        
        # Activate target version
        snapshot.is_active = 1
        db.commit()
        db.refresh(snapshot)
        
        return snapshot
    
    @staticmethod
    def list_taxonomy_snapshots(db: Session) -> List[TaxonomySnapshot]:
        """List all taxonomy snapshots.
        
        Args:
            db: Database session
            
        Returns:
            List of snapshots, ordered by creation date descending
        """
        return db.query(TaxonomySnapshot).order_by(
            desc(TaxonomySnapshot.created_at)
        ).all()
    
    @staticmethod
    def get_taxonomy_snapshot(db: Session, version: str) -> TaxonomySnapshot:
        """Get specific taxonomy snapshot.
        
        Args:
            db: Database session
            version: Version identifier
            
        Returns:
            Taxonomy snapshot
            
        Raises:
            NotFoundException: If version not found
        """
        snapshot = db.query(TaxonomySnapshot).filter(
            TaxonomySnapshot.version == version
        ).first()
        
        if not snapshot:
            raise NotFoundException("TaxonomySnapshot", version)
        
        return snapshot
    
    @staticmethod
    def export_taxonomy(
        db: Session,
        export_config: TaxonomyExportFormat,
    ) -> Dict[str, Any]:
        """Export taxonomy in specified format (RF-ADM-02).
        
        Args:
            db: Database session
            export_config: Export configuration
            
        Returns:
            Exported taxonomy data
            
        Raises:
            NotFoundException: If specified version not found
            ValidationException: If format not supported
        """
        # Get taxonomy data
        if export_config.version:
            # Export specific version
            snapshot = AdminService.get_taxonomy_snapshot(db, export_config.version)
            taxonomy_data = json.loads(snapshot.snapshot_data)
        else:
            # Export current taxonomy
            skills = db.query(Skill).all()
            
            # Build tree structure
            taxonomy_data = []
            root_skills = [s for s in skills if s.parent_id is None]
            
            def build_tree(skill: Skill) -> Dict[str, Any]:
                node = {
                    "id": skill.id,
                    "name": skill.name,
                }
                
                if export_config.include_descriptions:
                    node["description"] = skill.description
                
                if export_config.include_examples:
                    node["examples"] = skill.examples
                
                children = [s for s in skills if s.parent_id == skill.id]
                if children:
                    node["children"] = [build_tree(child) for child in children]
                
                return node
            
            taxonomy_data = [build_tree(skill) for skill in root_skills]
        
        # Format output
        if export_config.format == "json":
            return {
                "format": "json",
                "version": export_config.version or "current",
                "exported_at": datetime.now().isoformat(),
                "taxonomy": taxonomy_data,
            }
        elif export_config.format == "pdf":
            # PDF export would require additional library (reportlab, weasyprint, etc.)
            # For MVP, return structured data that frontend can convert to PDF
            return {
                "format": "pdf",
                "version": export_config.version or "current",
                "exported_at": datetime.now().isoformat(),
                "taxonomy": taxonomy_data,
                "note": "PDF generation should be handled by frontend or external service",
            }
        else:
            raise ValidationException(f"Unsupported export format: {export_config.format}")
    
    # ==========================================
    # Admin Dashboard
    # ==========================================
    
    @staticmethod
    def get_admin_dashboard(db: Session) -> AdminDashboard:
        """Get comprehensive admin dashboard data.
        
        Args:
            db: Database session
            
        Returns:
            Admin dashboard data
        """
        # Catalog statistics
        catalog_stats = AdminService.get_catalog_statistics(db)
        
        # Recent audit activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_actions = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp >= week_ago
        ).group_by(AuditLog.action).all()
        
        audit_summary = {str(action): count for action, count in recent_actions}
        
        # Taxonomy info
        total_skills = db.query(func.count(Skill.id)).scalar()
        active_snapshot = db.query(TaxonomySnapshot).filter(
            TaxonomySnapshot.is_active == 1
        ).first()
        
        taxonomy_info = {
            "total_skills": total_skills,
            "current_version": active_snapshot.version if active_snapshot else "none",
            "last_snapshot": active_snapshot.created_at.isoformat() if active_snapshot else None,
        }
        
        # System health (basic metrics)
        total_games = catalog_stats.total_games
        total_sessions = db.query(func.count(Recommendation.session_profile_id.distinct())).scalar()
        total_recommendations = db.query(func.count(Recommendation.id)).scalar()
        
        system_health = {
            "total_games": total_games,
            "total_sessions": total_sessions,
            "total_recommendations": total_recommendations,
            "avg_recommendations_per_session": (
                round(total_recommendations / total_sessions, 2) if total_sessions > 0 else 0
            ),
        }
        
        # Recent feedback (last 10)
        recent_feedback_raw = db.query(Recommendation).filter(
            Recommendation.feedback_date.isnot(None)
        ).order_by(desc(Recommendation.feedback_date)).limit(10).all()
        
        recent_feedback = [
            {
                "recommendation_id": rec.id,
                "game_id": rec.game_id,
                "score": rec.user_feedback_score,
                "was_used": rec.was_used,
                "asesor": rec.feedback_asesor,
                "date": rec.feedback_date.isoformat() if rec.feedback_date else None,
            }
            for rec in recent_feedback_raw
        ]
        
        return AdminDashboard(
            catalog_stats=catalog_stats,
            audit_summary=audit_summary,
            taxonomy_info=taxonomy_info,
            system_health=system_health,
            recent_feedback=recent_feedback,
        )
