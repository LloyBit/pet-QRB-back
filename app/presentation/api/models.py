'''DTO для API'''
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================== ENUMS ====================

class PaymentState(PyEnum):
    """Состояния платежа"""
    NOT_PAID = "not_paid"
    PAID = "paid"
    PENDING = "pending"


# ==================== USER MODELS ====================

class UserOut(BaseModel):
    """Модель для вывода информации о пользователе"""
    user_id: str = Field(..., description="Уникальный идентификатор пользователя")
    
    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    """Модель для создания пользователя"""
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Уникальный идентификатор пользователя"
    )
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('user_id не может быть пустым')
        return v.strip()


class UserUpdateRequest(BaseModel):
    """Модель для обновления пользователя"""
    user_id: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255,
        description="Уникальный идентификатор пользователя"
    )
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError('user_id не может быть пустым')
        return v.strip() if v else v


class UserDeleteResponse(BaseModel):
    """Модель ответа при удалении пользователя"""
    detail: str = Field(..., description="Сообщение о результате операции")


# ==================== TARIFF MODELS ====================

class TariffCreate(BaseModel):
    """Модель для создания тарифа"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Название тарифа"
    )
    price: int = Field(
        ..., 
        ge=0, 
        le=1000000,
        description="Цена тарифа в копейках"
    )
    features: str = Field(
        ..., 
        min_length=1,
        description="Описание возможностей тарифа"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Название тарифа не может быть пустым')
        return v.strip()
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if not v.strip():
            raise ValueError('Описание возможностей не может быть пустым')
        return v.strip()


class TariffRead(TariffCreate):
    """Модель для чтения тарифа"""
    tariff_id: UUID = Field(..., description="Уникальный идентификатор тарифа")
    
    model_config = ConfigDict(from_attributes=True)


class TariffUpdateRequest(BaseModel):
    """Модель для обновления тарифа"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255,
        description="Название тарифа"
    )
    price: Optional[int] = Field(
        None, 
        ge=0, 
        le=1000000,
        description="Цена тарифа в копейках"
    )
    features: Optional[str] = Field(
        None, 
        min_length=1,
        description="Описание возможностей тарифа"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Название тарифа не может быть пустым')
        return v.strip() if v else v
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Описание возможностей не может быть пустым')
        return v.strip() if v else v
    
    model_config = ConfigDict(from_attributes=True)


class TariffUpdateResponse(BaseModel):
    """Модель ответа при обновлении тарифа"""
    tariff_id: UUID = Field(..., description="Уникальный идентификатор тарифа")
    name: str = Field(..., description="Название тарифа")
    price: int = Field(..., description="Цена тарифа в копейках")
    features: str = Field(..., description="Описание возможностей тарифа")


class TariffDeleteResponse(BaseModel):
    """Модель ответа при удалении тарифа"""
    detail: str = Field(..., description="Сообщение о результате операции")


# ==================== PAYMENT MODELS ====================

class CreatePaymentRequest(BaseModel):
    """Модель для создания платежа"""
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Уникальный идентификатор пользователя"
    )
    tariff_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Название тарифа"
    )
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('user_id не может быть пустым')
        return v.strip()
    
    @field_validator('tariff_name')
    @classmethod
    def validate_tariff_name(cls, v):
        if not v.strip():
            raise ValueError('tariff_name не может быть пустым')
        return v.strip()


class CreatePaymentResponse(BaseModel):
    """Модель ответа при создании платежа"""
    payment_id: UUID = Field(..., description="Уникальный идентификатор платежа")
    amount: int = Field(..., ge=0, description="Сумма платежа в копейках")
    tariff_name: str = Field(..., description="Название тарифа")
    wallet_address: str = Field(..., description="Адрес кошелька для оплаты")
    qr_data: str = Field(..., description="QR код для оплаты")


class PaymentInfoResponse(BaseModel):
    """Модель для получения информации о платеже"""
    payment_id: UUID = Field(..., description="Уникальный идентификатор платежа")
    user_id: str = Field(..., description="Уникальный идентификатор пользователя")
    tariff_name: str = Field(..., description="Название тарифа")
    amount: int = Field(..., ge=0, description="Сумма платежа в копейках")
    wallet_address: str = Field(..., description="Адрес кошелька для оплаты")
    from_address: Optional[str] = Field(None, description="Адрес отправителя")
    status: str = Field(..., description="Статус платежа")
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата обновления")


class PaymentCheckResponse(BaseModel):
    """Модель ответа при проверке платежа"""
    payment_id: UUID = Field(..., description="Уникальный идентификатор платежа")
    status: str = Field(..., description="Статус платежа")
    message: str = Field(..., description="Сообщение о результате проверки")


class PaymentStatusResponse(BaseModel):
    """Модель ответа при получении статуса платежа"""
    payment_id: UUID = Field(..., description="Уникальный идентификатор платежа")
    status: str = Field(..., description="Статус платежа")


class UpdateFromAddressRequest(BaseModel):
    """Модель для обновления адреса отправителя"""
    from_address: str = Field(
        ..., 
        min_length=1,
        description="Адрес отправителя"
    )
    
    @field_validator('from_address')
    @classmethod
    def validate_from_address(cls, v):
        if not v.strip():
            raise ValueError('from_address не может быть пустым')
        return v.strip()


class UpdateFromAddressResponse(BaseModel):
    """Модель ответа при обновлении адреса отправителя"""
    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение о результате операции")


# ==================== QR CODE MODELS ====================

class QRCodeQuery(BaseModel):
    """Модель для запроса QR кода"""
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Уникальный идентификатор пользователя"
    )
    tariff_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Название тарифа"
    )
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('user_id не может быть пустым')
        return v.strip()
    
    @field_validator('tariff_name')
    @classmethod
    def validate_tariff_name(cls, v):
        if not v.strip():
            raise ValueError('tariff_name не может быть пустым')
        return v.strip()


# ==================== WEBHOOK MODELS ====================

class PaymentConfirmationWebhook(BaseModel):
    """Модель webhook для подтверждения платежа"""
    payment_id: UUID = Field(..., description="Уникальный идентификатор платежа")
    user_id: str = Field(..., description="Уникальный идентификатор пользователя")
    tariff_id: UUID = Field(..., description="Уникальный идентификатор тарифа")
    amount: int = Field(..., ge=0, description="Сумма платежа в копейках")