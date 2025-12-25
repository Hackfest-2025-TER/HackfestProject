"""Add slug column to politicians

Revision ID: add_politician_slug
Revises: 51ee1b7bf96e
Create Date: 2025-12-25 

"""
from alembic import op
import sqlalchemy as sa
import re


# revision identifiers, used by Alembic.
revision = 'add_politician_slug'
down_revision = '51ee1b7bf96e'
branch_labels = None
depends_on = None


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from politician name."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def upgrade():
    # Add slug column
    op.add_column('politicians', sa.Column('slug', sa.String(length=300), nullable=True))
    op.create_index('ix_politicians_slug', 'politicians', ['slug'], unique=True)
    
    # Populate slugs for existing politicians
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT id, name FROM politicians"))
    for row in res:
        slug = generate_slug(row[1])
        conn.execute(
            sa.text("UPDATE politicians SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": row[0]}
        )


def downgrade():
    op.drop_index('ix_politicians_slug', table_name='politicians')
    op.drop_column('politicians', 'slug')
