import redis.exceptions
from ..infrastructure.db.postgres.database import get_pool_stats
from ..infrastructure.db.redis.redis import redis_client


class HealthService:
    '''Сервис для проверки здоровья системы.'''
    @staticmethod
    async def check_db_pool():
        """Проверка пула соединений к базе"""
        return await get_pool_stats()

    @staticmethod
    async def check_db_with_explanation():
        """Возвращает пул соединений + объяснение"""
        stats = await get_pool_stats()
        explanation = {
            "connection_lifecycle": {
                "checked_in": "Connections available in pool for reuse",
                "checked_out": "Connections currently being used by requests",
                "overflow": "Additional connections created beyond pool_size",
                "total_connections": "Total connections (checked_in + checked_out)"
            },
            "pool_behavior": {
                "when_new_connections_created": [
                    "When all pool connections are checked_out",
                    "When overflow limit is not reached",
                    "When a new request needs a connection"
                ],
                "when_connections_reused": [
                    "When checked_in connections are available",
                    "When a request completes and returns connection to pool"
                ]
            }
        }
        return {"pool_stats": stats, "explanation": explanation}

    @staticmethod
    async def check_redis_user(user_id: int):
        """Проверка конкретного пользователя в Redis"""
        try:
            user_data = await redis_client.hgetall(f"user:{user_id}")
            if user_data:
                return {"user_id": user_id, "redis_data": user_data, "status": "found"}
            return {"user_id": user_id, "redis_data": {}, "status": "not_found"}
        except redis.exceptions.ConnectionError:
            return {"user_id": user_id, "error": "Redis connection failed", "status": "error"}

    @staticmethod
    async def get_all_redis_users():
        """Получить всех пользователей"""
        try:
            keys = await redis_client.keys("user:*")
            users = {}
            for key in keys:
                user_id = key.split(':')[1]
                user_data = await redis_client.hgetall(key)
                users[user_id] = user_data
            return {"total_users": len(users), "users": users, "status": "success"}
        except redis.exceptions.ConnectionError:
            return {"error": "Redis connection failed", "status": "error"}

    @staticmethod
    async def ping_redis():
        """Проверка доступности Redis"""
        try:
            result = await redis_client.ping()
            return {"redis_status": "connected" if result else "disconnected", "ping_response": result}
        except redis.exceptions.ConnectionError:
            return {"redis_status": "error", "error": "Redis connection failed"}

    @staticmethod
    async def overview():
        """Общий health-check системы"""
        health_status = {"database": "unknown", "redis": "unknown", "overall": "unknown"}

        # DB check
        try:
            db_stats = await get_pool_stats()
            health_status["database"] = "healthy"
            health_status["db_stats"] = db_stats
        except Exception as e:
            health_status["database"] = "error"
            health_status["db_error"] = str(e)

        # Redis check
        try:
            redis_result = await redis_client.ping()
            health_status["redis"] = "healthy" if redis_result else "disconnected"
        except redis.exceptions.ConnectionError:
            health_status["redis"] = "error"

        # Overall
        if health_status["database"] == "healthy" and health_status["redis"] in ["healthy", "disconnected"]:
            health_status["overall"] = "healthy"
        else:
            health_status["overall"] = "unhealthy"

        return health_status

    @staticmethod
    async def ping():
        """Простой ping для load testing"""
        return {"status": "ok", "timestamp": "2025-08-21T22:30:00Z"}
