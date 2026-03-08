from enum import Enum
from db import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserType(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SELLER = "seller"


class SellerStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(db.String(128), nullable=False)

    user_type = db.Column(
        db.Enum(UserType, name="user_type_enum", native_enum=False),
        default=UserType.CUSTOMER,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    # --- Password handling ---

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, password: str) -> None:
        self.set_password(password)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    full_name = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)

    user = db.relationship(
        "User",
        backref=db.backref(
            "profile",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<Profile id={self.id} user_id={self.user_id}>"


class SellerProfile(db.Model):
    __tablename__ = "seller_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    # --- Public seller identity ---
    display_name = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    business_email = db.Column(db.String(120), nullable=True)
    business_phone = db.Column(db.String(20), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)

    # --- Seller trust & moderation ---
    status = db.Column(
        db.Enum(SellerStatus, name="seller_status_enum", native_enum=False),
        default=SellerStatus.PENDING,
        nullable=False
    )

    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)

    # --- Seller metrics ---
    rating_avg = db.Column(db.Float, default=0.0, nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)
    total_sales = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship(
        "User",
        backref=db.backref(
            "seller_profile",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<SellerProfile id={self.id} user_id={self.user_id}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category id={self.id} name={self.name}>"


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False, default="USA")
    
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("addresses", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Address id={self.id} user_id={self.user_id} city={self.city}>"


class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    discount_type = db.Column(
        db.Enum(DiscountType, name="discount_type_enum", native_enum=False),
        nullable=False
    )
    discount_value = db.Column(db.Float, nullable=False)
    
    min_cart_value = db.Column(db.Float, default=0.0)
    expiry_date = db.Column(db.DateTime, nullable=True)
    usage_limit = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def is_valid(self, cart_total=0):
        from datetime import datetime
        if not self.is_active: return False
        if self.expiry_date and self.expiry_date < datetime.now(): return False
        if self.usage_limit and self.used_count >= self.usage_limit: return False
        if cart_total < self.min_cart_value: return False
        return True

    def calculate_discount(self, total):
        if self.discount_type == DiscountType.PERCENTAGE:
            return (total * self.discount_value) / 100
        return min(self.discount_value, total)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )
    
    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Comma-separated image filenames
    images = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )
    
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    seller = db.relationship("User", backref="products")

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"

    def get_image_list(self):
        """Return list of image filenames"""
        if self.images:
            return [img.strip() for img in self.images.split(',') if img.strip()]
        return []

    def get_primary_image(self):
        """Return the first image or None"""
        images = self.get_image_list()
        return images[0] if images else None


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)  # e.g., "Size: XL", "Color: Blue"
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    product = db.relationship("Product", backref=db.backref("variants", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<ProductVariant id={self.id} sku={self.sku}>"


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("wishlist_items", cascade="all, delete-orphan"))
    product = db.relationship("Product")

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist_item'),)


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False
    )
    
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    added_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    user = db.relationship("User", backref="cart_items")
    variant = db.relationship("ProductVariant", backref="cart_entries")

    @property
    def product(self):
        """Helper to get parent product through variant"""
        return self.variant.product if self.variant else None

    def __repr__(self):
        return f"<Cart id={self.id} user_id={self.user_id} variant_id={self.variant_id}>"

    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.variant.price * self.quantity


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Links to external details
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True)
    
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)  # final_amount = total - discount
    
    status = db.Column(
        db.Enum(OrderStatus, name="order_status_enum", native_enum=False),
        default=OrderStatus.PENDING,
        nullable=False
    )
    
    shipping_address_text = db.Column(db.Text, nullable=False) # Snapshot of address at time of purchase
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship("User", backref="orders")
    address = db.relationship("Address")
    coupon = db.relationship("Coupon")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    payment = db.relationship("Payment", backref="order", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order id={self.id} user_id={self.user_id} status={self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    
    # Metadata for fallback
    product_name = db.Column(db.String(200), nullable=False)
    variant_name = db.Column(db.String(100), nullable=True)

    variant = db.relationship("ProductVariant")

    @property
    def product(self):
        """Helper to get parent product through variant"""
        return self.variant.product if self.variant else None

    def __repr__(self):
        return f"<OrderItem id={self.id} order_id={self.order_id}>"

    def get_subtotal(self):
        return self.price_at_purchase * self.quantity


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    stripe_session_id = db.Column(db.String(255), unique=True, nullable=True)
    stripe_payment_intent = db.Column(db.String(255), unique=True, nullable=True)
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="usd")
    status = db.Column(db.String(50), default="pending")  # pending, succeeded, failed
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class ReturnStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ReturnRequest(db.Model):
    __tablename__ = "return_requests"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(ReturnStatus, name="return_status_enum", native_enum=False),
        default=ReturnStatus.PENDING,
        nullable=False
    )
    admin_comment = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    order = db.relationship("Order", backref="return_requests")
    product = db.relationship("Product")


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False
    )
    
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )
    
    # Relationships
    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')
    
    # Unique constraint: one review per user per product
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),
    )
    
    def __repr__(self):
        return f'<Review user_id={self.user_id} product_id={self.product_id} rating={self.rating}>'
