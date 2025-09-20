from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

# Сервисные enum'ы
class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    
class PaymentState(str, Enum):
    NOT_PAID = "not_paid"
    PAID = "paid"
    PENDING = "pending"
    
# Сервисные модели для платежей
class CreatePaymentResponse(BaseModel):
    payment_id: UUID
    amount: int
    tariff_name: str
    wallet_address: str
    qr_data: str

class PaymentData(BaseModel):
    payment_id: UUID
    user_id: str
    tariff_id: UUID
    amount: int
    status: PaymentStatus
    from_address: Optional[str] = None
    created_at: datetime
    confirmed_at: Optional[datetime] = None

class PaymentValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    error_code: Optional[str] = None

# Сервисные модели для пользователей
class UserData(BaseModel):
    user_id: str
    tariff_id: Optional[UUID] = None
    tariff_expires_at: Optional[datetime] = None
    status: UserStatus = UserStatus.ACTIVE
    
class UserOut(BaseModel):
    user_id: int
    tariff_id: Optional[UUID] = None
    tariff_expires_at: Optional[datetime] = None
    status: UserStatus = UserStatus.ACTIVE

# Сервисные модели для тарифов
class TariffData(BaseModel):
    tariff_id: UUID
    name: str
    price: int
    features: str
    is_active: bool
    
class TariffCreate(BaseModel):
    name: str
    price: int
    features: str
    is_active: bool

class PatchTariffModel(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None

# Сервисные модели для блокчейна
class BlockchainTransaction(BaseModel):
    transaction_hash: str
    from_address: str
    to_address: str
    amount: int
    block_number: int
    gas_used: int
    timestamp: datetime
    status: str  # "success" or "failed"

class BlockchainValidationResult(BaseModel):
    is_confirmed: bool
    confirmations: int
    transaction: Optional[BlockchainTransaction] = None
    error_message: Optional[str] = None
