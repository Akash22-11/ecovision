#!/bin/sh
# Container entrypoint: run pending Alembic migrations, then start the API.
#
# Runs the same way locally (docker-compose), and on PaaS targets like
# Railway that build straight from the Dockerfile and don't read
# docker-compose.yml. Binds to $PORT when the platform provides one
# (e.g. Railway sets this dynamically); falls back to 8000 otherwise.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting EcoVision AI backend on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
