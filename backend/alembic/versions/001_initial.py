"""Initial migration with games table

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create language_dependency enum
    language_dep_enum = postgresql.ENUM('NINGUNA', 'BAJA', 'MEDIA', 'ALTA', name='language_dependency_enum')
    language_dep_enum.create(op.get_bind())
    
    # Create games table
    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('bgg_id', sa.Integer(), nullable=False),
        sa.Column('duration_min', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('complexity', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('min_players', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('max_players', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('mechanics', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('language_dependency', sa.Enum('NINGUNA', 'BAJA', 'MEDIA', 'ALTA', name='language_dependency_enum'), nullable=False, server_default='BAJA'),
        sa.Column('bgg_rank', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('year_published', sa.Integer(), nullable=True),
        sa.Column('available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('has_partial_data', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_games_id'), 'games', ['id'], unique=False)
    op.create_index(op.f('ix_games_bgg_id'), 'games', ['bgg_id'], unique=True)
    op.create_index(op.f('ix_games_name'), 'games', ['name'], unique=False)
    op.create_index(op.f('ix_games_available'), 'games', ['available'], unique=False)
    op.create_index(op.f('ix_games_bgg_rank'), 'games', ['bgg_rank'], unique=False)
    op.create_index('idx_game_available_complexity', 'games', ['available', 'complexity'], unique=False)
    op.create_index('idx_game_players', 'games', ['min_players', 'max_players'], unique=False)
    op.create_index('idx_game_duration', 'games', ['duration_min'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_game_duration', table_name='games')
    op.drop_index('idx_game_players', table_name='games')
    op.drop_index('idx_game_available_complexity', table_name='games')
    op.drop_index(op.f('ix_games_bgg_rank'), table_name='games')
    op.drop_index(op.f('ix_games_available'), table_name='games')
    op.drop_index(op.f('ix_games_name'), table_name='games')
    op.drop_index(op.f('ix_games_bgg_id'), table_name='games')
    op.drop_index(op.f('ix_games_id'), table_name='games')
    op.drop_table('games')
    
    # Drop language_dependency enum
    language_dep_enum = postgresql.ENUM('NINGUNA', 'BAJA', 'MEDIA', 'ALTA', name='language_dependency_enum')
    language_dep_enum.drop(op.get_bind())
