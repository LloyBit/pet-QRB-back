import redis.asyncio as async_redis
import redis as sync_redis
from app.config import settings

# Создаем синхронный Redis клиент для celery-worker
sync_redis_client = sync_redis.from_url(
    settings.redis_url_main,
    decode_responses=True
)

# Создаем асинхронный Redis клиент для главного приложения
asyncio_redis_client = async_redis.from_url(
    settings.redis_url_main,
    encoding="utf-8",
    decode_responses=True,
    max_connections=10,  
    retry_on_timeout=True,
    socket_keepalive=True,
)

