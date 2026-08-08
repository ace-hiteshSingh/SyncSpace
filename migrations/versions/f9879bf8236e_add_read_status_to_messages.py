"""Add read status to messages

Revision ID: f9879bf8236e
Revises: 980bc6366339
Create Date: 2026-08-02 00:28:03.245370

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f9879bf8236e"
down_revision = "980bc6366339"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("messages") as batch_op:

        batch_op.add_column(
            sa.Column(
                "is_read",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )

        batch_op.add_column(
            sa.Column(
                "read_at",
                sa.DateTime(),
                nullable=True
            )
        )

    op.execute(
        "UPDATE messages SET is_read = 0"
    )


def downgrade():

    with op.batch_alter_table("messages") as batch_op:

        batch_op.drop_column("read_at")

        batch_op.drop_column("is_read")