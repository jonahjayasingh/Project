#!/usr/bin/env python3
"""
Admin creation script for E-Commerce Platform
Usage: python create_admin.py
"""

from app import app, db
from models import User, UserType
from werkzeug.security import generate_password_hash
import sys

def create_admin():
    """Interactive script to create an admin user"""
    with app.app_context():
        print("=" * 50)
        print("E-Commerce Platform - Admin Creation")
        print("=" * 50)
        print()
        
        # Get admin details
        username = input("Enter admin username: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            sys.exit(1)
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Error: Username '{username}' already exists")
            sys.exit(1)
        
        password = input("Enter admin password: ").strip()
        if not password:
            print("Error: Password cannot be empty")
            sys.exit(1)
        
        if len(password) < 6:
            print("Error: Password must be at least 6 characters")
            sys.exit(1)
        
        # Create admin user
        try:
            admin = User(
                username=username,
                password=password, # User model has a setter that hashes
                user_type=UserType.ADMIN
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print()
            print("=" * 50)
            print("✅ Admin user created successfully!")
            print("=" * 50)
            print(f"Username: {username}")
            print(f"User Type: ADMIN")
            print()
            print("You can now login with these credentials.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    create_admin()
