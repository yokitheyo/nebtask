#!/bin/bash
set -e

alembic upgrade head

echo "Waiting for database to start..."
sleep 5

echo "Running migrations and initializing database..."
python -m app.db.migrations

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 
