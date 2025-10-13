from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.config import settings

Base = declarative_base()

# Только для миграций можно использовать sync engine
DATABASE_URL = settings.db_url.replace("postgresql+asyncpg://", "postgresql://")
engine = create_engine(DATABASE_URL)


