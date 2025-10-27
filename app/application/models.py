from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

# Сервисные модели для тарифов

class TariffCreate(BaseModel):
    name: str
    price: int
    features: str
    is_active: bool = True

class TariffData(BaseModel):
    tariff_id: UUID
    name: str
    price: int
    features: str
    is_active: bool
    
    class Config:
        from_attributes = True
        
class PatchTariffModel(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None

class TariffActivateQuery(BaseModel):
    is_active: bool 

# Сервисные модели для транзакции

class TransactionData(BaseModel):
    """ Модель создания записи в Redis """
    payment_id: UUID
    user_id: int
    tariff_id: UUID
    amount: int
    created_at: datetime

class ContractData(BaseModel):
    """ Модель для создания calldata контракта """
    paymentId: UUID
    tariffId: UUID
    price: int
