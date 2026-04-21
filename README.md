# AI Debate Coach Backend

Backend MVP for the personal-user version of "AI Debate Coach".

Implemented:

- Flask application factory
- Blueprint routing
- Service and repository layering
- SQLAlchemy models for `sessions`, `messages`, and `evaluations`
- Alembic migration for the initial schema
- SQLite local development setup
- Mock LLM mode for local end-to-end testing
- Pytest coverage for `start`, `stream`, `evaluate`, and `prompt_builder`

Quick start:

```powershell
python -m pip install Flask Flask-SQLAlchemy SQLAlchemy alembic pytest requests python-dotenv
python -m alembic -c alembic.ini upgrade head
python run.py
```

More detailed frontend integration notes and manual test scripts are in [FRONTEND_HANDOFF.md](/d:/dev/web/ai-debate-coach/FRONTEND_HANDOFF.md).
Chinese field notes and frontend copy-paste examples are in [FRONTEND_HANDOFF_ZH.md](/d:/dev/web/ai-debate-coach/FRONTEND_HANDOFF_ZH.md).
A ready-to-copy frontend API helper is in [examples/frontend/api.js](/d:/dev/web/ai-debate-coach/examples/frontend/api.js).
