"""
Skill service implementing business logic and CRUD operations (Module C).
Implements RF-TAX-01, RF-TAX-02, and RF-TAX-03 requirements.
"""
from __future__ import annotations

import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from ..models.skill import Skill
from ..schemas.skill import (
    SkillCreate, SkillUpdate, SkillStatistics,
    HierarchyValidationResult, HierarchyValidationWarning
)
from ..core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class SkillService:
    """
    Service for skill taxonomy management with hierarchical validation.
    Implements RF-TAX-01 (hierarchy), RF-TAX-02 (CRUD), RF-TAX-03 (validation).
    """
    
    MAX_HIERARCHY_DEPTH = 5  # Maximum allowed depth for skill hierarchy
    
    def create(self, db: Session, skill_data: SkillCreate) -> Skill:
        """
        Create a new skill with hierarchy validation (RF-TAX-02).
        
        Args:
            db: Database session
            skill_data: Skill creation data
            
        Returns:
            Created Skill instance
            
        Raises:
            ValidationException: If parent doesn't exist or would create circular reference
        """
        # Validate parent exists if specified
        if skill_data.parent_id is not None:
            parent = self.get_by_id(db, skill_data.parent_id)
            
            # Check max depth
            parent_level = parent.get_level()
            if parent_level >= self.MAX_HIERARCHY_DEPTH - 1:
                raise ValidationException(
                    f"Cannot create child skill: parent is at maximum depth "
                    f"(level {parent_level}, max {self.MAX_HIERARCHY_DEPTH - 1})"
                )
        
        # Check for duplicate name
        existing = db.query(Skill).filter(Skill.name == skill_data.name).first()
        if existing:
            raise ValidationException(f"Skill with name '{skill_data.name}' already exists")
        
        # Create skill
        skill = Skill(**skill_data.model_dump())
        db.add(skill)
        db.commit()
        db.refresh(skill)
        
        logger.info(f"Created skill: {skill.name} (ID: {skill.id}, parent_id: {skill.parent_id})")
        return skill
    
    def get_by_id(self, db: Session, skill_id: int) -> Skill:
        """
        Get skill by ID (RF-TAX-02).
        
        Args:
            db: Database session
            skill_id: Skill ID
            
        Returns:
            Skill instance
            
        Raises:
            NotFoundException: If skill not found
        """
        skill = db.query(Skill).options(
            joinedload(Skill.parent),
            joinedload(Skill.children)
        ).filter(Skill.id == skill_id).first()
        
        if not skill:
            raise NotFoundException("Skill", str(skill_id))
        
        return skill
    
    def get_by_name(self, db: Session, name: str) -> Optional[Skill]:
        """
        Get skill by exact name match.
        
        Args:
            db: Database session
            name: Skill name
            
        Returns:
            Skill instance or None if not found
        """
        return db.query(Skill).filter(Skill.name == name).first()
    
    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        root_only: bool = False,
        parent_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> list[Skill]:
        """
        List skills with filters (RF-TAX-02).
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Filter only active skills
            root_only: Filter only root-level skills (no parent)
            parent_id: Filter by parent ID
            search: Search term for name/description
            
        Returns:
            List of Skill instances
        """
        query = db.query(Skill).options(
            joinedload(Skill.parent),
            joinedload(Skill.children)
        )
        
        if active_only:
            query = query.filter(Skill.is_active == True)
        
        if root_only:
            query = query.filter(Skill.parent_id == None)
        elif parent_id is not None:
            query = query.filter(Skill.parent_id == parent_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Skill.name.ilike(search_term),
                    Skill.description.ilike(search_term)
                )
            )
        
        query = query.order_by(Skill.name)
        return query.offset(skip).limit(limit).all()
    
    def update(self, db: Session, skill_id: int, skill_data: SkillUpdate) -> Skill:
        """
        Update a skill with hierarchy validation (RF-TAX-02, RF-TAX-03).
        
        Args:
            db: Database session
            skill_id: Skill ID to update
            skill_data: Update data
            
        Returns:
            Updated Skill instance
            
        Raises:
            NotFoundException: If skill not found
            ValidationException: If update would create circular reference or duplicate name
        """
        skill = self.get_by_id(db, skill_id)
        update_data = skill_data.model_dump(exclude_unset=True)
        
        # Validate name uniqueness if changing
        if 'name' in update_data and update_data['name'] != skill.name:
            existing = db.query(Skill).filter(
                Skill.name == update_data['name'],
                Skill.id != skill_id
            ).first()
            if existing:
                raise ValidationException(f"Skill with name '{update_data['name']}' already exists")
        
        # Validate parent_id change
        if 'parent_id' in update_data:
            new_parent_id = update_data['parent_id']
            
            # Cannot set self as parent
            if new_parent_id == skill_id:
                raise ValidationException("Skill cannot be its own parent")
            
            # Check if new parent exists
            if new_parent_id is not None:
                new_parent = self.get_by_id(db, new_parent_id)
                
                # Check for circular reference (RF-TAX-03)
                if not skill.can_have_parent(new_parent_id):
                    raise ValidationException(
                        f"Cannot set parent: would create circular reference. "
                        f"Skill {new_parent_id} is a descendant of skill {skill_id}"
                    )
                
                # Check max depth
                new_parent_level = new_parent.get_level()
                if new_parent_level >= self.MAX_HIERARCHY_DEPTH - 1:
                    raise ValidationException(
                        f"Cannot move skill: new parent is at maximum depth "
                        f"(level {new_parent_level}, max {self.MAX_HIERARCHY_DEPTH - 1})"
                    )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(skill, field, value)
        
        db.commit()
        db.refresh(skill)
        
        logger.info(f"Updated skill: {skill.name} (ID: {skill.id})")
        return skill
    
    def delete(self, db: Session, skill_id: int) -> bool:
        """
        Delete a skill (RF-TAX-02).
        Children will be cascade deleted due to foreign key constraint.
        
        Args:
            db: Database session
            skill_id: Skill ID to delete
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundException: If skill not found
        """
        skill = self.get_by_id(db, skill_id)
        
        # Log if has children (they will be cascade deleted)
        children_count = len(skill.children)
        if children_count > 0:
            logger.warning(
                f"Deleting skill '{skill.name}' (ID: {skill_id}) will cascade delete "
                f"{children_count} child skill(s)"
            )
        
        db.delete(skill)
        db.commit()
        
        logger.info(f"Deleted skill: {skill.name} (ID: {skill_id})")
        return True
    
    def get_tree(self, db: Session, root_id: Optional[int] = None, active_only: bool = False) -> List[Skill]:
        """
        Get hierarchical tree of skills (RF-TAX-01).
        
        Args:
            db: Database session
            root_id: Start from specific root (None for all roots)
            active_only: Include only active skills
            
        Returns:
            List of root skills with loaded children recursively
        """
        query = db.query(Skill).options(
            joinedload(Skill.children)
        )
        
        if active_only:
            query = query.filter(Skill.is_active == True)
        
        if root_id is not None:
            query = query.filter(Skill.id == root_id)
        else:
            query = query.filter(Skill.parent_id == None)
        
        roots = query.order_by(Skill.name).all()
        
        # Recursively load children
        def load_children(skill: Skill):
            if skill.children:
                for child in skill.children:
                    if active_only and not child.is_active:
                        continue
                    load_children(child)
        
        for root in roots:
            load_children(root)
        
        return roots
    
    def get_statistics(self, db: Session) -> SkillStatistics:
        """
        Get taxonomy statistics (RF-TAX-01).
        
        Args:
            db: Database session
            
        Returns:
            SkillStatistics with taxonomy metrics
        """
        total_skills = db.query(func.count(Skill.id)).scalar()
        active_skills = db.query(func.count(Skill.id)).filter(Skill.is_active == True).scalar()
        inactive_skills = total_skills - active_skills
        root_skills = db.query(func.count(Skill.id)).filter(Skill.parent_id == None).scalar()
        
        # Calculate max depth
        all_skills = db.query(Skill).options(joinedload(Skill.parent)).all()
        max_depth = 0
        for skill in all_skills:
            try:
                level = skill.get_level()
                max_depth = max(max_depth, level)
            except ValueError:
                # Skip skills with circular references
                continue
        
        # Calculate average children per parent
        parents = db.query(Skill).filter(Skill.children.any()).all()
        if parents:
            avg_children = sum(len(p.children) for p in parents) / len(parents)
        else:
            avg_children = 0.0
        
        # Count leaf skills (no children)
        leaf_skills = db.query(func.count(Skill.id)).filter(~Skill.children.any()).scalar()
        
        return SkillStatistics(
            total_skills=total_skills,
            active_skills=active_skills,
            inactive_skills=inactive_skills,
            root_skills=root_skills,
            max_depth=max_depth,
            avg_children_per_parent=round(avg_children, 2),
            leaf_skills=leaf_skills
        )
    
    def validate_hierarchy(self, db: Session) -> HierarchyValidationResult:
        """
        Validate entire hierarchy integrity (RF-TAX-03).
        Checks for circular references, orphaned skills, max depth violations.
        
        Args:
            db: Database session
            
        Returns:
            HierarchyValidationResult with any issues found
        """
        all_skills = db.query(Skill).options(joinedload(Skill.parent)).all()
        warnings: List[HierarchyValidationWarning] = []
        errors: List[HierarchyValidationWarning] = []
        
        for skill in all_skills:
            # Check for circular references
            try:
                level = skill.get_level()
                
                # Check max depth
                if level > self.MAX_HIERARCHY_DEPTH:
                    warnings.append(HierarchyValidationWarning(
                        skill_id=skill.id,
                        skill_name=skill.name,
                        issue_type='max_depth_exceeded',
                        message=f"Skill exceeds maximum depth (level {level}, max {self.MAX_HIERARCHY_DEPTH})",
                        severity='medium'
                    ))
            except ValueError as e:
                errors.append(HierarchyValidationWarning(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    issue_type='circular_reference',
                    message=str(e),
                    severity='critical'
                ))
            
            # Check for orphaned parents (parent_id points to non-existent skill)
            if skill.parent_id is not None and skill.parent is None:
                errors.append(HierarchyValidationWarning(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    issue_type='orphaned',
                    message=f"Parent ID {skill.parent_id} does not exist",
                    severity='high'
                ))
        
        is_valid = len(errors) == 0
        
        return HierarchyValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            total_skills_checked=len(all_skills)
        )    
    def associate_game(
        self,
        db: Session,
        skill_id: int,
        game_id: int,
        justification: Optional[str] = None
    ) -> bool:
        """
        Associate a skill with a game (RF-TAX-03).
        
        Args:
            db: Database session
            skill_id: Skill ID
            game_id: Game ID
            justification: Pedagogical justification for the association
            
        Returns:
            True if association was created
            
        Raises:
            NotFoundException: If skill or game not found
            ValidationException: If association already exists
        """
        from ..models.game import Game
        from ..models.skill import game_skills
        from sqlalchemy import insert
        
        # Verify skill exists
        skill = self.get_by_id(db, skill_id)
        
        # Verify game exists
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise NotFoundException("Game", str(game_id))
        
        # Check if association already exists
        existing = db.execute(
            game_skills.select().where(
                (game_skills.c.game_id == game_id) & 
                (game_skills.c.skill_id == skill_id)
            )
        ).first()
        
        if existing:
            raise ValidationException(f"Skill '{skill.name}' is already associated with game '{game.name}'")
        
        # Create association with justification
        stmt = insert(game_skills).values(
            game_id=game_id,
            skill_id=skill_id,
            justification=justification
        )
        db.execute(stmt)
        db.commit()
        
        logger.info(f"Associated skill '{skill.name}' (ID: {skill_id}) with game '{game.name}' (ID: {game_id})")
        return True
    
    def dissociate_game(
        self,
        db: Session,
        skill_id: int,
        game_id: int
    ) -> bool:
        """
        Remove association between a skill and a game (RF-TAX-03).
        
        Args:
            db: Database session
            skill_id: Skill ID
            game_id: Game ID
            
        Returns:
            True if association was removed
            
        Raises:
            NotFoundException: If skill or game not found, or association doesn't exist
        """
        from ..models.game import Game
        from ..models.skill import game_skills
        from sqlalchemy import delete
        
        # Verify skill exists
        skill = self.get_by_id(db, skill_id)
        
        # Verify game exists
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise NotFoundException("Game", str(game_id))
        
        # Check if association exists
        existing = db.execute(
            game_skills.select().where(
                (game_skills.c.game_id == game_id) & 
                (game_skills.c.skill_id == skill_id)
            )
        ).first()
        
        if not existing:
            raise NotFoundException(
                "Association",
                f"between skill '{skill.name}' and game '{game.name}'"
            )
        
        # Remove association
        stmt = delete(game_skills).where(
            (game_skills.c.game_id == game_id) & 
            (game_skills.c.skill_id == skill_id)
        )
        db.execute(stmt)
        db.commit()
        
        logger.info(f"Dissociated skill '{skill.name}' (ID: {skill_id}) from game '{game.name}' (ID: {game_id})")
        return True
    
    def get_skill_games(
        self,
        db: Session,
        skill_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """
        Get all games associated with a skill (RF-TAX-03).
        
        Args:
            db: Database session
            skill_id: Skill ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Game instances
            
        Raises:
            NotFoundException: If skill not found
        """
        from ..models.game import Game
        
        skill = self.get_by_id(db, skill_id)
        
        return skill.games.offset(skip).limit(limit).all()