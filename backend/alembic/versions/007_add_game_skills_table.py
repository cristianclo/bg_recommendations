"""add_game_skills_table

Revision ID: 007_add_game_skills_table
Revises: 006_add_admin_tables
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_game_skills_table'
down_revision = '006_add_admin_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create game_skills association table for many-to-many relationship
    op.create_table('game_skills',
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('justification', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('game_id', 'skill_id')
    )


def downgrade() -> None:
    op.drop_table('game_skills')
