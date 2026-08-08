"""Create friends table

Revision ID: 8d170900652f
Revises: 493c2736dfb6
Create Date: 2026-07-31

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8d170900652f"
down_revision = "493c2736dfb6"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "friends",

        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "sender_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "receiver_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        ),
    )


def downgrade():

    op.drop_table("friends")