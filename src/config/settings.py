"""Configuration classes for different environments."""
import os
from pathlib import Path

# Base directory
basedir = Path(__file__).parent.parent.parent


class BaseConfig:
    """Base configuration with safe defaults."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Flask-WTF CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Flask-Login
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'src', 'static', 'uploads', 'resources')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB per file
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


class DevConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    # Use instance folder for database (Flask standard)
    instance_path = basedir / 'instance'
    instance_path.mkdir(exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        f'sqlite:///{instance_path / "app.db"}'


class TestConfig(BaseConfig):
    """Test configuration with in-memory database."""
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProdConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or ''
    SECRET_KEY = os.environ.get('SECRET_KEY') or ''
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    REMEMBER_COOKIE_SECURE = True  # Requires HTTPS
    
    # Note: Validation should be done at runtime, not at class definition
    # Flask will use this config only when FLASK_ENV=production

