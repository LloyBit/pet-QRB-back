from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.application.container import ServicesContainer
from app.presentation.api.models import (
    CreatePaymentRequest, 
    CreatePaymentResponse, 
    UpdateFromAddressRequest, 
    UpdateFromAddressResponse,
    QRCodeQuery,
    PaymentInfoResponse,
    PaymentCheckResponse,
    PaymentStatusResponse
)

router = APIRouter(prefix="/payments", tags=["payments"])

# Инициализируем контейнер
container = ServicesContainer()

@router.post("", response_model=CreatePaymentResponse)
async def create_payment(request: CreatePaymentRequest):
    """Создает новый платеж."""
    payment_manager = container.get_payment_manager()
    return await payment_manager.create_payment(
        user_id=request.user_id,
        tariff_name=request.tariff_name
    )

@router.get("/{payment_id}", response_model=PaymentInfoResponse)
async def get_payment_info(payment_id: UUID):
    """Получает информацию о платеже."""
    payment_manager = container.get_payment_manager()
    payment_info = await payment_manager.get_payment_info(payment_id)
    
    if not payment_info:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment_info

@router.put("/{payment_id}/from-address", response_model=UpdateFromAddressResponse)
async def update_from_address(payment_id: UUID, request: UpdateFromAddressRequest):
    """Обновляет адрес отправителя в платеже."""
    payment_manager = container.get_payment_manager()
    success = await payment_manager.update_payment_from_address(
        payment_id=payment_id,
        from_address=request.from_address
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return UpdateFromAddressResponse(status="success", message="From address updated")

@router.post("/{payment_id}/check", response_model=PaymentCheckResponse)
async def check_payment(payment_id: UUID):
    """Проверяет статус платежа с мануальным опросом блокчейна."""
    payment_manager = container.get_payment_manager()
    status = await payment_manager.check_and_process_payment(payment_id=payment_id)
    
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return PaymentCheckResponse(
        payment_id=payment_id,
        status=status,
        message="Payment status checked and processed if confirmed"
    )

@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(payment_id: UUID):
    """Получает статус платежа без обработки."""
    payment_processor = container.get_payment_processor()
    status = await payment_processor.get_payment_status_safe(payment_id)
    
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return PaymentStatusResponse(payment_id=payment_id, status=status)

@router.post("/qr-code")
async def get_qr_code_image(query: QRCodeQuery):
    """Генерирует QR-код для указанного пользователем тарифа."""
    qr_service = container.get_qr_service()
    qr_image = await qr_service.build_qr_image(tariff_name=query.tariff_name, user_id=query.user_id)
    return StreamingResponse(
        qr_image,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=qr_code_{query.user_id}_{query.tariff_name}.png"
        }
    )
