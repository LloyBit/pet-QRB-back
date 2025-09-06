from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base

from ....config import settings
from .schemas import Tariffs, Transactions, Users

Base = declarative_base()

def create_database_if_not_exists(admin_db_url: str):
    """
    Создает базу данных, если она не существует
    
    :param db_url: URL для связи с базой
    """
    admin_engine = create_engine(admin_db_url, isolation_level="AUTOCOMMIT")
    
    with admin_engine.connect() as conn:
        try:
            conn.execute(text(f'CREATE DATABASE "{settings.db_name}"'))
            print(f"✅ Database '{settings.db_name}' created")
        except:
            print(f"ℹ️ Database '{settings.db_name}' already exists")


def init_db(db_url: str):
    """
    Инициализирует базу данных:
        1. Создает базу, если она не существует
        2. Создает таблицы в правильном порядке: Tariffs -> Users -> Transactions

    :param db_url: URL для связи с базой
    """
    create_database_if_not_exists(settings.admin_db_url)
    engine = create_engine(db_url)
    
    # Создаем таблицы в правильном порядке (сначала родительские, потом дочерние)
    Tariffs.__table__.create(bind=engine, checkfirst=True)
    Users.__table__.create(bind=engine, checkfirst=True)
    Transactions.__table__.create(bind=engine, checkfirst=True)
    
    print("✅ All tables created successfully!")

# Запуск скрипта
if __name__ == "__main__":
    init_db(settings.db_url)

