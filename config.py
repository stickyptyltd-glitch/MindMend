"""
Production Configuration for Mind Mend
=====================================
Sticky Pty Ltd - Mental Health Platform
"""

import os
from datetime import timedelta

class Config:
    # Company Information - Sticky Pty Ltd
    COMPANY_NAME = "Sticky Pty Ltd"
    COMPANY_ABN = "12345678901"  # Replace with actual ABN
    COMPANY_ADDRESS = "Suite 123, Level 45, Sydney CBD, NSW 2000, Australia"
    COMPANY_PHONE = "+61 2 9000 0000"  # Replace with actual phone
    COMPANY_EMAIL = "support@mindmend.com.au"
    
    # App Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mindmend.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # SSL Configuration
    SSL_REDIRECT = os.environ.get('SSL_REDIRECT', 'True').lower() == 'true'
    
    # CORS and Security Headers
    CORS_ORIGINS = [
        'https://mindmend.com.au',
        'https://www.mindmend.com.au',
        'https://app.mindmend.com.au'
    ]
    
    # Payment Configuration
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
    GOOGLE_PAY_MERCHANT_ID = os.environ.get('GOOGLE_PAY_MERCHANT_ID')
    
    # AI Services
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Mobile App Configuration
    IOS_APP_ID = "au.com.sticky.mindmend"
    ANDROID_PACKAGE_NAME = "au.com.sticky.mindmend"
    
    # Domain Configuration
    DOMAIN = os.environ.get('DOMAIN', 'mindmend.com.au')
    API_BASE_URL = f"https://api.{DOMAIN}"
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/mindmend.log'
    
    # HIPAA Compliance Settings
    DATA_RETENTION_DAYS = 2555  # 7 years as per HIPAA requirements
    AUDIT_LOG_ENABLED = True
    ENCRYPTION_ENABLED = True
    
    # Counselor Dashboard Settings
    COUNSELOR_SESSION_TIMEOUT = 30  # minutes
    MAX_CONCURRENT_SESSIONS = 5
    
    # Monitoring and Analytics
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    
    # Production Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}