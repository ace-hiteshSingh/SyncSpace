"""Create messages table

Revision ID: 976f0085a24a
Revises: 8d170900652f
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "976f0085a24a"
down_revision = "8d170900652f"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "messages",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

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
            "content",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )


def downgrade():

    op.drop_table("messages")