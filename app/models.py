from pydantic import BaseModel
from typing import Literal

# Модель запроса на генерацию QR кода и ответа с QR кодом
class qr_code_query(BaseModel):
    user_id: int
    tarif: str

class qr_code_response(BaseModel):
    qr_encoded: str

# Модели запроса на получение access токена и ответа с access токеном
class access_token_request(BaseModel):
    user_id: int

class access_token_response(BaseModel):
    user_id: int
    access_token: str

# Модель тарифа
class TariffModel(BaseModel):
    name: Literal["basic", "pro", "premium"]
    price: int
    features: list[str]