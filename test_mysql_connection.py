#!/usr/bin/env python3
"""
Simple script to test MySQL database connection for Prevento application.
Run this script to verify your MySQL setup before starting the main application.
"""

import os
import sys
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test MySQL database connection"""
    print("🔌 Testing MySQL Database Connection...")
    print("=" * 50)
    
    # Get connection parameters from environment
    host = os.environ.get('MYSQL_HOST', 'localhost')
    port = int(os.environ.get('MYSQL_PORT', 3306))
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DATABASE', 'prevento_db')
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    print(f"Password: {'*' * len(password) if password else '(empty)'}")
    print()
    
    try:
        # Test connection without specifying database first
        print("1. Testing MySQL server connection...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        print("   ✅ MySQL server connection successful!")
        connection.close()
        
        # Test connection with database
        print("2. Testing database connection...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        print("   ✅ Database connection successful!")
        
        # Test basic query
        print("3. Testing database query...")
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   ✅ MySQL version: {version[0]}")
        
        # Check if tables exist
        print("4. Checking for Prevento tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        if 'users' in table_names and 'predictions' in table_names:
            print("   ✅ Prevento tables found!")
            
            # Count records in users table
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   📊 Users in database: {user_count}")
            
            # Count records in predictions table
            cursor.execute("SELECT COUNT(*) FROM predictions")
            prediction_count = cursor.fetchone()[0]
            print(f"   📊 Predictions in database: {prediction_count}")
            
        else:
            print("   ⚠️  Prevento tables not found!")
            print("   💡 Run 'python setup_mysql.py' to create tables")
        
        cursor.close()
        connection.close()
        
        print()
        print("🎉 All tests passed! Your MySQL setup is working correctly.")
        print("🚀 You can now run 'python app.py' to start the application.")
        
        return True
        
    except pymysql.Error as e:
        print(f"   ❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return False

def show_help():
    """Show help information"""
    print("MySQL Connection Test for Prevento")
    print("=" * 40)
    print()
    print("This script tests your MySQL database connection.")
    print("Make sure you have:")
    print("1. MySQL server running")
    print("2. .env file with correct credentials")
    print("3. Database and tables created (run setup_mysql.py)")
    print()
    print("Usage:")
    print("  python test_mysql_connection.py")
    print()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("💡 Copy .env.example to .env and configure your MySQL credentials")
        print("   copy .env.example .env")
        sys.exit(1)
    
    success = test_connection()
    
    if not success:
        print()
        print("🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your credentials in .env file")
        print("3. Verify MySQL user has proper permissions")
        print("4. Run 'python setup_mysql.py' to create database and tables")
        sys.exit(1)

if __name__ == "__main__":
    main()
