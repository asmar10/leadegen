"""Initial tables

Revision ID: 001
Revises:
Create Date: 2024-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stores table
    op.create_table(
        'stores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('domain', sa.String(255), nullable=False),
        sa.Column('store_name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('niche', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instagram', sa.String(255), nullable=True),
        sa.Column('tiktok', sa.String(255), nullable=True),
        sa.Column('facebook', sa.String(255), nullable=True),
        sa.Column('twitter', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_scraped_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stores_id', 'stores', ['id'])
    op.create_index('ix_stores_url', 'stores', ['url'], unique=True)
    op.create_index('ix_stores_domain', 'stores', ['domain'], unique=True)
    op.create_index('ix_stores_email', 'stores', ['email'])
    op.create_index('ix_stores_country', 'stores', ['country'])
    op.create_index('ix_stores_niche', 'stores', ['niche'])

    # Create search_jobs table
    op.create_table(
        'search_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query', sa.String(500), nullable=False),
        sa.Column('niche', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='searchstatus'), nullable=False),
        sa.Column('stores_found', sa.Integer(), default=0),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_search_jobs_id', 'search_jobs', ['id'])
    op.create_index('ix_search_jobs_status', 'search_jobs', ['status'])
    op.create_index('ix_search_jobs_niche', 'search_jobs', ['niche'])
    op.create_index('ix_search_jobs_location', 'search_jobs', ['location'])

    # Create search_results table
    op.create_table(
        'search_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('search_id', sa.Integer(), nullable=False),
        sa.Column('store_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['search_id'], ['search_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_search_results_id', 'search_results', ['id'])
    op.create_index('ix_search_results_search_id', 'search_results', ['search_id'])
    op.create_index('ix_search_results_store_id', 'search_results', ['store_id'])


def downgrade() -> None:
    op.drop_table('search_results')
    op.drop_table('search_jobs')
    op.drop_table('stores')
    op.execute('DROP TYPE IF EXISTS searchstatus')
