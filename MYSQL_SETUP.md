# MySQL Database Setup for Prevento

This guide will help you set up MySQL database integration for your Prevento health prediction application with MySQL Workbench.

## Prerequisites

1. **MySQL Server** installed and running (MySQL 8.0+ recommended)
2. **MySQL Workbench** installed for database management
3. **Python 3.7+** installed
4. **pip** package manager

## Installation Steps

### 1. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Database

#### Step 1: Set up Environment Variables

1. Copy the example environment file:
```bash
# On Windows (PowerShell)
copy .env.example .env

# On Linux/Mac
cp .env.example .env
```

2. Edit the `.env` file with your MySQL credentials:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=prevento_db
```

#### Step 2: Create MySQL User (Optional but Recommended)

For better security, create a dedicated MySQL user:

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Run the following SQL commands:

```sql
-- Create a new user for Prevento
CREATE USER 'prevento_user'@'localhost' IDENTIFIED BY 'secure_password_here';

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON prevento_db.* TO 'prevento_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

Then update your `.env` file:
```env
MYSQL_USER=prevento_user
MYSQL_PASSWORD=secure_password_here
```

### 3. Set Up the Database

Run the MySQL database setup script:

```bash
python setup_mysql.py
```

This script will:
- Test MySQL server connection
- Create the MySQL database if it doesn't exist
- Create all necessary tables (users, predictions)
- Create an admin user and sample users for testing

### 4. Verify Database Connection

After running the setup script, verify your database connection:

1. Open MySQL Workbench
2. Connect to your MySQL server
3. You should see the `prevento_db` database
4. Expand it to see the tables:
   - `users` - User accounts and profiles
   - `predictions` - Health prediction history

### 5. Start the Application

```bash
python app.py
```

Visit `http://localhost:5000` to access your application.

## Database Schema

### Users Table (`users`)
| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY | Unique user identifier |
| `username` | VARCHAR(80) UNIQUE | Unique username |
| `email` | VARCHAR(120) UNIQUE | Optional email address |
| `password_hash` | VARCHAR(255) | Hashed password |
| `first_name` | VARCHAR(50) | Optional first name |
| `last_name` | VARCHAR(50) | Optional last name |
| `date_of_birth` | DATE | Optional date of birth |
| `phone` | VARCHAR(20) | Optional phone number |
| `created_at` | DATETIME | Account creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |
| `is_active` | BOOLEAN | Account status |

### Predictions Table (`predictions`)
| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY | Unique prediction identifier |
| `user_id` | INT FOREIGN KEY | Reference to users table |
| `symptoms` | JSON | Array of selected symptoms |
| `predicted_disease` | VARCHAR(100) | AI prediction result |
| `confidence_score` | FLOAT | Prediction confidence (0-1) |
| `precautions` | JSON | Array of precaution recommendations |
| `created_at` | DATETIME | Prediction timestamp |

## Features Added

### 🔐 Enhanced Authentication
- Secure password hashing with Werkzeug
- User registration with additional fields
- Session management
- Flash messages for user feedback

### 📊 User Management
- User profiles with optional personal information
- Account status management
- User prediction history

### 🎯 Prediction Storage
- All predictions are stored in the database
- User-specific prediction history
- Confidence scores and detailed results

### 🔗 MySQL Workbench Integration
- Full MySQL database support
- Easy database management through Workbench
- Proper indexing for performance
- UTF8MB4 character set for international support

## Default Accounts

After running the setup script, you can login with:

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`

### Sample User Accounts
- **Username:** `john_doe` | **Password:** `password123`
- **Username:** `jane_smith` | **Password:** `password123`

⚠️ **Important:** Change all default passwords in production!

## Troubleshooting

### Common Issues

1. **Connection Error**
   - Verify MySQL server is running
   - Check credentials in `.env` file
   - Ensure MySQL user has proper permissions
   - Test connection: `mysql -u your_user -p -h localhost`

2. **Database Creation Failed**
   - Check if MySQL user has CREATE DATABASE privileges
   - Verify database name doesn't already exist
   - Check MySQL server logs for errors

3. **Table Creation Failed**
   - Ensure database exists
   - Check for conflicting table names
   - Verify user has CREATE TABLE privileges

4. **PyMySQL Installation Issues**
   - Install dependencies: `pip install -r requirements.txt`
   - For Windows: `pip install --upgrade pip setuptools wheel`
   - For Linux: `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`

### Manual Database Creation

If the setup script fails, you can manually create the database in MySQL Workbench:

```sql
-- Create database
CREATE DATABASE prevento_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE prevento_db;

