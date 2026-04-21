"""initial tables

Revision ID: 20260421_0001
Revises: 
Create Date: 2026-04-21 00:00:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260421_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("position", sa.String(length=20), nullable=False),
        sa.Column("current_round", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("round_no", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_round_no", "messages", ["round_no"], unique=False)
    op.create_index("ix_messages_session_id", "messages", ["session_id"], unique=False)

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("logic_score", sa.Integer(), nullable=False),
        sa.Column("evidence_score", sa.Integer(), nullable=False),
        sa.Column("fluency_score", sa.Integer(), nullable=False),
        sa.Column("suggestion", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_evaluations_session_id", "evaluations", ["session_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_evaluations_session_id", table_name="evaluations")
    op.drop_table("evaluations")
    op.drop_index("ix_messages_session_id", table_name="messages")
    op.drop_index("ix_messages_round_no", table_name="messages")
    op.drop_table("messages")
    op.drop_table("sessions")
