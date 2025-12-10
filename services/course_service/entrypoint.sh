#!/usr/bin/env bash
set -e

sleep 2

# Надо будет подогнать миграции под скрипт Артема чтобы они заработали
# alembic upgrade head || true

exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000}
