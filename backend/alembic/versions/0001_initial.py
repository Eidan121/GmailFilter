"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(inspect(bind).get_table_names())

    if "gmail_accounts" not in existing:
        op.create_table(
            "gmail_accounts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(), nullable=False, unique=True),
            sa.Column("display_name", sa.String()),
            sa.Column("token_path", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), default=True),
            sa.Column("last_seen", sa.DateTime()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        )

    if "cached_filters" not in existing:
        op.create_table(
            "cached_filters",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("account_id", sa.Integer(), sa.ForeignKey("gmail_accounts.id", ondelete="CASCADE")),
            sa.Column("gmail_filter_id", sa.String(), nullable=False),
            sa.Column("criteria_json", sa.String(), nullable=False),
            sa.Column("action_json", sa.String(), nullable=False),
            sa.Column("synced_at", sa.DateTime(), server_default=sa.func.now()),
        )

    if "scan_results" not in existing:
        op.create_table(
            "scan_results",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("account_id", sa.Integer(), sa.ForeignKey("gmail_accounts.id", ondelete="CASCADE")),
            sa.Column("scanned_at", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("emails_scanned", sa.Integer(), default=0),
            sa.Column("flood_count", sa.Integer(), default=0),
            sa.Column("duration_sec", sa.Float(), default=0.0),
        )

    if "filter_suggestions" not in existing:
        op.create_table(
            "filter_suggestions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("account_id", sa.Integer(), sa.ForeignKey("gmail_accounts.id", ondelete="CASCADE")),
            sa.Column("scan_result_id", sa.Integer(), sa.ForeignKey("scan_results.id", ondelete="SET NULL")),
            sa.Column("sender_email", sa.String(), nullable=False),
            sa.Column("sender_domain", sa.String(), nullable=False),
            sa.Column("email_count", sa.Integer(), default=0),
            sa.Column("suggested_label", sa.String(), nullable=False),
            sa.Column("suggested_action", sa.String(), nullable=False),
            sa.Column("criteria_json", sa.String(), nullable=False),
            sa.Column("ai_rationale", sa.String()),
            sa.Column("status", sa.String(), default="pending"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("acted_at", sa.DateTime()),
        )


def downgrade() -> None:
    op.drop_table("filter_suggestions")
    op.drop_table("scan_results")
    op.drop_table("cached_filters")
    op.drop_table("gmail_accounts")
