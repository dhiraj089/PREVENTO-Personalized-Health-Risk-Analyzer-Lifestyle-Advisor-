#!/usr/bin/env python3
"""
Database setup script for Prevento application (SQLite).
Creates tables in the local SQLite database and seeds an admin user.
"""

import os
import sys
from config import Config
from models import db, User, Prediction
from app import app

def create_database():
    """Ensure SQLite database file exists (it will be created by SQLAlchemy)."""
    try:
        # Touch the database by creating tables via SQLAlchemy
        with app.app_context():
            db.create_all()
        print("✅ SQLite database ready!")
        return True
    except Exception as e:
        print(f"❌ Error ensuring SQLite database: {e}")
        return False

def create_tables():
    """Create all tables in the database"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create an admin user for testing"""
    try:
        with app.app_context():
            # Check if admin user already exists
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print("ℹ️  Admin user already exists!")
                return True
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@prevento.com',
                first_name='Admin',
                last_name='User'
            )
            admin.set_password('admin123')  # Change this in production!
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change the admin password in production!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Prevento SQLite Database...")
    print("=" * 50)
    
    # Step 1: Create database
    print("📊 Creating database...")
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    print("📋 Creating tables...")
    if not create_tables():
        sys.exit(1)
    
    # Step 3: Create admin user
    print("👤 Creating admin user...")
    if not create_admin_user():
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 SQLite database setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Run: python app.py")
    print("2. Visit: http://localhost:5000")
    print("3. Login with admin/admin123 (change password!)")

if __name__ == "__main__":
    main()


