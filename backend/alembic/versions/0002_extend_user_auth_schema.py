"""extend user schema for authentication
Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-07-18 00:10:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "000000000002"
down_revision = "000000000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(length=128), nullable=False, server_default=""))
    op.add_column("users", sa.Column("last_name", sa.String(length=128), nullable=False, server_default=""))
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("profile_image", sa.String(length=512), nullable=True))
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")))
    op.add_column("users", sa.Column("verification_token", sa.String(length=255), nullable=True, unique=True))
    op.add_column("users", sa.Column("password_reset_token", sa.String(length=255), nullable=True, unique=True))
    op.add_column("users", sa.Column("password_reset_expiry", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("last_login", sa.DateTime(), nullable=True))
    op.alter_column("users", "is_active", server_default=sa.text("FALSE"))

    op.create_table(
        "revoked_refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_revoked_refresh_tokens_token"), "revoked_refresh_tokens", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_revoked_refresh_tokens_token"), table_name="revoked_refresh_tokens")
    op.drop_table("revoked_refresh_tokens")
    op.drop_column("users", "last_login")
    op.drop_column("users", "password_reset_expiry")
    op.drop_column("users", "password_reset_token")
    op.drop_column("users", "verification_token")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "profile_image")
    op.drop_column("users", "phone")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.alter_column("users", "is_active", server_default=sa.text("TRUE"))
