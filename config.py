import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


def _mysql_is_available(host, port, user, password, database):
    if not host or not user:
        return False

    try:
        import pymysql

        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=1,
        )
        connection.close()
        return True
    except Exception:
        return False


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'

    DATABASE_URL = os.environ.get('DATABASE_URL')
    USE_MYSQL = os.environ.get('USE_MYSQL', '').strip().lower() in {'1', 'true', 'yes', 'on'}

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20,
        }
    elif USE_MYSQL:
        # Database Configuration - MySQL
        MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
        MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
        MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '@dhiraj859112'
        MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'prevento_db'

        if _mysql_is_available(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE):
            # URL-encode credentials to support special characters like '@', ':', '#', etc.
            _encoded_user = quote_plus(MYSQL_USER)
            _encoded_password = quote_plus(MYSQL_PASSWORD)
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{_encoded_user}:{_encoded_password}@"
                f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
            )
            SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_size': 10,
                'max_overflow': 20,
            }
        else:
            print(f"MySQL server at {MYSQL_HOST}:{MYSQL_PORT} is not reachable. Falling back to SQLite.")
            basedir = os.path.abspath(os.path.dirname(__file__))
            instance_dir = os.path.join(basedir, 'instance')
            os.makedirs(instance_dir, exist_ok=True)
            sqlite_path = os.path.join(instance_dir, 'prevento.db')
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{sqlite_path}'
            SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        instance_dir = os.path.join(basedir, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        sqlite_path = os.path.join(instance_dir, 'prevento.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{sqlite_path}'
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False


