# Repository Guidelines

## Project Structure & Module Organization
- Root app: `MindMend/` (Flask + Socket.IO).
- Entry point: `MindMend/main.py` (runs the server). Core app: `MindMend/app.py`.
- Views and assets: `MindMend/templates/`, `MindMend/static/`.
- Domain logic: `MindMend/models/` (AI, DB, integrations).
- Ops: `MindMend/docker/`, `MindMend/docker-compose.yml`, `MindMend/Dockerfile`.
- Utilities: `MindMend/scripts/` (deploy, monitor, setup).
- Data (dev): `MindMend/data/` (SQLite by default).
- Configuration: `MindMend/config.py`, `.env.template`, `.env.production`.

## Build, Test, and Development Commands
- Create venv: `python -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -e MindMend` (reads `MindMend/pyproject.toml`).
- Run locally (dev DB): `python MindMend/main.py` (serves on `localhost:5000`).
- Docker (prod-like): `cd MindMend && docker-compose up -d --build`.
- Health check: `curl http://localhost:8000/health` (Docker) or see `MindMend/scripts/monitor.sh`.

## Coding Style & Naming Conventions
- Language: Python 3.11, 4-space indentation, UTF-8.
- Names: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Imports: standard → third-party → local; avoid wildcards.
- Lint/format (recommended): `ruff check MindMend` and `black MindMend` before PRs.

## Testing Guidelines
- Framework: pytest (recommended). Place tests under `MindMend/tests/` mirroring module paths.
- Names: files `test_*.py`; functions `test_*`.
- Run: `pytest -q` (with venv active). Target coverage ≥ 80% where practical.
- Add fixture-based tests for routes, models, and scripts; use Flask test client for endpoints.

## Commit & Pull Request Guidelines
- Commits: imperative present, concise: `feat(admin): add role guard`, `fix(payments): handle Stripe 4xx`.
- Branches: `feat/*`, `fix/*`, `chore/*`, `docs/*`.
- PRs: include summary, rationale, screenshots for UI, steps to validate, and linked issues. Keep changes scoped.

## Security & Configuration Tips
- Never commit secrets. Copy `.env.template` → `.env.production` (Docker) or `.env.local` (dev); set `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`, DB/Redis creds.
- Dev DB defaults to SQLite (`sqlite:///data/patients.db`); Docker uses Postgres/Redis/Ollama. Rotate keys and review `MindMend/security_enhancements.py` if changing auth.
