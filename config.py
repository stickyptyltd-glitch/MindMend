"""
Production Configuration for Mind Mend
Optimized for cPanel hosting on stickyplates.net
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'mind-mend-production-key-2025'
    
    # Database Configuration
    basedir = Path(__file__).parent.absolute()
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{basedir}/mind_mend.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_timeout': 20,
        'pool_size': 10,
        'max_overflow': 5
    }
    
    # AI Integration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Payment Processing
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    
    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    UPLOAD_FOLDER = 'attached_assets'
    
    # Security Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Production Domain
    SERVER_NAME = 'mind-mend.xyz'
    PREFERRED_URL_SCHEME = 'https'
    
    # Business Information
    COMPANY_NAME = 'Sticky Pty Ltd'
    COMPANY_EMAIL = 'sticky.pty.ltd@gmail.com'
    COMPANY_ADDRESS = 'Suite 329/98-100 Elizabeth Street, Melbourne, VIC, 3000'
    
    # Feature Flags
    ENABLE_AI_THERAPY = True
    ENABLE_PAYMENT_PROCESSING = True
    ENABLE_ADMIN_PANEL = True
    ENABLE_MEDIA_PACK = True
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/mind_mend.log'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    
    # Performance optimizations
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}