"""
Skill model for hierarchical skills taxonomy (Module C).
Implements RF-TAX-01 (hierarchical taxonomy) and RF-TAX-03 (game associations).
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Table, func
from sqlalchemy.orm import relationship
from ..core.database import Base


# Association table for many-to-many relationship between skills and games
game_skills = Table(
    'game_skills',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
    Column('justification', Text, nullable=True),  # Pedagogical justification
    Column('created_at', DateTime, server_default=func.now(), nullable=False)
)


class Skill(Base):
    """
    Skill model with hierarchical parent-child relationships.
    
    Attributes:
        id: Primary key
        name: Skill name (unique)
        description: Detailed description of the skill
        parent_id: Foreign key to parent skill (NULL for root skills)
        is_active: Whether the skill is currently active/visible
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        
    Relationships:
        parent: Parent skill (self-referential)
        children: Child skills (self-referential)
    """
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False, server_default="true")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Self-referential relationship for hierarchy
    parent = relationship(
        "Skill",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id]
    )
    children = relationship(
        "Skill",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    
    # Many-to-many relationship with games (RF-TAX-03)
    games = relationship(
        "Game",
        secondary=game_skills,
        back_populates="skills",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
    
    def is_root(self) -> bool:
        """Check if this is a root-level skill (no parent)."""
        return self.parent_id is None
    
    def get_level(self) -> int:
        """
        Get the depth level of this skill in the hierarchy.
        Root skills are level 0.
        """
        if self.is_root():
            return 0
        level = 0
        current = self
        # Use a set to detect cycles and prevent infinite loops
        visited = {self.id}
        while current.parent_id is not None:
            if current.parent_id in visited:
                raise ValueError(f"Circular reference detected in skill hierarchy for skill {self.id}")
            visited.add(current.parent_id)
            level += 1
            current = current.parent
            if current is None:
                break
        return level
    
    def get_ancestors(self) -> list['Skill']:
        """
        Get all ancestor skills from immediate parent to root.
        Returns empty list for root skills.
        """
        ancestors = []
        current = self.parent
        visited = {self.id}
        while current is not None:
            if current.id in visited:
                raise ValueError(f"Circular reference detected in skill hierarchy for skill {self.id}")
            visited.add(current.id)
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self) -> list['Skill']:
        """
        Get all descendant skills (children, grandchildren, etc.).
        Returns empty list for leaf skills.
        """
        descendants = []
        visited = {self.id}
        
        def collect_descendants(skill):
            for child in skill.children:
                if child.id in visited:
                    raise ValueError(f"Circular reference detected in skill hierarchy")
                visited.add(child.id)
                descendants.append(child)
                collect_descendants(child)
        
        collect_descendants(self)
        return descendants
    
    def get_full_path(self) -> str:
        """
        Get the full hierarchical path of this skill.
        Example: "Root > Parent > Child"
        """
        ancestors = self.get_ancestors()
        if not ancestors:
            return self.name
        # Reverse to go from root to current
        path_parts = [a.name for a in reversed(ancestors)]
        path_parts.append(self.name)
        return " > ".join(path_parts)
    
    def can_have_parent(self, potential_parent_id: int) -> bool:
        """
        Check if a skill can be assigned as parent (no circular references).
        Returns False if setting this parent would create a cycle.
        """
        if potential_parent_id == self.id:
            return False
        
        # Check if potential parent is already a descendant
        descendant_ids = {d.id for d in self.get_descendants()}
        return potential_parent_id not in descendant_ids
