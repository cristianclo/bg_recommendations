"""add recommendations tables

Revision ID: 004_add_recommendations_tables
Revises: 003_add_skills_table
Create Date: 2026-01-05

Implements Module D (Recommendation Engine):
- RF-REC-01: Recommendations table for traceability
- RF-REC-02: ScoringConfig table for configurable weights
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_add_recommendations_tables'
down_revision: Union[str, None] = '003_add_skills_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create scoring_configs table
    op.create_table('scoring_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Weights (sum must be 1.0)
        sa.Column('skill_weight', sa.Float(), nullable=False),
        sa.Column('mechanics_weight', sa.Float(), nullable=False),
        sa.Column('difficulty_weight', sa.Float(), nullable=False),
        sa.Column('ranking_weight', sa.Float(), nullable=False),
        
        # Configuration flags
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        
        # Timestamps and audit
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scoring_configs_id'), 'scoring_configs', ['id'], unique=False)
    op.create_index(op.f('ix_scoring_configs_is_active'), 'scoring_configs', ['is_active'], unique=False)
    op.create_index(op.f('ix_scoring_configs_name'), 'scoring_configs', ['name'], unique=True)
    
    # Create recommendations table
    op.create_table('recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Foreign keys
        sa.Column('session_profile_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        
        # Scoring data
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Float(), nullable=False),
        sa.Column('skill_score', sa.Float(), nullable=False),
        sa.Column('mechanics_score', sa.Float(), nullable=False),
        sa.Column('difficulty_score', sa.Float(), nullable=False),
        sa.Column('ranking_score', sa.Float(), nullable=False),
        sa.Column('feedback_boost', sa.Float(), nullable=False),
        
        # Traceability (RF-REC-01, RF-EXP-02)
        sa.Column('weights_used', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('explanation_text', sa.Text(), nullable=True),
        sa.Column('match_reasons', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Feedback tracking (RF-RETRO-01)
        sa.Column('was_selected', sa.Boolean(), nullable=False),
        sa.Column('user_feedback_score', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_profile_id'], ['session_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendations_game_id'), 'recommendations', ['game_id'], unique=False)
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_recommendations_session_profile_id'), 'recommendations', ['session_profile_id'], unique=False)
    op.create_index(op.f('ix_recommendations_was_selected'), 'recommendations', ['was_selected'], unique=False)


def downgrade() -> None:
    # Drop recommendations table
    op.drop_index(op.f('ix_recommendations_was_selected'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_session_profile_id'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_id'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_game_id'), table_name='recommendations')
    op.drop_table('recommendations')
    
    # Drop scoring_configs table
    op.drop_index(op.f('ix_scoring_configs_name'), table_name='scoring_configs')
    op.drop_index(op.f('ix_scoring_configs_is_active'), table_name='scoring_configs')
    op.drop_index(op.f('ix_scoring_configs_id'), table_name='scoring_configs')
    op.drop_table('scoring_configs')
