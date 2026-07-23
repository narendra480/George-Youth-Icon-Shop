"""add shop settings table

Revision ID: 000000000004
Revises: 000000000003
Create Date: 2026-07-18 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "000000000004"
down_revision = "000000000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shop_name", sa.String(length=255), nullable=False, server_default="George's Youth Icon Shop"),
        sa.Column("tagline", sa.String(length=255), nullable=True, server_default=sa.text("'Premium Footwear Collection'")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_name", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=512), nullable=True),
        sa.Column("favicon_url", sa.String(length=512), nullable=True),
        sa.Column("hero_banner_url", sa.String(length=512), nullable=True),
        sa.Column("primary_phone", sa.String(length=32), nullable=True),
        sa.Column("phone_numbers", sa.String(length=512), nullable=True),
        sa.Column("whatsapp", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("state", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("postal_code", sa.String(length=32), nullable=True),
        sa.Column("business_hours", sa.Text(), nullable=True),
        sa.Column("google_maps_url", sa.String(length=512), nullable=True),
        sa.Column("google_maps_embed", sa.Text(), nullable=True),
        sa.Column("facebook_url", sa.String(length=512), nullable=True),
        sa.Column("instagram_url", sa.String(length=512), nullable=True),
        sa.Column("youtube_url", sa.String(length=512), nullable=True),
        sa.Column("twitter_url", sa.String(length=512), nullable=True),
        sa.Column("linkedin_url", sa.String(length=512), nullable=True),
        sa.Column("footer_text", sa.Text(), nullable=True),
        sa.Column("copyright_text", sa.String(length=255), nullable=True),
        sa.Column("privacy_policy_url", sa.String(length=512), nullable=True),
        sa.Column("terms_url", sa.String(length=512), nullable=True),
        sa.Column("faq_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("shop_settings")
