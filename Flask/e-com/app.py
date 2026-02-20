import os
from dotenv import load_dotenv
from flask import Flask, render_template, session
from routes.auth import routes as auth_routes
from routes.seller import routes as seller_routes
from routes.product import routes as product_routes
from routes.customer import routes as customer_routes
from routes.admin import routes as admin_routes
from models import db, User

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

@app.route('/')
def index():
    from models import Product, Category
    products = Product.query.filter(Product.quantity > 0).order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template('home.html', products=products, categories=categories)


app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(seller_routes, url_prefix='/seller')
app.register_blueprint(product_routes, url_prefix='/')
app.register_blueprint(customer_routes, url_prefix='/')
app.register_blueprint(admin_routes, url_prefix='/admin')


if __name__ == '__main__':
    with app.app_context():
        from models import (
            User, Profile, SellerProfile, Category, Product,
            Cart, Order, OrderItem
        )
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5001)
