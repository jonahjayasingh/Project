"""
Seed script to populate the database with sample data
"""
from app import app
from db import db
from models import User, Category, Product, UserType
import os

def seed_database():
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create categories
        print("Creating categories...")
        categories = [
            Category(name="Electronics", slug="electronics", description="Gadgets and electronic devices"),
            Category(name="Clothing", slug="clothing", description="Fashion and apparel"),
            Category(name="Books", slug="books", description="Books and literature"),
            Category(name="Home & Garden", slug="home-garden", description="Home improvement and gardening"),
            Category(name="Sports", slug="sports", description="Sports and outdoor equipment"),
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print(f"Created {len(categories)} categories")
        
        # Create sample users
        print("Creating sample users...")
        
        # Admin user
        admin = User(username="admin", user_type=UserType.ADMIN)
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Customer user
        customer = User(username="customer", user_type=UserType.CUSTOMER)
        customer.set_password("password")
        db.session.add(customer)
        
        # Seller users
        seller1 = User(username="seller1", user_type=UserType.SELLER)
        seller1.set_password("password")
        db.session.add(seller1)
        
        seller2 = User(username="seller2", user_type=UserType.SELLER)
        seller2.set_password("password")
        db.session.add(seller2)
        
        db.session.commit()
        print("Created 4 sample users (admin, customer, seller1, seller2)")
        
        # Create seller profiles
        print("Creating seller profiles...")
        from models import SellerProfile, SellerStatus
        
        seller_profile1 = SellerProfile(
            user_id=seller1.id,
            display_name="Tech Store",
            company_name="Tech Store Inc",
            description="Your one-stop shop for electronics",
            business_email="contact@techstore.com",
            status=SellerStatus.ACTIVE
        )
        db.session.add(seller_profile1)
        
        seller_profile2 = SellerProfile(
            user_id=seller2.id,
            display_name="Fashion Hub",
            company_name="Fashion Hub LLC",
            description="Latest trends in fashion",
            business_email="contact@fashionhub.com",
            status=SellerStatus.ACTIVE
        )
        db.session.add(seller_profile2)
        
        db.session.commit()
        print("Created 2 seller profiles")
        
        # Create sample products
        print("Creating sample products...")
        
        products = [
            # Electronics by seller1
            Product(
                name="Wireless Headphones",
                description="Premium noise-canceling wireless headphones with 30-hour battery life",
                price=199.99,
                quantity=50,
                category_id=categories[0].id,
                seller_id=seller1.id
            ),
            Product(
                name="Smart Watch",
                description="Fitness tracker with heart rate monitor and GPS",
                price=299.99,
                quantity=30,
                category_id=categories[0].id,
                seller_id=seller1.id
            ),
            Product(
                name="Laptop Stand",
                description="Adjustable aluminum laptop stand for better ergonomics",
                price=49.99,
                quantity=100,
                category_id=categories[0].id,
                seller_id=seller1.id
            ),
            
            # Clothing by seller2
            Product(
                name="Cotton T-Shirt",
                description="Comfortable 100% cotton t-shirt in various colors",
                price=24.99,
                quantity=200,
                category_id=categories[1].id,
                seller_id=seller2.id
            ),
            Product(
                name="Denim Jeans",
                description="Classic fit denim jeans with stretch fabric",
                price=59.99,
                quantity=80,
                category_id=categories[1].id,
                seller_id=seller2.id
            ),
            Product(
                name="Winter Jacket",
                description="Warm winter jacket with water-resistant outer layer",
                price=129.99,
                quantity=40,
                category_id=categories[1].id,
                seller_id=seller2.id
            ),
            
            # Books by seller1
            Product(
                name="Python Programming Guide",
                description="Comprehensive guide to Python programming for beginners",
                price=39.99,
                quantity=60,
                category_id=categories[2].id,
                seller_id=seller1.id
            ),
            Product(
                name="Web Development Handbook",
                description="Modern web development techniques and best practices",
                price=44.99,
                quantity=45,
                category_id=categories[2].id,
                seller_id=seller1.id
            ),
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        print(f"Created {len(products)} sample products")
        
        print("\nSample data created successfully!")
        print("\nSample credentials:")
        print("Admin - username: admin, password: admin123")
        print("Customer - username: customer, password: password")
        print("Seller 1 - username: seller1, password: password")
        print("Seller 2 - username: seller2, password: password")

if __name__ == "__main__":
    seed_database()
