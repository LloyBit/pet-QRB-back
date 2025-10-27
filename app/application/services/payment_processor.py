from datetime import datetime
import hashlib
import json
import logging
from typing import Optional
from uuid import UUID
import uuid

from app.application.models import TariffData, TransactionData
from app.infrastructure.db.redis.repositories import TransactionsRepository as TransactionsRepositoryRedis
from app.infrastructure.db.postgres.repositories.transactions import TransactionsRepository as TransactionsRepositoryPostgres

logger = logging.getLogger(__name__)

class PaymentProcessor:
    
    def __init__(self, transactions_pg: TransactionsRepositoryPostgres):
        self.transactions_pg = transactions_pg  

    async def check_payment(self, payment_id: UUID) -> Optional[str]:
        """Проверяет, есть ли платеж с данным UUID в БД и возвращает токен, если есть."""
        tx = self.transactions_pg.find(payment_id)
        if tx.scalar_one_or_none() is not None:
            return PaymentProcessor._get_secret_token()
        return None
        
    @staticmethod
    def _get_secret_token() -> str:
        """ Выдает секретный токен """
        #TODO: Продумать логику токену
        return "SUPER_SECRET_TOKEN"   
    
class TransactionService:
    """ Сервис управления жизненным циклом платежа """
    REDIS_KEY_TEMPLATE = "transaction:{payment_hash}"
    
    def __init__(self, redis_repository: TransactionsRepositoryRedis, transactions_pg: TransactionsRepositoryPostgres):
        self.redis_repository = redis_repository
        self.tariffs_pg = transactions_pg

    async def create_transaction_redis(self, user_id: int, tariff: TariffData) -> str:
        """Создаёт транзакцию в Redis и возвращает данные для формирования calldata """
        payment_id = str(uuid.uuid4())
        
        data = TransactionData(
            payment_id=payment_id,
            user_id=user_id,
            tariff_id=tariff.tariff_id,
            amount=tariff.price,
            created_at=datetime.utcnow(),
        )
        payment_hash = TransactionService.compute_payment_hash(data.payment_id, data.tariff_id)
        key = self._make_redis_key(payment_hash)
        
        await self.redis_repository.create_transaction(key, json.dumps(data, default=str), expire_seconds=3600)
        return data
    
    async def migrate_transaction(self, payment_hash: str):
        tx = await self._find_transaction_redis(payment_hash)
        new_tx = await self._create_transaction_postgres(tx)
        if new_tx:
            delete_tx = await self._delete_transaction_redis(payment_hash)
            return delete_tx
        else:
            raise 
    
    async def _find_transaction_redis(self, payment_hash):
        key = self._make_redis_key(payment_hash)
        data = await self.redis_repository.find_transaction(key)
        tx = TransactionData(**data)
        return tx
    
    async def _create_transaction_postgres(self, tx):
        tx = self.tariffs_pg.create(tx)
        return tx
    
    async def _delete_transaction_redis(self, payment_hash):
        key = self._make_redis_key(payment_hash)
        return await self.redis_repository.delete_transaction(key)
        
    async def _prepare_data(self, payment_id: UUID, user_id: str, tariff_id: UUID, tariff_price: int):
        return TransactionData(
        payment_id=payment_id,
        user_id=user_id,
        tariff_id=tariff_id,
        amount=tariff_price,
        created_at=datetime.utcnow(),
    )
    
    @classmethod
    def _make_redis_key(cls, payment_hash: str) -> str:
        return cls.REDIS_KEY_TEMPLATE.format(payment_hash=payment_hash)
    
    @staticmethod
    def compute_payment_hash(payment_id: str, tariff_id: str) -> str:
        data = f"{payment_id}{tariff_id}"
        return hashlib.sha256(data.encode()).hexdigest()
    