"""add_admin_tables_for_module_h

Revision ID: dc0be62ab7eb
Revises: 005_add_feedback_fields
Create Date: 2026-01-06 01:25:46.597480-05:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_admin_tables'
down_revision = '005_add_feedback_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_logs table
    op.create_table('audit_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_type', sa.Enum('GAME', 'SKILL', 'SESSION', 'RECOMMENDATION', 'SCORING_CONFIG', 'TAXONOMY', name='auditlogentity'), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.Enum('CREATE', 'UPDATE', 'DELETE', 'BULK_IMPORT', 'EXPORT', 'REORGANIZE', name='auditlogaction'), nullable=False),
    sa.Column('user_id', sa.String(length=100), nullable=False),
    sa.Column('user_role', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('changes_summary', sa.Text(), nullable=True),
    sa.Column('affected_count', sa.Integer(), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('session_id', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    
    # Create taxonomy_snapshots table
    op.create_table('taxonomy_snapshots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', sa.String(length=100), nullable=False),
    sa.Column('snapshot_data', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('skill_count', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_taxonomy_snapshots_created_at'), 'taxonomy_snapshots', ['created_at'], unique=False)
    op.create_index(op.f('ix_taxonomy_snapshots_id'), 'taxonomy_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_taxonomy_snapshots_version'), 'taxonomy_snapshots', ['version'], unique=True)


def downgrade() -> None:
    # Drop taxonomy_snapshots table
    op.drop_index(op.f('ix_taxonomy_snapshots_version'), table_name='taxonomy_snapshots')
    op.drop_index(op.f('ix_taxonomy_snapshots_id'), table_name='taxonomy_snapshots')
    op.drop_index(op.f('ix_taxonomy_snapshots_created_at'), table_name='taxonomy_snapshots')
    op.drop_table('taxonomy_snapshots')
    
    # Drop audit_logs table
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
