from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Table, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(512), nullable=True)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    sku = Column(String(64), unique=True, nullable=False, index=True)
    barcode = Column(String(64), nullable=True, unique=True, index=True)

    short_description = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    specifications = Column(JSON, nullable=True)
    search_keywords = Column(String(512), nullable=True, index=True)
    tags = Column(JSON, nullable=True)

    dimensions = Column(JSON, nullable=True)
    weight = Column(Float, nullable=True)
    weight_unit = Column(String(16), nullable=True, default="kg")

    gst_percentage = Column(Float, nullable=True)
    hsn_code = Column(String(16), nullable=True)
    country_of_origin = Column(String(64), nullable=True)
    manufacturer = Column(String(255), nullable=True)

    cost_price = Column(Float, nullable=True)
    mrp = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0, nullable=False)
    offer_price = Column(Float, nullable=True)
    offer_start_date = Column(DateTime, nullable=True)
    offer_end_date = Column(DateTime, nullable=True)

    is_featured = Column(Boolean, default=False, nullable=False)
    is_new_arrival = Column(Boolean, default=False, nullable=False)
    is_best_seller = Column(Boolean, default=False, nullable=False)
    is_trending = Column(Boolean, default=False, nullable=False)

    status = Column(String(32), default="draft", nullable=False, index=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    inventories = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    inventory_histories = relationship("InventoryHistory", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_path = Column(String(512), nullable=False)
    alt_text = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="images")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    sku = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    attributes = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)

    price = Column(Float, nullable=True)
    mrp = Column(Float, nullable=True)
    inventory_quantity = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    product = relationship("Product", back_populates="variants")
    inventories = relationship("Inventory", back_populates="variant", cascade="all, delete-orphan")
    inventory_histories = relationship("InventoryHistory", back_populates="variant", cascade="all, delete-orphan")


class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True)

    current_stock = Column(Integer, default=0, nullable=False)
    reserved_stock = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=0, nullable=False)
    low_stock_alert = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="inventories")
    variant = relationship("ProductVariant", back_populates="inventories")


class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True)

    change_type = Column(String(32), nullable=False, index=True)
    quantity_change = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    reference_id = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="inventory_histories")
    variant = relationship("ProductVariant", back_populates="inventory_histories")


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    subtitle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=False)
    mobile_image_url = Column(String(512), nullable=True)
    link_url = Column(String(512), nullable=True)
    position = Column(String(64), nullable=False, default="home")
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    background_color = Column(String(32), nullable=True)
    text_color = Column(String(32), nullable=True)
    overlay_opacity = Column(Float, nullable=True, default=0.5)
    banner_type = Column(String(32), nullable=False, default="hero")
    redirect_type = Column(String(32), nullable=False, default="url")
    cta_button_1_text = Column(String(64), nullable=True)
    cta_button_1_url = Column(String(512), nullable=True)
    cta_button_2_text = Column(String(64), nullable=True)
    cta_button_2_url = Column(String(512), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    collection_id = Column(Integer, nullable=True)
    is_featured = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    click_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    is_saved_for_later = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class Wishlist(Base):
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    discount_type = Column(String(32), nullable=False)
    discount_value = Column(Float, nullable=False)
    min_order_amount = Column(Float, nullable=True)
    max_discount_amount = Column(Float, nullable=True)
    max_uses = Column(Integer, nullable=True)
    max_uses_per_user = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CouponUsage(Base):
    __tablename__ = "coupon_usages"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, nullable=True)
    discount_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    is_verified_purchase = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product")
    user = relationship("User")


