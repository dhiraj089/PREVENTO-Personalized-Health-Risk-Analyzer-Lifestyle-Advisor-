#!/usr/bin/env python3
"""
MySQL Database setup script for Prevento application.
Creates MySQL database, tables, and seeds an admin user.
"""

import os
import sys
import pymysql
from config import Config
from models import db, User, Prediction
from app import app

def test_mysql_connection():
    """Test MySQL server connection"""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        connection.close()
        print("✅ MySQL server connection successful!")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your credentials in .env file")
        print("3. Verify MySQL user has proper permissions")
        return False

def create_database():
    """Create MySQL database if it doesn't exist"""
    try:
        # Connect without specifying database
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{Config.MYSQL_DATABASE}' created/verified successfully!")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all tables in the MySQL database"""
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

def create_sample_users():
    """Create sample users for testing"""
    try:
        with app.app_context():
            sample_users = [
                {
                    'username': 'john_doe',
                    'email': 'john@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'password': 'password123'
                },
                {
                    'username': 'jane_smith',
                    'email': 'jane@example.com',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'password': 'password123'
                }
            ]
            
            created_count = 0
            for user_data in sample_users:
                # Check if user already exists
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name']
                    )
                    user.set_password(user_data['password'])
                    
                    db.session.add(user)
                    created_count += 1
            
            if created_count > 0:
                db.session.commit()
                print(f"✅ Created {created_count} sample users!")
            else:
                print("ℹ️  Sample users already exist!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample users: {e}")
        return False

def show_database_info():
    """Display database connection information"""
    print("\n📊 Database Information:")
    print(f"   Host: {Config.MYSQL_HOST}")
    print(f"   Port: {Config.MYSQL_PORT}")
    print(f"   Database: {Config.MYSQL_DATABASE}")
    print(f"   User: {Config.MYSQL_USER}")
    print(f"   Connection String: {Config.SQLALCHEMY_DATABASE_URI}")

def main():
    """Main setup function"""
    print("🚀 Setting up Prevento MySQL Database...")
    print("=" * 60)
    
    # Show database info
    show_database_info()
    print()
    
    # Step 1: Test MySQL connection
    print("🔌 Testing MySQL connection...")
    if not test_mysql_connection():
        sys.exit(1)
    
    # Step 2: Create database
    print("📊 Creating database...")
    if not create_database():
        sys.exit(1)
    
    # Step 3: Create tables
    print("📋 Creating tables...")
    if not create_tables():
        sys.exit(1)
    
    # Step 4: Create admin user
    print("👤 Creating admin user...")
    if not create_admin_user():
        sys.exit(1)
    
    # Step 5: Create sample users (optional)
    print("👥 Creating sample users...")
    create_sample_users()
    
    print("=" * 60)
    print("🎉 MySQL database setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run: python app.py")
    print("3. Visit: http://localhost:5000")
    print("4. Login with admin/admin123 (change password!)")
    print("\n🔐 Test Users:")
    print("   admin / admin123")
    print("   john_doe / password123")
    print("   jane_smith / password123")

if __name__ == "__main__":
    main()
