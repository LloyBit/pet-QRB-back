from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from typing import Optional, Union
import json

class MigrationRepository:
    def __init__(self, redis_client: Union[SyncRedis, AsyncRedis]):
        self.redis = redis_client
        self.last_block_key = "last_processed_block"

    # Создать/обновить транзакцию
    async def create_transaction(self, key: str, transaction_data: dict, expire_seconds: int = 3600):
        data = json.dumps(transaction_data)
        await self.redis.set(key, data)
        await self.redis.expire(key, expire_seconds)

    # Найти транзакцию
    async def find_transaction(self, key: str) -> Optional[dict]:
        data = await self.redis.get(key)
        if not data:
            return None
        return json.loads(data)

    # Удалить транзакцию
    async def delete_transaction(self, key: str):
        await self.redis.delete(key)

    # Методы для последнего обработанного блока
    async def get_last_block_number(self) -> int | None:
        data = await self.redis.get(self.last_block_key)
        if data is None:
            return None
        return int(data)

    async def set_last_block_number(self, block_number: int):
        await self.redis.set(self.last_block_key, block_number)

        
    