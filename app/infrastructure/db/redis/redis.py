import redis.asyncio as redis
from app.config import settings

# Создаем Redis клиент с базовой конфигурацией
redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=10,  
    retry_on_timeout=True,
    socket_keepalive=True,
)