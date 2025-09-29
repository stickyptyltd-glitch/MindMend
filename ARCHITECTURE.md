# Architecture Overview

This document summarizes how MindMend is structured, how components interact, and where to extend safely.

## High-Level Components
- Web App: Flask + Socket.IO (`app.py`) registered via `main.py` for local dev.
- Blueprints: Modular feature areas — Admin (`admin_panel.py`), Counselor (`counselor_dashboard.py`), Payments (`payment_integration.py`), OAuth (`oauth_system.py`), Media Pack (`media_pack.py`), Mobile (`mobile_app.py`), Emotion/Crisis APIs.
- Models/Domain: `models/` contains AI orchestration, analytics, persistence helpers, and domain services (e.g., `ai_manager.py`, `health_checker.py`, `therapy_*`).
- UI: Jinja templates in `templates/`, assets in `static/`.
- Persistence: SQLAlchemy (`models/database.py`). Dev uses SQLite (`data/`); Docker uses Postgres/Redis.
- Ops: `docker-compose.yml`, `docker/` (Nginx, Postgres, init SQL, start scripts), `scripts/` for deploy and monitoring.

## Data Flow
1. Request hits Flask route or blueprint.
2. Handlers call domain services in `models/` (e.g., AIManager, ExerciseGenerator).
3. SQLAlchemy persists/fetches data via `models/database.py`.
4. Real-time events use Socket.IO where applicable.
5. Payments handled in `payment_integration.py` (Stripe/PayPal); OAuth handled in `oauth_system.py`.

## External Services
- OpenAI (chat/vision) via `models/ai_manager.py`, `video_analyzer.py`.
- Stripe/PayPal integrations in `payment_integration.py`.
- Optional Ollama server via Docker Compose for local LLMs.

## Environments
- Local: `python main.py` (SQLite, debug); `.env.template` → `.env.local`.
- Docker: `docker-compose up -d --build` (Postgres, Redis, Nginx, Ollama, Celery) with `.env.production`.

## Extension Points
- Routes: Add to existing blueprints or create a new one and register in `app.py`.
- Domain Logic: Add services under `models/` and import into handlers.
- DB: Define models in `models/database.py`; run `db.create_all()` occurs at startup in `app.py`.
- Frontend: Add Jinja templates under `templates/` and static assets under `static/`.

## Observability & Health
- Health checks exposed via Nginx/Compose and application endpoints (see ROUTES.md).
- Monitoring utilities: `scripts/monitor.sh`, `monitoring.py`.

## Security Notes
- Never commit secrets. Configure `SESSION_SECRET`, Stripe keys, `OPENAI_API_KEY`, `DATABASE_URL`.
- `security_enhancements.py` and login flows in `app.py`/`admin_*` enforce auth; update carefully.

