"""merge_branches

Revision ID: 63d18e39e5cd
Revises: add_politician_slug, add_signature_columns
Create Date: 2025-12-25 10:03:34.911492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63d18e39e5cd'
down_revision: Union[str, None] = ('add_politician_slug', 'add_signature_columns')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
