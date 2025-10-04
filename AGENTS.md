# Repository Guidelines

This guide helps you contribute effectively to MindMend (Flask + Socket.IO).
Follow the conventions below to keep changes consistent and easy to review.

## Project Structure & Module Organization
- Root app: `MindMend/` (Flask app + Socket.IO).
- Entry point: `MindMend/main.py` (runs server). Core app: `MindMend/app.py`.
- Views/assets: `MindMend/templates/`, `MindMend/static/`.
- Domain logic: `MindMend/models/` (AI, DB, integrations).
- Ops: `MindMend/docker/`, `MindMend/docker-compose.yml`, `MindMend/Dockerfile`.
- Utilities: `MindMend/scripts/` (deploy, monitor, setup).
- Data (dev): `MindMend/data/` (SQLite by default).
- Config: `MindMend/config.py`, `.env.template`, `.env.production`.
- Tests: `MindMend/tests/` mirroring modules.

## Build, Test, and Development Commands
- Create venv: `python -m venv .venv && source .venv/bin/activate`.
- Install deps (editable): `pip install -e MindMend`.
- Run locally (dev DB): `python MindMend/main.py` → `http://localhost:5000`.
- Docker (prod-like): `cd MindMend && docker-compose up -d --build`.
- Health check: `curl http://localhost:8000/health` or run `MindMend/scripts/monitor.sh`.

## Coding Style & Naming Conventions
- Python 3.11, UTF-8, 4-space indentation.
- Naming: `snake_case` (functions/vars), `PascalCase` (classes), `UPPER_SNAKE` (constants).
- Imports: standard → third-party → local; avoid wildcards.
- Lint/format before PRs: `ruff check MindMend` and `black MindMend`.

## Testing Guidelines
- Framework: pytest. Place tests under `MindMend/tests/` with `test_*.py` files and `test_*` functions.
- Run tests: `pytest -q` (with venv active).
- Coverage target: ≥ 80% where practical.
- Use Flask test client for endpoint tests; add fixtures for routes, models, and scripts.

## Commit & Pull Request Guidelines
- Commits (imperative, concise): e.g., `feat(admin): add role guard`, `fix(payments): handle Stripe 4xx`.
- Branches: `feat/*`, `fix/*`, `chore/*`, `docs/*`.
- PRs: include summary, rationale, screenshots (for UI), steps to validate, and linked issues. Keep scope focused.

## Security & Configuration Tips
- Do not commit secrets. Copy `.env.template` to `.env.production` (Docker) or `.env.local` (dev).
- Set `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`, DB/Redis creds. Rotate keys regularly.
- Dev DB: SQLite (`sqlite:///data/patients.db`). Docker: Postgres/Redis/Ollama.
- Review `MindMend/security_enhancements.py` when altering auth or session settings.

