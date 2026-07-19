"""add RBAC tables (roles, permissions, user_roles)

Revision ID: 000000000003
Revises: 000000000002
Create Date: 2026-07-18 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "000000000003"
down_revision = "000000000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)
    op.create_index(op.f("ix_roles_slug"), "roles", ["slug"], unique=True)

    # Create permissions table
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False, server_default=sa.text("'general'")),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissions_name"), "permissions", ["name"], unique=True)
    op.create_index(op.f("ix_permissions_slug"), "permissions", ["slug"], unique=True)

    # Create role_permissions association table
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # Create user_roles table
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_roles_user_id"), "user_roles", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_user_roles_user_id"), table_name="user_roles")
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_index(op.f("ix_permissions_slug"), table_name="permissions")
    op.drop_index(op.f("ix_permissions_name"), table_name="permissions")
    op.drop_table("permissions")
    op.drop_index(op.f("ix_roles_slug"), table_name="roles")
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")
