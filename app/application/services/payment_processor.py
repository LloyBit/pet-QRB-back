from datetime import datetime
import json
import logging
import logging
from typing import Optional
from uuid import UUID
import uuid
import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.infrastructure.db.postgres.schemas import Transactions
from app.infrastructure.db.postgres.schemas import Tariffs, Transactions
from app.infrastructure.db.redis.repositories import MigrationRepository

logger = logging.getLogger(__name__)

class PaymentProcessor:
    def __init__(self, db_helper: AsyncDatabaseHelper):
        self.db_helper = db_helper  

    async def check_payment(self, payment_id: UUID) -> Optional[str]:
        """Проверяет, есть ли платеж с данным UUID в БД и возвращает токен, если есть."""
        async with self.db_helper.session_only() as session:
            query = select(Transactions).where(Transactions.payment_id == payment_id)
            result = await session.execute(query)
            if result.scalar_one_or_none() is not None:
                return PaymentProcessor._get_secret_token()
        return None
        
    @staticmethod
    def _get_secret_token() -> str:
        """ Выдает секретный токен """
        #TODO: Продумать логику токену
        return "SUPER_SECRET_TOKEN"   
    
class TransactionService:
    def __init__(self, db_helper, redis_repository: MigrationRepository):
        self.db_helper = db_helper
        self.redis_repository = redis_repository

    async def create_transaction(self, user_id: int, tariff_name: str) -> str:
        """Создаёт транзакцию в Redis и возвращает payment_hash"""
        payment_id = str(uuid.uuid4())
        
        async with self.db_helper.session_only() as session:
            tariff = await self._get_tariff_or_raise(tariff_name, session)
        payment_hash = TransactionService.compute_payment_hash(payment_id, tariff.tariff_id, tariff.price)
        data = {
            "payment_id": payment_id,
            "user_id": user_id,
            "tariff_id": tariff.tariff_id,
            "amount": tariff.price,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        key = f"transaction:{payment_hash}"
        await self.redis_repository.create_transaction(key, json.dumps(data), expire_seconds=3600)
        return payment_hash

    # TODO: Искать тариф по UUID
    async def _get_tariff_or_raise(self, tariff_name: str, session: AsyncSession) -> Tariffs:
        """Возвращает тариф или бросает исключение, если не найден."""
        query = select(Tariffs).where(Tariffs.name == tariff_name, Tariffs.is_active == True)
        result = await session.execute(query)
        tariff = result.scalar_one_or_none()
        if not tariff:
            raise ValueError(f"Tariff '{tariff_name}' not found")
        return tariff
    
    @staticmethod
    def compute_payment_hash(payment_id: str, tariff_id: str, tariff_price: int) -> str:
        data = f"{payment_id}{tariff_id}{tariff_price}"
        return hashlib.sha256(data.encode()).hexdigest()
    