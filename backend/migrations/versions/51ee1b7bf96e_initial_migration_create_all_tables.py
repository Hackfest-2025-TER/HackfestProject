"""Initial migration: Create all tables

Revision ID: 51ee1b7bf96e
Revises: 
Create Date: 2025-12-25 00:28:32.809972

This migration creates the complete database schema for PromiseThread:
- voters: Voter registry from election commission data
- zk_credentials: Zero-knowledge credentials for anonymous authentication
- politicians: Political figures who make promises
- manifestos: Political promises/manifestos
- manifesto_votes: Individual votes on manifestos (anonymous via nullifier)
- comments: Discussion comments on manifestos (threaded)
- comment_votes: Upvote/downvote tracking for comments
- audit_logs: Blockchain simulation for audit trail
- merkle_roots: Merkle roots for vote batches
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '51ee1b7bf96e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for PromiseThread"""
    
    # Create voters table
    op.create_table(
        'voters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('voter_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('spouse_name', sa.String(length=255), nullable=True),
        sa.Column('parent_name', sa.String(length=255), nullable=True),
        sa.Column('province', sa.String(length=50), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('vdc', sa.String(length=100), nullable=True),
        sa.Column('ward', sa.Integer(), nullable=True),
        sa.Column('registration_center', sa.String(length=255), nullable=True),
        sa.Column('merkle_leaf', sa.String(length=66), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('voter_id')
    )
    op.create_index(op.f('ix_voters_voter_id'), 'voters', ['voter_id'], unique=True)
    
    # Create zk_credentials table
    op.create_table(
        'zk_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nullifier_hash', sa.String(length=66), nullable=False),
        sa.Column('credential_hash', sa.String(length=66), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nullifier_hash')
    )
    op.create_index(op.f('ix_zk_credentials_nullifier_hash'), 'zk_credentials', ['nullifier_hash'], unique=True)
    
    # Create politicians table
    op.create_table(
        'politicians',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('party', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create manifestos table
    op.create_table(
        'manifestos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('politician_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('promise_hash', sa.String(length=66), nullable=True),
        sa.Column('grace_period_end', sa.DateTime(), nullable=False),
        sa.Column('vote_kept', sa.Integer(), nullable=True),
        sa.Column('vote_broken', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'kept', 'broken')", name='valid_status'),
        sa.ForeignKeyConstraint(['politician_id'], ['politicians.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create manifesto_votes table
    op.create_table(
        'manifesto_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manifesto_id', sa.Integer(), nullable=False),
        sa.Column('nullifier', sa.String(length=66), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('vote_hash', sa.String(length=66), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("vote_type IN ('kept', 'broken')", name='valid_vote_type'),
        sa.ForeignKeyConstraint(['manifesto_id'], ['manifestos.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manifesto_id', 'nullifier', name='unique_vote_per_manifesto')
    )
    op.create_index(op.f('ix_manifesto_votes_nullifier'), 'manifesto_votes', ['nullifier'], unique=False)
    
    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manifesto_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('nullifier_display', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('upvotes', sa.Integer(), nullable=True),
        sa.Column('downvotes', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['manifesto_id'], ['manifestos.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create comment_votes table
    op.create_table(
        'comment_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('nullifier', sa.String(length=66), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("vote_type IN ('up', 'down')", name='valid_comment_vote_type'),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('comment_id', 'nullifier', name='unique_vote_per_comment')
    )
    op.create_index(op.f('ix_comment_votes_nullifier'), 'comment_votes', ['nullifier'], unique=False)
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manifesto_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('block_hash', sa.String(length=66), nullable=False),
        sa.Column('prev_hash', sa.String(length=66), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['manifesto_id'], ['manifestos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create merkle_roots table
    op.create_table(
        'merkle_roots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('root_hash', sa.String(length=66), nullable=False),
        sa.Column('leaf_count', sa.Integer(), nullable=False),
        sa.Column('tree_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('root_hash')
    )


def downgrade() -> None:
    """Drop all tables (reverse migration)"""
    op.drop_table('merkle_roots')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_comment_votes_nullifier'), table_name='comment_votes')
    op.drop_table('comment_votes')
    op.drop_table('comments')
    op.drop_index(op.f('ix_manifesto_votes_nullifier'), table_name='manifesto_votes')
    op.drop_table('manifesto_votes')
    op.drop_table('manifestos')
    op.drop_table('politicians')
    op.drop_index(op.f('ix_zk_credentials_nullifier_hash'), table_name='zk_credentials')
    op.drop_table('zk_credentials')
    op.drop_index(op.f('ix_voters_voter_id'), table_name='voters')
    op.drop_table('voters')
