'''DTO для API'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ==================== USER MODELS ====================

class UserOut(BaseModel):
    """Модель для вывода информации о пользователе"""
    user_id: int = Field(..., description="Уникальный идентификатор пользователя")
    
    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    """Модель для создания пользователя"""
    user_id: int = Field(
        ..., 
        ge=1, 
        le=9223372036854775807,
        description="Telegram user ID"
    )
    

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
        description="Цена тарифа в gwei"
    )
    features: str = Field(
        ..., 
        min_length=1,
        description="Описание возможностей тарифа"
    )
    is_active: bool = True
    
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

class TariffActivateQuery(BaseModel):
    is_active: bool = Field(..., description="Флаг активности тарифа")


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

class PaymentCheckResponse(BaseModel):
    """Модель ответа при проверке платежа"""
    token: Optional[str] = Field(None, description="Токен доступа")

# ==================== QR CODE MODELS ====================

class QRCodeQuery(BaseModel):
    """Модель для запроса QR кода"""
    user_id: int = Field(
        ..., 
        ge=1,  
        le=9223372036854775807,
        description="Telegram user ID"
    )
    tariff_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Название тарифа"
    )
    
    @field_validator('tariff_name')
    @classmethod
    def validate_tariff_name(cls, v):
        if not v.strip():
            raise ValueError('tariff_name не может быть пустым')
        return v.strip()