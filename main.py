""" Модуль входа в приложение """
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as all_routers
from app.infrastructure.db.postgres.database import engine
from app.infrastructure.middleware import LoggingMiddleware, ExceptionMiddleware
from app.infrastructure.logger_config import setup_logging
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI application"""
    # Startup
    logger = setup_logging()  # Инициализируем логирование при старте
    logger.info("🚀 Application starting up...")
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
