""" Модуль входа в приложение """
from contextlib import asynccontextmanager
import sys

from fastapi import FastAPI
import uvicorn

from app.api import router as all_routers
from app.infrastructure.db.postgres.database import engine
from app.infrastructure.middleware import LoggingMiddleware, ExceptionMiddleware
from app.infrastructure.logger_config import setup_logging
from app.config import settings
from scripts.migrate import run_migrations
from scripts.create_db import create_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI application"""
    # Startup
    logger = setup_logging()
    logger.info("🚀 Application starting up...")
    
    # Создаем базу данных при старте
    if not create_database():
        logger.error("❌ Failed to create database. Exiting...")
        sys.exit(1)
    
    # Запускаем миграции при старте
    if not run_migrations():
        logger.error("❌ Failed to run migrations. Exiting...")
        sys.exit(1)
    
    yield
    # Shutdown
    logger.info("🛑 Application shutting down...")
    await engine.dispose()

app = FastAPI(title="QR Payment Server", version="1.0.0", lifespan=lifespan)

# Добавляем middleware. Порядок важен: ExceptionMiddleware должен быть первым
app.add_middleware(ExceptionMiddleware, debug=settings.debug)
app.add_middleware(LoggingMiddleware, log_level=settings.log_level)
# Подключаем предварительно собранные роуты
app.include_router(all_routers)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)