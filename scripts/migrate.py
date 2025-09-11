"""Скрипт для запуска миграций Alembic"""
import os
import sys
import subprocess
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def run_migrations():
    """Запускает миграции Alembic"""
    try:
        print("🔄 Running database migrations...")
        
        # Устанавливаем переменные окружения для Alembic
        os.environ['PYTHONPATH'] = str(root_dir)
        
        # Запускаем миграции
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Database migrations completed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
