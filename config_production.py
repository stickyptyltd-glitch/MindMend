import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production_secret_key_change_me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/mindmend_production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Advanced Features Configuration
    ENABLE_PREDICTIVE_ANALYTICS = True
    ENABLE_CRISIS_INTERVENTION = True
    ENABLE_IOT_INTEGRATION = True
    ENABLE_VR_THERAPY = True
    ENABLE_SOCIAL_CONNECTIONS = True

    # Security Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # Performance Settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files

    # External APIs (configure in environment variables)
    CRISIS_HOTLINE_API = os.environ.get('CRISIS_HOTLINE_API')
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/mindmend/app.log'
