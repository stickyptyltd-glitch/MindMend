# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands
- **Setup**: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- **Alternative setup**: `pip install -e .` (installs from pyproject.toml)
- **Run locally**: `python app.py` (serves on localhost:5000)
- **Run with main entry**: `python main.py`
- **Run with Docker**: `docker-compose up -d --build`
- **Health check**: `curl http://localhost:5000/health`

### Code Quality Commands
- **Lint**: `ruff check .`
- **Format**: `black .`
- **Type check**: Uses ruff linting with Python 3.11+ target

### Testing Commands
- **Run tests**: `pytest -q` (configured in pytest.ini)
- **Test coverage**: `pytest --cov=. -q`
- **Test specific file**: `pytest tests/test_routes.py -v`
- **Payment system test**: `python test_payment_system.py`
- **Advanced systems test**: `python test_advanced_systems.py`

### Deployment Commands
- **Deploy to server**: `./auto_deploy_to_vultr.sh`
- **Quick fix deployment**: `./quick_fix_deployment.sh`
- **Update server**: `./update_mindmend.sh`
- **Deploy from Git**: `./deploy_from_git.sh`
- **Production deployment**: `./deploy_production.sh`
- **Setup admin access**: `python setup_admin_login.py`
- **Server setup from scratch**: `./server_complete_setup.sh`

## High-Level Architecture

### Core Application Structure
- **Entry Point**: `app.py` - Main Flask application with all routes and configurations
- **Database Models**: `models/database.py` - Core SQLAlchemy models (Session, BiometricData, Patient, etc.)
- **AI System**: Distributed across multiple modules:
  - `models/ai_manager.py` - Central AI orchestrator
  - `models/therapy_ai_integration.py` - Advanced therapy AI with ensemble models
  - `models/ai_model_manager.py` - Multiple AI model management
  - `models/treatment_recommender.py` - Personalized treatment planning
  - `models/enhancement_manager.py` - AI enhancement management
  - `models/research_manager.py` - Research and analytics capabilities

### Key Architecture Patterns
- **Modular AI Components**: Each AI feature (health checking, exercise generation, video analysis) is a separate module that can be imported and used independently
- **Blueprint Registration**: Core app registers multiple Flask blueprints (admin, counselor, payment, oauth, media)
- **Database Integration**: SQLAlchemy models with Flask-Login for user authentication
- **Real-time Features**: Socket.IO for live video analysis and biometric monitoring
- **Payment Integration**: Stripe payments with subscription management via `payment_integration.py`

### Critical Dependencies
- **AI Services**: OpenAI API for therapy responses (requires OPENAI_API_KEY)
- **Payment Processing**: Stripe (requires STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY)
- **Database**: Defaults to SQLite for development, PostgreSQL for production
- **Authentication**: Flask-Login with password hashing via Werkzeug
- **Real-time Communication**: Flask-SocketIO for WebSocket connections

### Environment Configuration
- **Development**: Uses SQLite database at `data/patients.db`
- **Production**: Requires environment variables:
  - `DATABASE_URL` for PostgreSQL connection
  - `OPENAI_API_KEY` for AI functionality
  - `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` for payments
  - `SESSION_SECRET` for Flask session security

### Advanced Features
- **Multi-modal AI**: Combines text, video, and biometric analysis
- **Crisis Detection**: Health checker scans for risk indicators
- **Personalized Treatment**: AI generates customized therapy exercises and plans
- **Biometric Integration**: Processes data from wearable devices
- **Video Analysis**: Real-time emotion and stress detection
- **Subscription System**: Tiered access with payment processing

### Admin Panel Access
- **URL**: http://67.219.102.9/admin (use IP to avoid SSL redirect)
- **Setup**: Run `python setup_admin_login.py` to create admin user
- **Credentials**: admin@mindmend.xyz / MindMend2024! (enterprise subscription tier)
- **Authentication**: Uses Patient table with enterprise subscription for admin access

### Important Notes
- **Security**: CSRF protection on auth forms, secure password hashing, environment-based secrets
- **Testing**: Uses pytest framework with fixtures in `tests/` directory
- **Deployment**: Multiple deployment scripts for different environments (Vultr, Docker, local)
- **Scalability**: Socket.IO and modular AI design support real-time features and horizontal scaling
- **Server**: Production runs on 67.219.102.9 (mindmend.xyz), use IP for admin access to avoid HTTPS redirect issues