"""
Seed script to populate the database with sample data for the E-Commerce Platform.
This version includes support for Product Variants, Customer Addresses, and Coupons.
"""
from app import app
from db import db
from models import (
    User, Category, Product, ProductVariant, UserType, 
    SellerProfile, SellerStatus, Address, Coupon, DiscountType
)
import os
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.session.remove()
        db.drop_all()
        db.create_all()
        print("Recreated database schema")
        
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
        
        # Create sample users
        print("Creating sample users...")
        
        # Admin
        admin = User(username="admin", user_type=UserType.ADMIN)
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Customer
        customer = User(username="customer", user_type=UserType.CUSTOMER)
        customer.set_password("password")
        db.session.add(customer)
        
        # Sellers
        seller1 = User(username="seller1", user_type=UserType.SELLER)
        seller1.set_password("password")
        db.session.add(seller1)
        
        seller2 = User(username="seller2", user_type=UserType.SELLER)
        seller2.set_password("password")
        db.session.add(seller2)
        
        db.session.commit()
        
        # Create seller profiles
        print("Creating seller profiles...")
        sp1 = SellerProfile(
            user_id=seller1.id,
            display_name="Tech Store",
            company_name="Tech Store Inc",
            business_email="contact@techstore.com",
            business_phone="1234567890",
            status=SellerStatus.ACTIVE,
            is_verified=True
        )
        db.session.add(sp1)
        
        sp2 = SellerProfile(
            user_id=seller2.id,
            display_name="Fashion Hub",
            company_name="Fashion Hub LLC",
            business_email="contact@fashionhub.com",
            business_phone="0987654321",
            status=SellerStatus.ACTIVE,
            is_verified=True
        )
        db.session.add(sp2)
        db.session.commit()
        
        # Create Customer Address
        print("Creating customer address...")
        addr = Address(
            user_id=customer.id,
            name="Jonah Jay",
            address_line1="123 Main St",
            city="Colombo",
            state="Western",
            postal_code="00100",
            country="Sri Lanka",
            phone="1122334455",
            is_default=True
        )
        db.session.add(addr)
        
        # Create Coupon
        print("Creating sample coupon...")
        coupon = Coupon(
            code="SAVE10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=10.0,
            is_active=True,
            expiry_date=datetime.now() + timedelta(days=30),
            min_cart_value=100.0,
            usage_limit=100
        )
        db.session.add(coupon)
        db.session.commit()
        
        # Create Products and Variants
        print("Creating products and variants...")
        
        # 1. Smartphone (Electronics)
        p1 = Product(
            name="Pro Phone 15",
            description="The latest high-end smartphone with brilliant display.",
            price=999.99, # Base price for listing
            quantity=100, # Total quantity
            category_id=categories[0].id,
            seller_id=seller1.id
        )
        db.session.add(p1)
        db.session.flush()
        
        v1_1 = ProductVariant(product_id=p1.id, name="128GB - Midnight Black", price=999.99, stock=50, sku="PH15-128-BLK")
        v1_2 = ProductVariant(product_id=p1.id, name="256GB - Galactic Silver", price=1099.99, stock=50, sku="PH15-256-SLV")
        db.session.add_all([v1_1, v1_2])
        
        # 2. Cotton T-Shirt (Clothing)
        p2 = Product(
            name="Classic Organic T-Shirt",
            description="Premium organic cotton t-shirt for daily comfort.",
            price=29.99,
            quantity=200,
            category_id=categories[1].id,
            seller_id=seller2.id
        )
        db.session.add(p2)
        db.session.flush()
        
        for size in ["Small", "Medium", "Large", "XL"]:
            v = ProductVariant(product_id=p2.id, name=f"Size: {size} - White", price=29.99, stock=50, sku=f"TSH-ORG-WHT-{size[:1]}")
            db.session.add(v)
            
        # 3. Python Book (Books)
        p3 = Product(
            name="Advanced Web Apps with Flask",
            description="Learn how to build production-ready Flask applications.",
            price=45.00,
            quantity=50,
            category_id=categories[2].id,
            seller_id=seller1.id
        )
        db.session.add(p3)
        db.session.flush()
        
        v3_1 = ProductVariant(product_id=p3.id, name="Paperback", price=45.00, stock=30, sku="BOOK-FLASK-PB")
        v3_2 = ProductVariant(product_id=p3.id, name="Hardcover", price=65.00, stock=20, sku="BOOK-FLASK-HC")
        db.session.add_all([v3_1, v3_2])
        
        db.session.commit()
        print("Seeding completed successfully!")
        print("\nCredentials:")
        print("Admin: admin / admin123")
        print("Customer: customer / password")
        print("Sellers: seller1 / password, seller2 / password")

if __name__ == "__main__":
    seed_database()
