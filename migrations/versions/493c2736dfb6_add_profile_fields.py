"""Add profile fields

Revision ID: 493c2736dfb6
Revises: a9abfc37d86c
Create Date: 2026-07-31

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "493c2736dfb6"
down_revision = "a9abfc37d86c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("avatar", sa.String(length=255), nullable=True)
        )

        batch_op.drop_column("profile_image")


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("profile_image", sa.String(length=255), nullable=True)
        )

        batch_op.drop_column("avatar")