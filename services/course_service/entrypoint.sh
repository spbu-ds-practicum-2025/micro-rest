#!/usr/bin/env bash
set -e

sleep 2

alembic upgrade head || true

exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000}
