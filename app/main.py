""" Модуль входа в приложение """
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.presentation.api import router as all_routers
from app.config import settings
from app.infrastructure.db.redis.redis import asyncio_redis_client
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.presentation.middleware.logger_config import setup_logging
from app.presentation.middleware import ExceptionMiddleware, LoggingMiddleware
from app.application.container import ServicesContainer
from app.infrastructure.db.redis.repositories import MigrationRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик событий жизненного цикла FastAPI"""
    # Startup
    logger = setup_logging()
    logger.info("🚀 Application starting up...")
    
    # Создаем подключение ко всем БД
    app.state.postgres = AsyncDatabaseHelper(settings.db_url)
    await app.state.postgres.connect()
    
    # Создаем репозитории
    app.state.migration_repo = MigrationRepository(redis_client=asyncio_redis_client)
    
    # Билдим образ контейнера и прокидываем контейнер
    app.state.container = ServicesContainer(db_helper=app.state.postgres, redis_repository=app.state.migration_repo)
    
    # Тест БД, вынести отсюда
    try:
        logger.info("🔄 Connecting to Postgres...")
        async with app.state.postgres.session_only() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ Postgres connection test successful")
    except Exception as e:
        logger.error(f"❌ Postgres connection test failed: {e}")
        raise
    app.state.engine = app.state.postgres.engine
    
    yield
    
    # Shutdown
    # Закрываем соединения
    await app.state.postgres.close()
    await app.state.redis_client.close()
    
    logger.info("🛑 Application shut down successfully")
    
app = FastAPI(title="QR-Blockchain Server", version="1.0.0", lifespan=lifespan)

# Добавляем middleware. Порядок важен: ExceptionMiddleware должен быть первым
app.add_middleware(ExceptionMiddleware, debug=settings.debug)
app.add_middleware(LoggingMiddleware, log_level=settings.log_level)

# Подключаем предварительно собранные роуты
app.include_router(all_routers)
