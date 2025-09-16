""" Модуль входа в приложение """
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from sqlalchemy import text

from app.api import router as all_routers
from app.config import settings
from app.infrastructure.db.postgres.database import db_helper
from app.infrastructure.db.redis.redis import redis_client
from app.infrastructure.kafka.client import KafkaClient
from app.infrastructure.kafka.consumer import KafkaConsumerService
from app.infrastructure.kafka.producer import KafkaProducerService
from app.infrastructure.logger_config import setup_logging
from app.infrastructure.middleware import ExceptionMiddleware, LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик событий жизненного цикла FastAPI"""
    # Startup
    logger = setup_logging()
    logger.info("🚀 Application starting up...")
    
    # Запускаем Kafka при старте
    logger.info("🔄 Connecting to Kafka...")
    kafka_client = KafkaClient()
    await kafka_client.connect()
    app.state.kafka_client = kafka_client
    app.state.kafka_producer = KafkaProducerService(kafka_client)
    app.state.kafka_consumer = KafkaConsumerService(kafka_client)
    
    # Запускаем Redis при старте
    logger.info("🔄 Connecting to Redis...")
    app.state.redis_client = redis_client
    
    # Запускаем Postgres при старте
    logger.info("🔄 Connecting to Postgres...")
    # Test database connectivity without creating a persistent connection
    try:
        async with db_helper.session_only() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ Postgres connection test successful")
    except Exception as e:
        logger.error(f"❌ Postgres connection test failed: {e}")
        raise
    app.state.engine = db_helper.engine
    
    # Shutdown
    yield
    # Закрываем соединения
    await db_helper.close()
    await app.state.redis_client.close()
    await kafka_client.disconnect()
    logger.info("🛑 Application shut down successfully")
    
app = FastAPI(title="QR-Blockchain Server", version="1.0.0", lifespan=lifespan)

# Добавляем middleware. Порядок важен: ExceptionMiddleware должен быть первым
app.add_middleware(ExceptionMiddleware, debug=settings.debug)
app.add_middleware(LoggingMiddleware, log_level=settings.log_level)
# Подключаем предварительно собранные роуты
app.include_router(all_routers)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)