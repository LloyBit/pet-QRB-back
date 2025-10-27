from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.infrastructure.db.postgres.repositories.tariffs import TariffsRepository
from app.infrastructure.db.postgres.repositories.transactions import TransactionsRepository as PostgresTransactionsRepository
from app.infrastructure.db.redis.repositories import TransactionsRepository as RedisTransactionsRepository
from app.config import Settings
from app.infrastructure.blockchain import AsyncWeb3Service

import redis.asyncio as async_redis

class InfrastructureContainer:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._async_db_helper: AsyncDatabaseHelper | None = None
        self._async_redis_helper: async_redis.Redis | None = None
        self._tariffs_pg: TariffsRepository | None = None
        self._transactions_pg: PostgresTransactionsRepository | None = None
        self._transactions_redis: RedisTransactionsRepository | None = None
        self._blockchain: AsyncWeb3Service | None = None
        
    @property
    def redis_client(self) -> async_redis.Redis:
        if self._async_redis_helper is None:
            self._async_redis_helper = async_redis.from_url(
                self._settings.redis_url_main,
                encoding=self._settings.encoding,
                decode_responses=self._settings.decode_responses,
                max_connections=self._settings.max_connections,
                retry_on_timeout=self._settings.retry_on_timeout,
                socket_keepalive=self._settings.socket_keepalive,
            )
        return self._async_redis_helper
    
    @property
    def db_helper(self) -> AsyncDatabaseHelper:
        if self._async_db_helper is None:
            self._async_db_helper = AsyncDatabaseHelper(self._settings.db_url)
        return self._async_db_helper

    @property
    def tariffs_pg(self) -> TariffsRepository:
        if self._tariffs_pg is None:
            self._tariffs_pg = TariffsRepository(self.db_helper)  
        return self._tariffs_pg

    @property
    def transactions_pg(self) -> PostgresTransactionsRepository:
        if self._transactions_pg is None:
            self._transactions_pg = PostgresTransactionsRepository(self.db_helper)
        return self._transactions_pg

    @property
    def transactions_redis(self) -> RedisTransactionsRepository:
        if self._transactions_redis is None:
            self._transactions_redis = RedisTransactionsRepository(self.redis_client)
        return self._transactions_redis

    @property
    def blockchain_helper(self) -> AsyncWeb3Service:
        if self._blockchain is None:
            self._blockchain = AsyncWeb3Service(settings=self._settings)
        return self._blockchain
    
    