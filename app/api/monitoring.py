from fastapi import APIRouter
from ..services.container import ServicesContainer

router = APIRouter(prefix="/health", tags=["monitoring"])

# Инициализируем контейнер
container = ServicesContainer()

@router.get("/db-pool")
async def get_db_pool_status():
    return await container.get_health_service().check_db_pool()

@router.get("/db-connections")
async def get_db_connection_details():
    return await container.get_health_service().check_db_with_explanation()

@router.get("/redis/check/{user_id}")
async def check_redis_user(user_id: int):
    return await container.get_health_service().check_redis_user(user_id)

@router.get("/redis/all")
async def get_all_redis_users():
    return await container.get_health_service().get_all_redis_users()

@router.get("/redis/ping")
async def redis_ping():
    return await container.get_health_service().ping_redis()

@router.get("/overview")
async def health_overview():
    return await container.get_health_service().overview()

@router.get("/ping")
async def health_ping():
    return await container.get_health_service().ping()