class RecentlyViewed(Base):
    __tablename__ = "recently_viewed"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(128), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(32), nullable=True)
    profile_image = Column(String(512), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True, unique=True)
    password_reset_token = Column(String(255), nullable=True, unique=True)
    password_reset_expiry = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    banner_url = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    icon_url = Column(String(512), nullable=True)
    is_featured = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles", cascade="all, delete")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(64), nullable=False, default="general")
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions", cascade="all, delete")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reason = Column(Text, nullable=True)

    user = relationship("User", foreign_keys=[user_id], backref="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])


class ShopSettings(Base):
    __tablename__ = "shop_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    shop_name = Column(String(255), nullable=False, default="George's Youth Icon Shop")
    tagline = Column(String(255), nullable=True, default="Premium Footwear Collection")
    description = Column(Text, nullable=True)
    owner_name = Column(String(255), nullable=True)
    
    logo_url = Column(String(512), nullable=True)
    favicon_url = Column(String(512), nullable=True)
    hero_banner_url = Column(String(512), nullable=True)
    
    primary_phone = Column(String(32), nullable=True)
    phone_numbers = Column(String(512), nullable=True)
    whatsapp = Column(String(32), nullable=True)
    email = Column(String(255), nullable=True)
    
    address = Column(String(255), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)
    country = Column(String(128), nullable=True)
    postal_code = Column(String(32), nullable=True)
    
    business_hours = Column(Text, nullable=True)
    google_maps_url = Column(String(512), nullable=True)
    google_maps_embed = Column(Text, nullable=True)
    
    facebook_url = Column(String(512), nullable=True)
    instagram_url = Column(String(512), nullable=True)
    youtube_url = Column(String(512), nullable=True)
    twitter_url = Column(String(512), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    
    footer_text = Column(Text, nullable=True)
    copyright_text = Column(String(255), nullable=True)
    privacy_policy_url = Column(String(512), nullable=True)
    terms_url = Column(String(512), nullable=True)
    faq_url = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    mobile = Column(String(32), nullable=False)
    alternate_mobile = Column(String(32), nullable=True)
    house_flat = Column(String(255), nullable=False)
    street = Column(String(255), nullable=False)
    landmark = Column(String(255), nullable=True)
    area = Column(String(128), nullable=True)
    district = Column(String(128), nullable=True)
    city = Column(String(128), nullable=False)
    state = Column(String(128), nullable=False)
    country = Column(String(128), nullable=True, default="India")
    pincode = Column(String(32), nullable=False)
    address_type = Column(String(32), nullable=False, default="home")
    is_default = Column(Boolean, default=False, nullable=False)
    gst_number = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    
    subtotal = Column(Float, nullable=False)
    gst_amount = Column(Float, nullable=False)
    shipping_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False)
    
    status = Column(String(32), nullable=False, default="pending")
    payment_status = Column(String(32), nullable=False, default="pending")
    payment_method = Column(String(64), nullable=True)
    
    coupon_code = Column(String(64), nullable=True)
    delivery_estimate = Column(String(128), nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    address = relationship("Address")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False)
    note = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="status_history")
    admin = relationship("User", foreign_keys=[created_by])


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    invoice_number = Column(String(64), unique=True, nullable=False)
    invoice_url = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    payment_method = Column(String(32), nullable=False)
    payment_gateway = Column(String(64), nullable=True)
    gateway_transaction_id = Column(String(128), nullable=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    status = Column(String(32), nullable=False, default="pending")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    type = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    balance = Column(Float, nullable=True)
    
    reference_id = Column(String(128), nullable=True)
    remarks = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(32), nullable=False, default="system")
    is_read = Column(Boolean, default=False, nullable=False)
    
    link_url = Column(String(512), nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PaymentAudit(Base):
    __tablename__ = "payment_audits"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False, index=True)
    
    action = Column(String(64), nullable=False)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    payment = relationship("Payment")


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True, index=True)
    courier_partner_id = Column(Integer, ForeignKey("courier_partners.id"), nullable=True, index=True)
    
    tracking_number = Column(String(128), nullable=True, index=True)
    awb_number = Column(String(128), nullable=True)
    courier_name = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    
    estimated_delivery = Column(DateTime, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    order = relationship("Order", backref="shipments")
    warehouse = relationship("Warehouse", backref="shipments")
    courier_partner = relationship("CourierPartner", backref="shipments")


class ShipmentPackage(Base):
    __tablename__ = "shipment_packages"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True)
    
    package_number = Column(String(64), nullable=True)
    weight = Column(Float, nullable=True)
    dimensions = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CourierPartner(Base):
    __tablename__ = "courier_partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), nullable=False, unique=True)
    api_key = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    
    status = Column(String(64), nullable=False)
    location = Column(String(256), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    remarks = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shipment = relationship("Shipment", backref="tracking_events")


class DeliveryProof(Base):
    __tablename__ = "delivery_proofs"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, unique=True)
    
    receiver_name = Column(String(128), nullable=True)
    signature_image = Column(String(512), nullable=True)
    delivery_image = Column(String(512), nullable=True)
    otp = Column(String(16), nullable=True)
    gps_coordinates = Column(String(128), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shipment = relationship("Shipment", backref="delivery_proof")


class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False)
    remarks = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    attempted_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shipment = relationship("Shipment", backref="delivery_attempts")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    
    address = Column(String(256), nullable=False)
    city = Column(String(128), nullable=False)
    state = Column(String(128), nullable=False)
    pincode = Column(String(32), nullable=False)
    manager = Column(String(128), nullable=True)
    
    priority = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    reason = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    order = relationship("Order", backref="return_requests")
    user = relationship("User", foreign_keys=[user_id])


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    contact_person = Column(String(128), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(32), nullable=True)
    gstin = Column(String(32), nullable=True)
    pan = Column(String(32), nullable=True)
    
    address = Column(String(256), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)
    country = Column(String(128), nullable=True, default="India")
    pincode = Column(String(32), nullable=True)
    
    bank_details = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(64), nullable=False, unique=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True, index=True)
    
    status = Column(String(32), nullable=False, default="draft")
    expected_delivery = Column(DateTime, nullable=True)
    total_amount = Column(Float, nullable=False, default=0)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    supplier = relationship("Supplier", backref="purchase_orders")
    warehouse = relationship("Warehouse", backref="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    gst_rate = Column(Float, nullable=False, default=18)
    discount = Column(Float, nullable=False, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class GoodsReceiptNote(Base):
    __tablename__ = "goods_receipt_notes"

    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String(64), nullable=False, unique=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    
    received_quantity = Column(Integer, nullable=False)
    rejected_quantity = Column(Integer, nullable=False, default=0)
    damaged_quantity = Column(Integer, nullable=False, default=0)
    
    remarks = Column(Text, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    purchase_order = relationship("PurchaseOrder", backref="grns")


class LoyaltyPoint(Base):
    __tablename__ = "loyalty_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    points = Column(Integer, nullable=False, default=0)
    source = Column(String(32), nullable=False)
    reference_id = Column(String(64), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    referral_code = Column(String(32), nullable=False, unique=True)
    status = Column(String(32), nullable=False, default="pending")
    
    reward_points = Column(Integer, nullable=False, default=0)
    rewarded_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    referrer = relationship("User", foreign_keys=[referrer_id])
    referred = relationship("User", foreign_keys=[referred_id])


class GiftCard(Base):
    __tablename__ = "gift_cards"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), nullable=False, unique=True)
    
    amount = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ProductQuestion(Base):
    __tablename__ = "product_questions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    answered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    answered_at = Column(DateTime, nullable=True)
    
    is_helpful = Column(Integer, default=0, nullable=False)
    is_reported = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product")
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[answered_by])


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    event_type = Column(String(32), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    search_query = Column(String(255), nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    recommendation_type = Column(String(32), nullable=False)
    score = Column(Float, nullable=False, default=0)
    is_clicked = Column(Boolean, default=False, nullable=False)
    is_purchased = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    vendor_code = Column(String(32), nullable=False, unique=True)
    shop_name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    
    gstin = Column(String(32), nullable=True)
    pan = Column(String(32), nullable=True)
    bank_account = Column(String(64), nullable=True)
    settlement_account = Column(String(64), nullable=True)
    
    commission_percentage = Column(Float, nullable=False, default=10)
    rating = Column(Float, nullable=True, default=0)
    
    status = Column(String(32), nullable=False, default="pending")
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User")


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    
    amount = Column(Float, nullable=False)
    commission = Column(Float, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="pending")
    
    settled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    vendor = relationship("Vendor", backref="settlements")


class Franchise(Base):
    __tablename__ = "franchises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    
    store_name = Column(String(255), nullable=False)
    store_code = Column(String(32), nullable=False, unique=True)
    
    address = Column(String(256), nullable=False)
    city = Column(String(128), nullable=False)
    state = Column(String(128), nullable=False)
    pincode = Column(String(32), nullable=False)
    
    manager_name = Column(String(128), nullable=True)
    manager_phone = Column(String(32), nullable=True)
    
    revenue = Column(Float, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User")


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    activity_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
