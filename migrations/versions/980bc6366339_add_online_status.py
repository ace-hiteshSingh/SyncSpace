"""Add online status

Revision ID: 980bc6366339
Revises: 976f0085a24a
Create Date: 2026-08-01 23:58:06.188972

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "980bc6366339"
down_revision = "976f0085a24a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("last_seen", sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column("users", "last_seen")