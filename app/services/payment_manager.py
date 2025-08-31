from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..infrastructure.db.postgres.schemas import Tariffs, Users
from ..infrastructure.db.redis.redis import redis_client
from .payment_processor import PaymentProcessor

logger = logging.getLogger(__name__)

class PaymentManager:
    """Сервис для управления жизненным циклом платежей."""
    
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
    
    async def create_payment(
        self, 
        user_id: int, 
        tariff_name: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Создает новый платеж.
        
        Args:
            user_id: ID пользователя
            tariff_name: Название тарифа
            session: Сессия базы данных
            
        Returns:
            Dict с данными платежа
        """
        try:
            # Получаем информацию о тарифе
            tariff = await self._get_tariff_by_name(tariff_name, session)
            if not tariff:
                raise ValueError(f"Tariff '{tariff_name}' not found")
            
            # Проверяем пользователя
            user = await self._get_user(user_id, session)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Генерируем уникальный payment_id
            payment_id = self._generate_payment_id()
            
            # Создаем данные платежа
            payment_data = {
                "payment_id": payment_id,
                "user_id": user_id,
                "tariff_id": tariff.tariff_id,
                "tariff_name": tariff_name,
                "amount": tariff.price,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
                "from_address": None,  # Будет заполнено при оплате
                "transaction_hash": None  # Будет заполнено при подтверждении
            }
            
            # Сохраняем в Redis с TTL (например, 24 часа)
            redis_key = f"payment:{payment_id}"
            await redis_client.set(
                redis_key, 
                json.dumps(payment_data), 
                ex=86400  # 24 часа
            )
            
            logger.info(f"Created payment {payment_id} for user {user_id}, tariff {tariff_name}")
            
            return {
                "payment_id": payment_id,
                "amount": tariff.price,
                "tariff_name": tariff_name,
                "wallet_address": self._get_wallet_address(),
                "qr_data": self._prepare_qr_data(payment_id, tariff_name, user_id)
            }
            
        except Exception as e:
            logger.error(f"Error creating payment for user {user_id}, tariff {tariff_name}: {e}")
            raise
    
    async def get_payment_info(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о платеже.
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Dict с данными платежа или None
        """
        try:
            redis_key = f"payment:{payment_id}"
            payment_data = await redis_client.get(redis_key)
            
            if payment_data:
                return json.loads(payment_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting payment info for {payment_id}: {e}")
            return None
    
    async def update_payment_from_address(
        self, 
        payment_id: str, 
        from_address: str
    ) -> bool:
        """
        Обновляет адрес отправителя в платеже.
        
        Args:
            payment_id: ID платежа
            from_address: Адрес отправителя
            
        Returns:
            bool: True если обновление прошло успешно
        """
        try:
            payment_data = await self.get_payment_info(payment_id)
            if not payment_data:
                return False
            
            payment_data["from_address"] = from_address
            payment_data["status"] = "waiting_confirmation"
            
            redis_key = f"payment:{payment_id}"
            await redis_client.set(
                redis_key, 
                json.dumps(payment_data), 
                ex=86400
            )
            
            logger.info(f"Updated payment {payment_id} with from_address {from_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating payment {payment_id} with from_address: {e}")
            return False
    
    async def check_and_process_payment(
        self, 
        payment_id: str,
        session: AsyncSession
    ) -> str:
        """
        Проверяет и обрабатывает платеж.
        
        Args:
            payment_id: ID платежа
            session: Сессия базы данных
            
        Returns:
            str: Статус платежа
        """
        try:
            payment_data = await self.get_payment_info(payment_id)
            if not payment_data:
                return "not_found"
            
            # Проверяем и обрабатываем платеж
            status = await self.payment_processor.check_and_process_payment(
                payment_id=payment_id,
                user_id=payment_data["user_id"],
                tariff_id=payment_data["tariff_id"],
                amount=payment_data["amount"],
                session=session
            )
            
            # Обновляем статус в Redis
            if status == "Accepted":
                await self._mark_payment_completed(payment_id)
            
            return status
            
        except Exception as e:
            logger.error(f"Error checking payment {payment_id}: {e}")
            return "not_found"
    
    async def _mark_payment_completed(self, payment_id: str) -> None:
        """Отмечает платеж как завершенный."""
        try:
            payment_data = await self.get_payment_info(payment_id)
            if payment_data:
                payment_data["status"] = "completed"
                payment_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                
                redis_key = f"payment:{payment_id}"
                await redis_client.set(
                    redis_key, 
                    json.dumps(payment_data), 
                    ex=86400
                )
                
                logger.info(f"Marked payment {payment_id} as completed")
                
        except Exception as e:
            logger.error(f"Error marking payment {payment_id} as completed: {e}")
    
    async def _get_tariff_by_name(self, tariff_name: str, session: AsyncSession):
        """Получает тариф по названию."""
        query = select(Tariffs).where(Tariffs.name == tariff_name, Tariffs.is_active == True)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_user(self, user_id: int, session: AsyncSession):
        """Получает пользователя по ID."""
        query = select(Users).where(Users.user_id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    def _generate_payment_id(self) -> str:
        """Генерирует уникальный ID платежа."""
        # Используем UUID для уникальности
        return str(uuid.uuid4())
    
    def _get_wallet_address(self) -> str:
        """Получает адрес кошелька для оплаты."""
        return settings.admin_wallet_address
    
    def _prepare_qr_data(self, payment_id: str, tariff_name: str, user_id: int) -> str:
        """Подготавливает данные для QR-кода."""
        return (
            f"payment_id:{payment_id},"
            f"tariff:{tariff_name},"
            f"user_id:{user_id},"
            f"wallet:{self._get_wallet_address()}"
        )
