"""Fix ZK credential column sizes for larger nullifier hashes

Revision ID: fix_zk_columns
Revises: 63d18e39e5cd
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_zk_columns'
down_revision: Union[str, None] = '63d18e39e5cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ZK nullifier hashes from snarkjs can be up to 78 characters (256-bit decimal number)
    # Increase column size to 128 to be safe
    op.alter_column('zk_credentials', 'nullifier_hash',
                    existing_type=sa.String(66),
                    type_=sa.String(128),
                    existing_nullable=False)
    
    op.alter_column('zk_credentials', 'credential_hash',
                    existing_type=sa.String(66),
                    type_=sa.String(128),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('zk_credentials', 'nullifier_hash',
                    existing_type=sa.String(128),
                    type_=sa.String(66),
                    existing_nullable=False)
    
    op.alter_column('zk_credentials', 'credential_hash',
                    existing_type=sa.String(128),
                    type_=sa.String(66),
                    existing_nullable=False)
