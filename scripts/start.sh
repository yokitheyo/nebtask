#!/bin/bash
set -e

echo "Ожидание запуска базы данных..."
sleep 5

echo "Запуск миграций и инициализация базы данных..."
python -m app.db.migrations

echo "Запуск приложения..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
