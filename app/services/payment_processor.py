from datetime import datetime, timezone
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.db.postgres.schemas import Transactions, Users
from ..infrastructure.db.redis.redis import redis_client
from .blockchain_checker import BlockchainChecker

logger = logging.getLogger(__name__)

class PaymentProcessor:
    """Сервис для обработки платежей с мануальным опросом блокчейна."""
    
    def __init__(self, blockchain_checker: BlockchainChecker = None):
        self.migration_lock_timeout = 30  # секунды
        self.blockchain_checker = blockchain_checker
        
        if not self.blockchain_checker:
            logger.warning("BlockchainChecker not provided - using mock implementation")
    
    async def process_confirmed_payment(self, payment_id: str, session: AsyncSession):
        # Обновляем статус в PostgreSQL
        query = select(Transactions).where(Transactions.payment_id == payment_id)
        result = await session.execute(query)
        transaction = result.scalar_one_or_none()
        
        if transaction and transaction.status == "pending":
            transaction.status = "confirmed"
            transaction.confirmed_at = datetime.now(timezone.utc)
            
            # Обновляем тариф пользователя
            await self._update_user_tariff(transaction.user_id, transaction.tariff_id, session)
            
            await session.commit()
            
            # Удаляем из Redis
            await redis_client.delete(f"payment:{payment_id}")
            
            return True
        
        return False
    async def _check_blockchain_transaction(self, payment_id: str, expected_amount: int) -> bool:
        """
        Проверяет подтверждение транзакции в блокчейне.
        
        Args:
            payment_id: ID платежа
            expected_amount: Ожидаемая сумма в wei
            
        Returns:
            bool: True если транзакция подтверждена в блокчейне
        """
        if not self.blockchain_checker:
            logger.warning(f"No blockchain checker available for payment {payment_id}")
            return False
        
        try:
            # Получаем данные из Redis для дополнительной валидации
            redis_key = f"payment:{payment_id}"
            redis_data = await redis_client.get(redis_key)
            if not redis_data:
                logger.warning(f"Payment {payment_id} not found in Redis during blockchain check")
                return False
            
            # Парсим данные из Redis (новый формат JSON)
            try:
                import json
                payment_data = json.loads(redis_data)
                from_address = payment_data.get('from_address')
                min_timestamp = payment_data.get('created_at')
                if min_timestamp:
                    # Конвертируем ISO timestamp в Unix timestamp
                    from datetime import datetime
                    dt = datetime.fromisoformat(min_timestamp.replace('Z', '+00:00'))
                    min_timestamp = int(dt.timestamp())
            except Exception as e:
                logger.warning(f"Error parsing payment data for {payment_id}: {e}")
                from_address = None
                min_timestamp = None
            
            # Проверяем блокчейн
            confirmed = await self.blockchain_checker.check_transaction_confirmation(
                payment_id=payment_id,
                expected_amount=expected_amount,
                from_address=from_address,
                min_timestamp=min_timestamp
            )
            
            if confirmed:
                logger.info(f"Blockchain confirmation received for payment {payment_id}")
            else:
                logger.info(f"Blockchain confirmation pending for payment {payment_id}")
            
            return confirmed
            
        except Exception as e:
            logger.error(f"Error checking blockchain for payment {payment_id}: {e}")
            return False
    
    async def _migrate_payment_to_postgres(
        self, 
        payment_id: str, 
        user_id: int, 
        tariff_id: int, 
        amount: int,
        session: AsyncSession
    ) -> bool:
        """Атомарно мигрирует платеж из Redis в PostgreSQL."""
        migration_key = f"migrating:{payment_id}"
        
        try:
            # Устанавливаем флаг миграции
            await redis_client.set(migration_key, "1", ex=self.migration_lock_timeout)
            
            # Проверяем, не существует ли уже запись в PostgreSQL
            existing_transaction = await self._get_transaction(payment_id, session)
            if existing_transaction:
                logger.info(f"Transaction {payment_id} already exists in PostgreSQL")
                await redis_client.delete(migration_key)
                return True
            
            # Создаем запись в PostgreSQL
            success = await self._create_transaction(
                payment_id, user_id, tariff_id, amount, session
            )
            
            if success:
                # Обновляем пользователя (привязываем тариф)
                await self._update_user_tariff(user_id, tariff_id, session)
                
                # Удаляем данные из Redis только после успешной записи
                redis_key = f"payment:{payment_id}"
                await redis_client.delete(redis_key)
                logger.info(f"Successfully migrated payment {payment_id} to PostgreSQL")
            
            # Удаляем флаг миграции
            await redis_client.delete(migration_key)
            return success
            
        except Exception as e:
            logger.error(f"Error migrating payment {payment_id}: {e}")
            # Удаляем флаг миграции в случае ошибки
            await redis_client.delete(migration_key)
            return False
    
    async def _get_transaction(self, payment_id: str, session: AsyncSession):
        """Получает транзакцию из PostgreSQL."""
        query = select(Transactions).where(Transactions.payment_id == payment_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def _create_transaction(
        self, 
        payment_id: str, 
        user_id: int, 
        tariff_id: int, 
        amount: int,
        session: AsyncSession
    ) -> bool:
        """Создает запись транзакции в PostgreSQL."""
        try:
            # Используем UUID как строку для payment_id
            transaction = Transactions(
                payment_id=payment_id,  # Теперь это строка UUID
                user_id=user_id,
                tariff_id=tariff_id,
                amount=amount,
                created_at=datetime.now(timezone.utc),
                expired_at=datetime.now(timezone.utc) + relativedelta(months=+1)
            )
            
            session.add(transaction)
            await session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error creating transaction {payment_id}: {e}")
            await session.rollback()
            return False
    
    async def _update_user_tariff(self, user_id: int, tariff_id: int, session: AsyncSession):
        """Обновляет тариф пользователя."""
        try:
            # Получаем пользователя
            query = select(Users).where(Users.user_id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                # Обновляем тариф и срок действия
                user.tariff_id = tariff_id
                user.tariff_expires_at = datetime.now(timezone.utc) + relativedelta(months=+1)
                await session.commit()
                logger.info(f"Updated user {user_id} tariff to {tariff_id}")
            
        except Exception as e:
            logger.error(f"Error updating user {user_id} tariff: {e}")
            await session.rollback()
    
    async def get_payment_status_safe(self, payment_id: str, session: AsyncSession) -> str:
        """
        Безопасная проверка статуса платежа с учетом миграции.
        """
        try:
            # Сначала проверяем PostgreSQL
            transaction = await self._get_transaction(payment_id, session)
            if transaction:
                return "Accepted"
            
            # Проверяем флаг миграции
            migration_key = f"migrating:{payment_id}"
            is_migrating = await redis_client.get(migration_key)
            if is_migrating:
                return "In_progress"
            
            # Проверяем Redis (новый формат)
            redis_key = f"payment:{payment_id}"
            redis_data = await redis_client.get(redis_key)
            if redis_data:
                return "In_progress"
            
            return "not_found"
            
        except Exception as e:
            logger.error(f"Error in get_payment_status_safe for {payment_id}: {e}")
            return "not_found"
