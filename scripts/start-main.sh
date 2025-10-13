#!/usr/bin/env bash
set -e

# Run migrations
echo "🔄 Running database migrations..."

# Устанавливаем PYTHONPATH 
export PYTHONPATH="$(dirname "$(dirname "$0")")"

if alembic upgrade head; then
  echo "✅ Database migrations completed successfully!"
else
  echo "❌ Migration failed!"
  exit 1
fi

# Запуск приложения
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
