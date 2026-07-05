#!/usr/bin/env python3
"""
Quick setup script for Prevento using SQLite (no MySQL required).
Creates local SQLite database, tables, and an admin user.
"""

import os
import sys

def create_env_file():
    """Create .env file with minimal Flask configuration"""
    print("🔧 Setting up configuration for SQLite...")
    
    # Create .env file content
    env_content = f"""# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_database_connection():
    """Test the SQLite database by executing a simple query"""
    print("\n🔍 Testing SQLite database...")
    
    try:
        from models import db
        from app import app
        
        with app.app_context():
            # Try to connect to database
            db.session.execute('SELECT 1')
            print("✅ SQLite database ready!")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def create_database_and_tables():
    """Create database and tables (SQLite) and seed admin user"""
    print("\n📊 Creating database and tables...")
    
    try:
        from models import db, User, Prediction
        from app import app
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create admin user
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin = User(
                    username='admin',
                    email='admin@prevento.com',
                    first_name='Admin',
                    last_name='User'
                )
                admin.set_password('admin123')
                
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
            
            return True
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Prevento SQLite Setup")
    print("=" * 40)
    
    # Step 1: Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Step 2: Test database
    if not test_database_connection():
        sys.exit(1)
    
    # Step 3: Create database and tables
    if not create_database_and_tables():
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Run: python app.py")
    print("2. Visit: http://localhost:5000")
    print("3. Login with admin/admin123")
    print("4. Register new users and test the system!")

if __name__ == "__main__":
    main()
