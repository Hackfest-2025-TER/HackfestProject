"""
Update comments table for cosine similarity moderation

Revision ID: add_comment_moderation_fields
Revises: add_signature_columns
Create Date: 2025-12-25

Changes:
- Remove nullifier_display (no longer required)
- Add session_id for anonymous author tracking
- Add author_display for user-friendly display name
- Add moderation state fields (state, auto_flag_reason)
- Add similarity scores (similarity_score, matched_promise_id, spam_similarity_score)
- Add flag_count for community flagging
- Add delete_scheduled_at for delayed deletion
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_comment_moderation_fields'
down_revision = 'add_signature_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column('comments', sa.Column('session_id', sa.String(32), nullable=True))
    op.add_column('comments', sa.Column('author_display', sa.String(20), nullable=True))
    op.add_column('comments', sa.Column('state', sa.String(20), server_default='active', nullable=True))
    op.add_column('comments', sa.Column('auto_flag_reason', sa.String(20), nullable=True))
    op.add_column('comments', sa.Column('similarity_score', sa.Integer(), nullable=True))
    op.add_column('comments', sa.Column('matched_promise_id', sa.Integer(), nullable=True))
    op.add_column('comments', sa.Column('spam_similarity_score', sa.Integer(), nullable=True))
    op.add_column('comments', sa.Column('flag_count', sa.Integer(), server_default='0', nullable=True))
    op.add_column('comments', sa.Column('delete_scheduled_at', sa.DateTime(), nullable=True))
    
    # Migrate existing data: convert nullifier_display to session_id
    op.execute("""
        UPDATE comments 
        SET session_id = COALESCE(REPLACE(nullifier_display, '...', ''), 'legacy_' || id::text),
            author_display = 'Citizen-' || COALESCE(LEFT(REPLACE(nullifier_display, '...', ''), 6), 'legacy'),
            state = 'active'
        WHERE session_id IS NULL
    """)
    
    # Make session_id required after migration
    op.alter_column('comments', 'session_id', nullable=False)
    
    # Drop old column (optional - keep for now for backward compatibility)
    # op.drop_column('comments', 'nullifier_display')
    
    # Update comment_votes to support 'flag' vote_type
    # The existing check constraint needs to be updated
    op.execute("""
        ALTER TABLE comment_votes 
        DROP CONSTRAINT IF EXISTS valid_comment_vote_type
    """)
    op.execute("""
        ALTER TABLE comment_votes 
        ADD CONSTRAINT valid_comment_vote_type 
        CHECK (vote_type IN ('up', 'down', 'flag'))
    """)


def downgrade() -> None:
    # Revert comment_votes constraint
    op.execute("""
        ALTER TABLE comment_votes 
        DROP CONSTRAINT IF EXISTS valid_comment_vote_type
    """)
    op.execute("""
        ALTER TABLE comment_votes 
        ADD CONSTRAINT valid_comment_vote_type 
        CHECK (vote_type IN ('up', 'down'))
    """)
    
    # Drop new columns
    op.drop_column('comments', 'delete_scheduled_at')
    op.drop_column('comments', 'flag_count')
    op.drop_column('comments', 'spam_similarity_score')
    op.drop_column('comments', 'matched_promise_id')
    op.drop_column('comments', 'similarity_score')
    op.drop_column('comments', 'auto_flag_reason')
    op.drop_column('comments', 'state')
    op.drop_column('comments', 'author_display')
    op.drop_column('comments', 'session_id')
