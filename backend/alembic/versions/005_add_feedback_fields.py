"""add_feedback_fields_for_module_g

Revision ID: 005_add_feedback_fields
Revises: 004_add_recommendations_tables
Create Date: 2026-01-06

Adds feedback fields to recommendations table for Module G (RF-RETRO-01).
Enables asesores to provide qualitative and quantitative feedback on recommendations.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_feedback_fields'
down_revision = '004_add_recommendations_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add feedback fields to recommendations table."""
    # Add feedback-related columns
    op.add_column('recommendations', sa.Column('was_used', sa.Boolean(), nullable=True))
    op.add_column('recommendations', sa.Column('feedback_date', sa.DateTime(), nullable=True))
    op.add_column('recommendations', sa.Column('feedback_asesor', sa.String(length=100), nullable=True))
    op.add_column('recommendations', sa.Column('skill_actually_worked', sa.String(length=200), nullable=True))
    op.add_column('recommendations', sa.Column('what_worked_well', sa.Text(), nullable=True))
    op.add_column('recommendations', sa.Column('what_didnt_work', sa.Text(), nullable=True))
    op.add_column('recommendations', sa.Column('additional_notes', sa.Text(), nullable=True))
    op.add_column('recommendations', sa.Column('can_edit_until', sa.DateTime(), nullable=True))
    
    # Add index for feedback queries
    op.create_index('ix_recommendations_feedback_date', 'recommendations', ['feedback_date'])
    op.create_index('ix_recommendations_feedback_asesor', 'recommendations', ['feedback_asesor'])


def downgrade() -> None:
    """Remove feedback fields from recommendations table."""
    # Drop indexes
    op.drop_index('ix_recommendations_feedback_asesor', table_name='recommendations')
    op.drop_index('ix_recommendations_feedback_date', table_name='recommendations')
    
    # Drop columns
    op.drop_column('recommendations', 'can_edit_until')
    op.drop_column('recommendations', 'additional_notes')
    op.drop_column('recommendations', 'what_didnt_work')
    op.drop_column('recommendations', 'what_worked_well')
    op.drop_column('recommendations', 'skill_actually_worked')
    op.drop_column('recommendations', 'feedback_asesor')
    op.drop_column('recommendations', 'feedback_date')
    op.drop_column('recommendations', 'was_used')

