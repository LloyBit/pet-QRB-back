#!/usr/bin/env bash
set -e

# Create database
python scripts/create_db.py

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

exec "$@"
