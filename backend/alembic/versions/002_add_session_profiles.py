"""Add session_profiles table for Module B

Revision ID: 002_add_session_profiles
Revises: 001_initial
Create Date: 2026-01-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_session_profiles'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create modality enum
    modality_enum = postgresql.ENUM('competitive', 'cooperative', 'any', name='modality_enum')
    modality_enum.create(op.get_bind())
    
    # Create session_profiles table
    op.create_table(
        'session_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=True),
        sa.Column('objectives', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('primary_skill_id', sa.Integer(), nullable=True),
        sa.Column('secondary_skill_id', sa.Integer(), nullable=True),
        sa.Column('primary_skill_name', sa.String(length=255), nullable=False),
        sa.Column('secondary_skill_name', sa.String(length=255), nullable=True),
        sa.Column('available_time_min', sa.Integer(), nullable=False),
        sa.Column('group_size', sa.Integer(), nullable=False),
        sa.Column('max_language_dependency', sa.Enum('NINGUNA', 'BAJA', 'MEDIA', 'ALTA', name='language_dependency_enum'), nullable=False),
        sa.Column('preferred_modality', sa.Enum('competitive', 'cooperative', 'any', name='modality_enum'), nullable=False),
        sa.Column('additional_constraints', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('validation_warnings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('has_warnings', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_by_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('has_recommendations', sa.Boolean(), nullable=True, server_default='false'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_profiles_id'), 'session_profiles', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_session_profiles_id'), table_name='session_profiles')
    op.drop_table('session_profiles')
    
    # Drop modality enum
    modality_enum = postgresql.ENUM('competitive', 'cooperative', 'any', name='modality_enum')
    modality_enum.drop(op.get_bind())