-- Verify creation
SHOW DATABASES;
```

Then run the application and visit `/init-db` to create tables.

### Testing Database Connection

You can test your database connection with this simple Python script:

```python
import pymysql
from config import Config

try:
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        charset='utf8mb4'
    )
    print("✅ Database connection successful!")
    connection.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## Security Notes

1. **Change Default Passwords**
   - Update admin password immediately
   - Use strong secret key in production
   - Consider using environment variables for all secrets

2. **Environment Variables**
   - Never commit `.env` file to version control
   - Use environment variables in production
   - Add `.env` to your `.gitignore` file

3. **Database Security**
   - Use dedicated MySQL user with minimal privileges
   - Enable SSL connections in production
   - Regular database backups
   - Restrict MySQL user to specific database only

4. **Application Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Regular security updates
   - Input validation and sanitization

## MySQL Workbench Integration

### Connecting to Your Database

1. Open MySQL Workbench
2. Create a new connection:
   - **Connection Name:** Prevento Local
   - **Hostname:** localhost
   - **Port:** 3306
   - **Username:** your_mysql_username
   - **Password:** your_mysql_password
3. Click "Test Connection" to verify
4. Save and connect

### Managing Data

Once connected, you can:
- View and edit user data in the `users` table
- Monitor prediction history in the `predictions` table
- Run custom queries for analytics
- Export data for backup purposes

### Useful Queries

```sql
-- View all users
SELECT id, username, email, first_name, last_name, created_at, is_active 
FROM users;

-- View user predictions
SELECT u.username, p.predicted_disease, p.confidence_score, p.created_at
FROM predictions p
JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC;

-- Count predictions per user
SELECT u.username, COUNT(p.id) as prediction_count
FROM users u
LEFT JOIN predictions p ON u.id = p.user_id
GROUP BY u.id, u.username;

-- Most common diseases
SELECT predicted_disease, COUNT(*) as frequency
FROM predictions
GROUP BY predicted_disease
ORDER BY frequency DESC;
```

## Production Deployment

For production deployment:

1. **Server Setup**
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Set up proper environment variables
   - Use a production MySQL server

2. **Security**
   - Enable SSL/HTTPS
   - Set up proper firewall rules
   - Use strong passwords and keys

3. **Monitoring**
   - Set up database backups
   - Configure proper logging
   - Monitor application performance

4. **Database Optimization**
   - Set up proper indexing
   - Configure MySQL for production
   - Regular maintenance and optimization

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET /register` - Registration form
- `POST /register` - Create new user
- `GET /login` - Login form
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /welcome` - User dashboard

### Health Prediction
- `GET /survey` - Symptom survey form
- `POST /predict` - Get health prediction
- `GET /my-reports` - View prediction history
- `GET /report-preview` - Preview health report
- `GET /download-report` - Download PDF report

### Database Management
- `GET /init-db` - Initialize database tables (development only)
- `GET /api/dataset-accuracy` - Get model accuracy metrics

## Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
copy .env.example .env
# Edit .env with your MySQL credentials

# 3. Set up database
python setup_mysql.py

# 4. Run application
python app.py

# 5. Access application
# Visit: http://localhost:5000
# Login: admin / admin123
```

## Support

If you encounter any issues:

1. **Check Console Output**
   - Look for error messages in terminal
   - Check Flask application logs

2. **Verify MySQL Status**
   - Ensure MySQL server is running
   - Test connection with MySQL Workbench

3. **Database Permissions**
   - Verify user has CREATE, INSERT, UPDATE, SELECT privileges
   - Check database and table permissions

4. **Configuration Files**
   - Review `.env` file settings
   - Check `config.py` for proper configuration

5. **Dependencies**
   - Ensure all Python packages are installed
   - Check for version compatibility issues

For additional help, check the troubleshooting section above or review the application logs.

Happy coding! 🚀


