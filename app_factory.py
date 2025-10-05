
import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
socketio = SocketIO()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "your-secret-key-here")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data/patients.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Login manager setup
    login_manager.login_view = 'auth.login'

    from models.database import Patient, Admin

    @login_manager.user_loader
    def load_user(user_id):
        # First, try to load as an admin
        admin = Admin.query.get(int(user_id))
        if admin:
            return admin
        # If not an admin, try to load as a patient
        return Patient.query.get(int(user_id))

    # Register blueprints
    with app.app_context():
        from general import general_bp
        app.register_blueprint(general_bp)

        from auth import auth_bp
        app.register_blueprint(auth_bp)

        from admin_auth_routes import admin_auth_bp
        app.register_blueprint(admin_auth_bp)

        from video import video_bp
        app.register_blueprint(video_bp)

        from biometric import biometric_bp
        app.register_blueprint(biometric_bp)

        from crisis import crisis_bp
        app.register_blueprint(crisis_bp)

        from emotion import emotion_bp
        app.register_blueprint(emotion_bp)

        from avatar import avatar_bp
        app.register_blueprint(avatar_bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return "<h1>Page Not Found</h1>", 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return "<h1>Internal Server Error</h1>", 500

    return app
