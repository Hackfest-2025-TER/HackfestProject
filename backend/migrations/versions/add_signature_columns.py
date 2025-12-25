"""Add digital signature columns

Revision ID: add_signature_columns
Revises: 51ee1b7bf96e
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_signature_columns'
down_revision = '51ee1b7bf96e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to politicians table
    op.add_column('politicians', sa.Column('wallet_address', sa.String(42), unique=True, nullable=True))
    op.add_column('politicians', sa.Column('wallet_created_at', sa.DateTime(), nullable=True))
    op.add_column('politicians', sa.Column('public_key', sa.String(130), nullable=True))
    op.add_column('politicians', sa.Column('key_version', sa.Integer(), default=1, nullable=True))
    op.add_column('politicians', sa.Column('key_revoked', sa.Boolean(), default=False, nullable=True))
    op.add_column('politicians', sa.Column('key_revoked_at', sa.DateTime(), nullable=True))
    op.add_column('politicians', sa.Column('key_revoked_reason', sa.String(255), nullable=True))
    op.add_column('politicians', sa.Column('previous_wallet_addresses', postgresql.JSONB(), default=list, nullable=True))
    
    # Add columns to manifestos table
    op.add_column('manifestos', sa.Column('signature', sa.Text(), nullable=True))
    op.add_column('manifestos', sa.Column('signed_at', sa.DateTime(), nullable=True))
    op.add_column('manifestos', sa.Column('signer_address', sa.String(42), nullable=True))
    op.add_column('manifestos', sa.Column('signer_key_version', sa.Integer(), nullable=True))
    op.add_column('manifestos', sa.Column('blockchain_tx', sa.String(66), nullable=True))
    op.add_column('manifestos', sa.Column('blockchain_confirmed', sa.Boolean(), default=False, nullable=True))
    op.add_column('manifestos', sa.Column('blockchain_block', sa.Integer(), nullable=True))
    op.add_column('manifestos', sa.Column('legacy_unverified', sa.Boolean(), default=False, nullable=True))
    
    # Mark existing manifestos as legacy (unverified)
    op.execute("UPDATE manifestos SET legacy_unverified = TRUE WHERE signature IS NULL")
    
    # Set default key_version for politicians
    op.execute("UPDATE politicians SET key_version = 1 WHERE key_version IS NULL")
    op.execute("UPDATE politicians SET key_revoked = FALSE WHERE key_revoked IS NULL")


def downgrade() -> None:
    # Remove columns from manifestos table
    op.drop_column('manifestos', 'legacy_unverified')
    op.drop_column('manifestos', 'blockchain_block')
    op.drop_column('manifestos', 'blockchain_confirmed')
    op.drop_column('manifestos', 'blockchain_tx')
    op.drop_column('manifestos', 'signer_key_version')
    op.drop_column('manifestos', 'signer_address')
    op.drop_column('manifestos', 'signed_at')
    op.drop_column('manifestos', 'signature')
    
    # Remove columns from politicians table
    op.drop_column('politicians', 'previous_wallet_addresses')
    op.drop_column('politicians', 'key_revoked_reason')
    op.drop_column('politicians', 'key_revoked_at')
    op.drop_column('politicians', 'key_revoked')
    op.drop_column('politicians', 'key_version')
    op.drop_column('politicians', 'public_key')
    op.drop_column('politicians', 'wallet_created_at')
    op.drop_column('politicians', 'wallet_address')
