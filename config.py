import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///aura.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Password Security
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_EXPIRY_DAYS = 90
    
    # Rate Limiting - Fixed to use proper storage
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "redis://localhost:6379"  # Use Redis in production
    RATELIMIT_STORAGE_OPTIONS = {
        'connection_pool': None,
        'socket_connect_timeout': 5,
        'socket_timeout': 5,
    }
    
    # Account Security
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION = timedelta(minutes=30)
    MAX_ACCOUNT_LOCKOUT_ATTEMPTS = 15
    ACCOUNT_LOCKOUT_24H = timedelta(hours=24)
    
    # Token Expiry
    EMAIL_VERIFICATION_EXPIRY = timedelta(hours=24)
    PASSWORD_RESET_EXPIRY = timedelta(hours=1)
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https:;"
    }
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/aura.log'
    
    # Email Configuration (for password reset and verification)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Two-Factor Authentication
    TWO_FACTOR_ENABLED = True
    TOTP_ISSUER = 'Aura'
    
    # IP Whitelist/Blacklist (for additional security)
    ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '').split(',') if os.environ.get('ALLOWED_IPS') else []
    BLOCKED_IPS = os.environ.get('BLOCKED_IPS', '').split(',') if os.environ.get('BLOCKED_IPS') else []
    
    # Suspicious Activity Detection
    SUSPICIOUS_ACTIVITY_THRESHOLD = 10
    SUSPICIOUS_IP_THRESHOLD = 5


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    
    # Use memory storage for development (no Redis required)
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STORAGE_OPTIONS = {}


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Enhanced security for production
    WTF_CSRF_TIME_LIMIT = 1800  # 30 minutes
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Stricter rate limiting
    RATELIMIT_DEFAULT = "100 per day"
    
    # Shorter token expiry
    EMAIL_VERIFICATION_EXPIRY = timedelta(hours=12)
    PASSWORD_RESET_EXPIRY = timedelta(minutes=30)


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    
    # Use memory storage for testing
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STORAGE_OPTIONS = {}


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': TestingConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
