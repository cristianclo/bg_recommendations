"""
Service for managing scoring configurations.
Implements RF-REC-02 requirement (configurable weights).
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

from ..models.recommendation import ScoringConfig
from ..schemas.recommendation import ScoringConfigCreate, ScoringConfigUpdate
from ..core.exceptions import NotFoundException, ValidationException


class ScoringConfigService:
    """Service for CRUD operations on scoring configurations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, config_create: ScoringConfigCreate) -> ScoringConfig:
        """
        Create a new scoring configuration.
        
        Args:
            config_create: Configuration data
        
        Returns:
            Created ScoringConfig
        
        Raises:
            ValidationException: If weights don't sum to 1.0 or name exists
        """
        # Validate weights sum
        weights_sum = (
            config_create.skill_weight +
            config_create.mechanics_weight +
            config_create.difficulty_weight +
            config_create.ranking_weight
        )
        
        if not (0.99 <= weights_sum <= 1.01):
            raise ValidationException(
                f"Weights must sum to 1.0 (got {weights_sum:.4f})"
            )
        
        # Check for duplicate name
        existing = self.db.query(ScoringConfig).filter(
            ScoringConfig.name == config_create.name
        ).first()
        
        if existing:
            raise ValidationException(
                f"Configuration with name '{config_create.name}' already exists"
            )
        
        # If setting as active, deactivate others
        if config_create.is_active:
            self._deactivate_all()
        
        # If setting as default, remove default from others
        if config_create.is_default:
            self._remove_default_flag()
        
        # Create configuration
        config = ScoringConfig(**config_create.model_dump())
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def get_by_id(self, config_id: int) -> Optional[ScoringConfig]:
        """Get configuration by ID."""
        return self.db.query(ScoringConfig).filter(
            ScoringConfig.id == config_id
        ).first()
    
    def get_active(self) -> Optional[ScoringConfig]:
        """Get currently active configuration."""
        return self.db.query(ScoringConfig).filter(
            ScoringConfig.is_active == True
        ).first()
    
    def get_default(self) -> Optional[ScoringConfig]:
        """Get default configuration."""
        return self.db.query(ScoringConfig).filter(
            ScoringConfig.is_default == True
        ).first()
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[ScoringConfig]:
        """
        List scoring configurations.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only return active configuration
        
        Returns:
            List of ScoringConfig
        """
        query = self.db.query(ScoringConfig)
        
        if active_only:
            query = query.filter(ScoringConfig.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def update(
        self,
        config_id: int,
        config_update: ScoringConfigUpdate
    ) -> ScoringConfig:
        """
        Update scoring configuration.
        
        Args:
            config_id: Configuration ID
            config_update: Updated data
        
        Returns:
            Updated ScoringConfig
        
        Raises:
            NotFoundException: If configuration not found
            ValidationException: If weights don't sum to 1.0
        """
        config = self.get_by_id(config_id)
        if not config:
            raise NotFoundException("ScoringConfig", str(config_id))
        
        # Track if weights are being updated
        weight_fields = ['skill_weight', 'mechanics_weight', 'difficulty_weight', 'ranking_weight']
        weights_changed = any(
            getattr(config_update, field) is not None
            for field in weight_fields
        )
        
        # Update fields
        update_data = config_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        # Validate weights if any changed
        if weights_changed:
            weights_sum = (
                config.skill_weight +
                config.mechanics_weight +
                config.difficulty_weight +
                config.ranking_weight
            )
            
            if not (0.99 <= weights_sum <= 1.01):
                raise ValidationException(
                    f"Updated weights must sum to 1.0 (got {weights_sum:.4f})"
                )
        
        # Handle is_active flag
        if config_update.is_active is not None and config_update.is_active:
            self._deactivate_all()
            config.is_active = True
        
        # Handle is_default flag
        if config_update.is_default is not None and config_update.is_default:
            self._remove_default_flag()
            config.is_default = True
        
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def delete(self, config_id: int) -> bool:
        """
        Delete scoring configuration.
        
        Args:
            config_id: Configuration ID
        
        Returns:
            True if deleted
        
        Raises:
            NotFoundException: If configuration not found
            ValidationException: If trying to delete active or default config
        """
        config = self.get_by_id(config_id)
        if not config:
            raise NotFoundException("ScoringConfig", str(config_id))
        
        # Prevent deletion of active or default config
        if config.is_active:
            raise ValidationException(
                "Cannot delete active configuration. Deactivate it first."
            )
        
        if config.is_default:
            raise ValidationException(
                "Cannot delete default configuration. Unmark it as default first."
            )
        
        self.db.delete(config)
        self.db.commit()
        
        return True
    
    def activate(self, config_id: int) -> ScoringConfig:
        """
        Activate a configuration (deactivates others).
        
        Args:
            config_id: Configuration ID to activate
        
        Returns:
            Activated ScoringConfig
        
        Raises:
            NotFoundException: If configuration not found
        """
        config = self.get_by_id(config_id)
        if not config:
            raise NotFoundException("ScoringConfig", str(config_id))
        
        # Deactivate all others
        self._deactivate_all()
        
        # Activate this one
        config.is_active = True
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def set_as_default(self, config_id: int) -> ScoringConfig:
        """
        Set configuration as default.
        
        Args:
            config_id: Configuration ID
        
        Returns:
            Updated ScoringConfig
        
        Raises:
            NotFoundException: If configuration not found
        """
        config = self.get_by_id(config_id)
        if not config:
            raise NotFoundException("ScoringConfig", str(config_id))
        
        # Remove default flag from others
        self._remove_default_flag()
        
        # Set this as default
        config.is_default = True
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _deactivate_all(self) -> None:
        """Deactivate all configurations."""
        self.db.query(ScoringConfig).update(
            {ScoringConfig.is_active: False},
            synchronize_session=False
        )
    
    def _remove_default_flag(self) -> None:
        """Remove default flag from all configurations."""
        self.db.query(ScoringConfig).update(
            {ScoringConfig.is_default: False},
            synchronize_session=False
        )
