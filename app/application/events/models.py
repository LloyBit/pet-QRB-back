from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Типы событий в системе"""
    PAYMENT_CREATED = "payment_created"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    USER_TARIFF_UPDATED = "user_tariff_updated"
    BLOCKCHAIN_TRANSACTION_DETECTED = "blockchain_transaction_detected"

class BaseEvent(BaseModel):
    """Базовая модель события"""
    event_id: UUID = Field(..., description="Уникальный ID события")
    event_type: EventType = Field(..., description="Тип события")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Источник события")
    version: str = Field(default="1.0")

class PaymentCreatedEvent(BaseEvent):
    """Событие создания платежа"""
    event_type: EventType = EventType.PAYMENT_CREATED
    payment_id: UUID
    user_id: str
    tariff_id: int
    amount: int
    wallet_address: str

class PaymentConfirmedEvent(BaseEvent):
    """Событие подтверждения платежа"""
    event_type: EventType = EventType.PAYMENT_CONFIRMED
    payment_id: UUID
    user_id: str
    tariff_id: int
    amount: int
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None

class PaymentFailedEvent(BaseEvent):
    """Событие неудачного платежа"""
    event_type: EventType = EventType.PAYMENT_FAILED
    payment_id: UUID
    user_id: str
    reason: str
    error_code: Optional[str] = None

class UserTariffUpdatedEvent(BaseEvent):
    """Событие обновления тарифа пользователя"""
    event_type: EventType = EventType.USER_TARIFF_UPDATED
    user_id: str
    old_tariff_id: Optional[int] = None
    new_tariff_id: int
    expires_at: datetime

class BlockchainTransactionDetectedEvent(BaseEvent):
    """Событие обнаружения транзакции в блокчейне"""
    event_type: EventType = EventType.BLOCKCHAIN_TRANSACTION_DETECTED
    payment_id: UUID
    transaction_hash: str
    from_address: str
    to_address: str
    amount: int