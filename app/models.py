from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enum import Enum as PyEnum

# Enum для состояний платежа
class PaymentState(PyEnum):
    NOT_PAID = "not_paid"
    PAID = "paid"
    PENDING = "pending"

# Модель запроса на генерацию QR кода 
class qr_code_query(BaseModel):
    user_id: int
    tariff_name: str

# Модель для создания тарифа — клиент не передаёт ID
class TariffCreate(BaseModel):
    name: str
    price: int
    features: str

# Модель для ответа — включает ID, который сгенерировала база
class TariffRead(TariffCreate):
    tariff_id: int

# Модель обновления тарифа с необязательными полями
class PatchTariffModel(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = Field(None, ge=0, le=1000, description="Price must be between 0 and 1000")
    features: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

# Модель для вывода пользователя
class UserOut(BaseModel):
    user_id: int
    tariff: str

    class Config:
        from_attributes = True

# Модель для webhook'а подтверждения платежа
class PaymentConfirmationWebhook(BaseModel):
    payment_id: str
    user_id: int
    tariff_id: int
    amount: int

# Модель для создания платежа
class CreatePaymentRequest(BaseModel):
    user_id: int
    tariff_name: str

# Модель ответа при создании платежа
class CreatePaymentResponse(BaseModel):
    payment_id: str
    amount: int
    tariff_name: str
    wallet_address: str
    qr_data: str

# Модель для обновления адреса отправителя
class UpdateFromAddressRequest(BaseModel):
    from_address: str