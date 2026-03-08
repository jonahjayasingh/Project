# 🛍️ Advanced E-Commerce Ecosystem

A high-performance, full-featured Flask-based e-commerce platform engineered for production scale. This ecosystem features a robust multi-role architecture, integrated Stripe payments, dynamic marketing tools, and a premium Glassmorphic UI/UX.

---

## 🌟 Core Features

### 👤 Multi-Role Architecture

- **Customers**: Product discovery, variant selection, cart, wishlist, address management, and order tracking.
- **Sellers**: Dedicated dashboard, product/variant management, order fulfillment, and sales analytics.
- **Admins**: Platform-wide oversight of users, products, categories, and payment auditing.

### 🍱 Advanced Product Engine

- **Variant Support**: Multi-variant architecture allowing sellers to define different sizes, colors, or specifications with independent stock and pricing.
- **Inventory Control**: Real-time stock decrementing upon successful payment and restock upon returns.
- **Categorization**: Multi-level category system with slug-based SEO-friendly URLs.

### 💳 Financial & Payments

- **Stripe Checkout**: PCI-compliant checkout session integration.
- **Webhooks**: Automated order state transitions (Paid → Processing) via secure Stripe webhook listeners.
- **Transaction Auditing**: Persistent payment records linked to Stripe Session and Payment Intent IDs.

### 📦 Customer Experience

- **Personalization**: Multi-address book management with default shipping address settings.
- **Interest Tracking**: Persistent wishlist system for saving products.
- **Reviews & Ratings**: Verified purchase review system with star ratings and comments.
- **Returns Lifecycle**: Built-in return request workflow for delivered orders.

### 📢 Marketing & Growth

- **Dynamic Coupons**: Coupon engine supporting percentage-based or fixed discounts with minimum purchase requirements.
- **Public Storefronts**: Seller-specific pages showcasing their entire catalog and trust metrics.

---

## 🛠️ Technology Stack

| Layer        | Technologies                                              |
| :----------- | :-------------------------------------------------------- |
| **Backend**  | Python 3.x, Flask, SQLAlchemy (ORM)                       |
| **Payment**  | Stripe API Express                                        |
| **Security** | Flask-WTF (CSRF), Flask-Limiter (Rate Limiting)           |
| **Database** | SQLite (Production-ready schema)                          |
| **Frontend** | Jinja2, Vanilla CSS3 (Custom Glassmorphism Design System) |
| **Tooling**  | `uv` package manager, `python-dotenv`                     |

---

## 📂 Modular Architecture

```text
e-com/
├── app.py              # App entry point & Middlewares
├── models.py           # Unified SQLAlchemy Schema (20+ Models)
├── seed.py             # Industrial-grade database population script
├── routes/             # Production Blueprints
│   ├── auth.py         # RBAC Authentication logic
│   ├── customer.py     # Cart, Wishlist, Address, and Profile management
│   ├── seller.py       # Inventory and Dashboard analytics
│   ├── payment.py      # Stripe Checkout & Webhook handlers
│   ├── admin.py        # System-wide management
│   └── product.py      # Catalog discovery & Variant logic
├── templates/          # Responsive Jinja2 Templates
└── static/             # Assets (CSS/JS/Uploads)
```

---

## 🚀 Setup & Execution

### 1. Environment Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secure_random_key
DATABASE_URL=sqlite:///ecommerce.db
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 2. Dependency Installation

Using standard `pip`:

```bash
pip install -r requirements.txt
```

Or using `uv` (recommended):

```bash
uv sync
```

### 3. Database Initialization

Reset and seed the database with professional sample data:

```bash
python seed.py
```

### 4. Local Stripe Testing

To handle real-time payment fulfillments:

1. **Start Stripe CLI**: `stripe listen --forward-to localhost:5001/stripe-webhook`
2. **Copy the Webhook Secret**: Update `STRIPE_WEBHOOK_SECRET` in `.env`.

### 5. Launch

```bash
python app.py
```

Access the application at: `http://localhost:5001`

---

## 🛡️ Security & Performance

- **CSRF Protection**: All POST/PUT requests are validated via Flask-WTF tokens.
- **Rate Limiting**: Critical endpoints (login, API calls) are protected against brute force.
- **Eager Loading**: Database queries utilize `joinedload` and `selectinload` where necessary to prevent N+1 performance issues.
- **Data Integrity**: Cascading deletes and soft-null foreign keys ensure database consistency.

---

Built for Scalability and Excellence.
