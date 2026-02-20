# Vibrant E-Commerce Platform

A comprehensive, full-featured Flask-based e-commerce ecosystem designed with a focus on usability, security, and a robust multi-role architecture. This platform caters to Customers, Sellers, and Administrators, providing a seamless shopping experience and powerful management tools.

---

## 🚀 Key Features

### 👤 Customer Experience
- **Product Discovery**: Browse products by categories, search for specific items, and filter by price.
- **Shopping Cart**: Real-time cart management with stock validation.
- **Secure Checkout**: Streamlined checkout process with shipping address management.
- **Order Tracking**: Comprehensive order history with detailed status updates (Pending, Processing, Shipped, Delivered, Cancelled).
- **User Profiles**: Manage personal information including full name, phone number, and primary address.
- **Reviews & Ratings**: Share feedback on purchased products with a 1-5 star rating system and comments.
- **Dynamic Homepage**: Highlighting the latest products and available categories.

### 🏪 Seller Dashboard
- **Business Analytics**: High-level metrics showing total sales, revenue, and inventory status.
- **Inventory Management**: Full CRUD operations for products including multiple image uploads.
- **Order Fulfillment**: Track and update order statuses for assigned products.
- **Sales Reports**: Interactive data visualization using Chart.js, featuring:
  - Total revenue and product sales.
  - Sales trends over the last 30 days.
  - Top-selling products.
  - Order status distribution.
- **Product Policy**: Sellers are automatically restricted from purchasing their own products to maintain platform integrity.

### 🛡️ Administrative Control
- **User Moderation**: Manage user accounts, including the ability to activate or suspend seller profiles.
- **Category Management**: Create and organize product categories with custom slugs and descriptions.
- **Platform Monitoring**: Oversight of all platform orders and business performance.
- **CLI Tools**: Built-in script for secure administrative user creation.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, [Flask](https://flask.palletsprojects.com/)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) (ORM) with SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: Jinja2 Templates, Modern CSS3 (featuring Glassmorphism, Gradients, and Responsive Layouts), Vanilla JavaScript
- **Visualization**: [Chart.js](https://www.chartjs.org/) for seller analytics
- **Security**: Werkzeug password hashing, role-based access control (RBAC), and session-based authentication.
- **Environment**: `python-dotenv` for configuration management.

---

## 📂 Project Structure

```text
e-com/
├── app.py              # Application entry point & configuration
├── models.py           # Database models (User, Product, Order, etc.)
├── routes/             # Blueprint-based modular routing
│   ├── admin.py        # Admin panel logic
│   ├── auth.py         # Login, Registration, Logout
│   ├── customer.py     # Cart, Checkout, Profile, Orders
│   ├── product.py      # Product listings & detail views
│   └── seller.py       # Seller dashboard & management
├── static/             # Assets (CSS, JS, Images, Uploads)
├── templates/          # HTML templates (Jinja2)
├── utils/              # Helper functions & decorators (e.g., @login_required)
├── create_admin.py     # CLI tool for creating admin users
├── seed.py             # Script to populate sample data
└── requirements.txt    # Project dependencies
```

---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd e-com
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///ecommerce.db
   ```

5. **Initialize Database and Seed Data** (Optional but recommended)
   ```bash
   python seed.py
   ```
   *This will create the database schema and populate it with sample categories, products, and users (Admin, Seller, Customer).*

6. **Create an Admin User**
   ```bash
   python create_admin.py
   ```

7. **Run the Application**
   ```bash
   python app.py
   ```
   Access the platform at `http://localhost:5001`

---

## 🧪 Sample Credentials (from `seed.py`)

- **Admin**: `admin` / `admin123`
- **Seller**: `seller1` / `password`
- **Customer**: `customer` / `password`

---

## 🔮 Future Roadmap

- [ ] **Payment Integration**: Integration with Stripe/Razorpay for actual transactions.
- [ ] **Email Notifications**: Automated emails for order confirmations and status updates.
- [ ] **Enhanced Search**: Implementation of full-text search (ElasticSearch or similar).
- [ ] **Multi-Currency Support**: Dynamic currency switching and localization.
- [ ] **Mobile App**: API preparation for mobile integration.

---

Built for excellence in modern e-commerce.
