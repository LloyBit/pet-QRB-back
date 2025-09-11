from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.db.postgres.database import get_session
from ..models import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    UpdateFromAddressRequest,
    qr_code_query,
)
from ..services.container import ServicesContainer
from .utils import handle_errors

router = APIRouter(prefix="/payments", tags=["payments"])

# Инициализируем контейнер
container = ServicesContainer()

@router.post("/create", response_model=CreatePaymentResponse)
@handle_errors("Error creating payment")
async def create_payment(request: CreatePaymentRequest, session: AsyncSession = Depends(get_session)):
    """Создает новый платеж."""
    api_service = container.get_payment_api_service()
    return await api_service.create_payment(request, session)

@router.post("/{payment_id}/from_address")
@handle_errors("Error updating from address")
async def update_from_address(payment_id: str, request: UpdateFromAddressRequest):
    """Обновляет адрес отправителя в платеже."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.update_from_address(payment_id, request)

@router.get("/check/{payment_id}")
@handle_errors("Error checking payment")
async def check_payment(payment_id: str, session: AsyncSession = Depends(get_session)):
    """Проверяет статус платежа с мануальным опросом блокчейна."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.check_payment(payment_id, session)

@router.get("/status/{payment_id}")
@handle_errors("Error getting payment status")
async def get_payment_status_only(payment_id: str, session: AsyncSession = Depends(get_session)):
    """Только проверяет статус платежа без обработки."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.get_payment_status(payment_id, session)

@router.get("/info/{payment_id}")
@handle_errors("Error getting payment info")
async def get_payment_info(payment_id: str):
    """Получает информацию о платеже из Redis."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.get_payment_info(payment_id)

@router.post("/qr_code")
@handle_errors("Error generating QR code")
async def get_qr_code_image(query: qr_code_query, session: AsyncSession = Depends(get_session)):
    """Генерирует QR-код для указанного пользователем тарифа."""
    qr_service = container.get_qr_service()
    qr_image = await qr_service.build_qr_image(
        tariff_name=query.tariff_name,
        user_id=query.user_id,
        session=session
    )
    return StreamingResponse(
        qr_image,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=qr_code_{query.user_id}_{query.tariff_name}.png"
        }
    )
