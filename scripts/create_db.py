"""Скрипт для создания базы данных (только для инфраструктурного уровня)"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config import settings

def create_database():
    """Создает базу данных, если она не существует"""
    try:
        print(f"🔄 Creating database '{settings.db_name}' if not exists...")
        
        # Используем admin URL для создания базы данных
        admin_engine = create_engine(settings.admin_db_url, isolation_level="AUTOCOMMIT")
        
        with admin_engine.connect() as conn:
            try:
                conn.execute(text(f'CREATE DATABASE "{settings.db_name}"'))
                print(f"✅ Database '{settings.db_name}' created successfully!")
            except ProgrammingError as e:
                # Проверяем код ошибки PostgreSQL (42P04 = duplicate database)
                if hasattr(e.orig, 'pgcode') and e.orig.pgcode == '42P04':
                    print(f"ℹ️ Database '{settings.db_name}' already exists - skipping creation")
                else:
                    # Если это другая ошибка PostgreSQL, пробрасываем её дальше
                    raise e
            except Exception as e:
                # Для других типов ошибок проверяем текст сообщения
                error_msg = str(e).lower()
                if any(phrase in error_msg for phrase in ["already exists", "duplicate", "база данных", "уже существует"]):
                    print(f"ℹ️ Database '{settings.db_name}' already exists - skipping creation")
                else:
                    raise e
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
