# Quick MySQL Setup Guide for Prevento

## 🚀 Quick Start (5 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env file with your MySQL credentials:
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=your_mysql_password
# MYSQL_DATABASE=prevento_db
```

### Step 3: Set Up MySQL Database
```bash
python setup_mysql.py
```

### Step 4: Start Application
```bash
python app.py
```

### Step 5: Access Application
- Visit: http://localhost:5000
- Login with: admin / admin123

## 🔗 Connect to MySQL Workbench

1. Open MySQL Workbench
2. Create new connection:
   - **Name:** Prevento Local
   - **Host:** localhost
   - **Port:** 3306
   - **Username:** root (or your MySQL user)
   - **Password:** your_mysql_password
3. Test connection and connect
4. You'll see `prevento_db` database with `users` and `predictions` tables

## 📊 Database Tables Created

### Users Table
- Stores user accounts with username, email, password
- Includes profile information (first name, last name, etc.)
- Has authentication and session management

### Predictions Table  
- Stores health prediction results
- Links to users via foreign key
- Contains symptoms, predicted disease, confidence scores

## 🔐 Default Login Credentials

- **Admin:** admin / admin123
- **Test User 1:** john_doe / password123  
- **Test User 2:** jane_smith / password123

## ⚠️ Important Notes

1. **Change default passwords** before production use
2. **Never commit .env file** to version control
3. **Backup your database** regularly
4. **Use strong MySQL passwords**

## 🆘 Need Help?

Check the full `MYSQL_SETUP.md` file for detailed troubleshooting and advanced configuration options.
