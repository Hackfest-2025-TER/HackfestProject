"""add politician verification fields

Revision ID: add_politician_verification
Revises: add_politician_slug
Create Date: 2025-12-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_politician_verification'
down_revision = 'add_politician_slug'
branch_labels = None
depends_on = None


def upgrade():
    # Add citizen verification fields
    op.add_column('politicians', sa.Column('citizen_nullifier', sa.String(length=128), nullable=True))
    op.add_column('politicians', sa.Column('citizen_voter_id', sa.String(length=50), nullable=True))
    op.add_column('politicians', sa.Column('citizenship_verified_at', sa.DateTime(), nullable=True))
    
    # Add politician verification status fields
    op.add_column('politicians', sa.Column('application_status', sa.String(length=20), nullable=True, server_default='approved'))
    op.add_column('politicians', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('politicians', sa.Column('verified_by', sa.String(length=100), nullable=True))
    op.add_column('politicians', sa.Column('verified_at', sa.DateTime(), nullable=True))
    op.add_column('politicians', sa.Column('election_commission_id', sa.String(length=50), nullable=True))
    op.add_column('politicians', sa.Column('rejection_reason', sa.Text(), nullable=True))
    
    # Create unique index on citizen_nullifier
    op.create_index('ix_politicians_citizen_nullifier', 'politicians', ['citizen_nullifier'], unique=True)
    
    # Update existing politicians to have verified status
    op.execute("""
        UPDATE politicians 
        SET application_status = 'approved', 
            is_verified = true,
            verified_at = created_at,
            verified_by = 'System Migration'
        WHERE application_status IS NULL OR is_verified IS NULL
    """)


def downgrade():
    # Drop index
    op.drop_index('ix_politicians_citizen_nullifier', table_name='politicians')
    
    # Remove columns
    op.drop_column('politicians', 'rejection_reason')
    op.drop_column('politicians', 'election_commission_id')
    op.drop_column('politicians', 'verified_at')
    op.drop_column('politicians', 'verified_by')
    op.drop_column('politicians', 'is_verified')
    op.drop_column('politicians', 'application_status')
    op.drop_column('politicians', 'citizenship_verified_at')
    op.drop_column('politicians', 'citizen_voter_id')
    op.drop_column('politicians', 'citizen_nullifier')
