from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.application.container import ServicesContainer
from app.application.services.payment_processor import TransactionService
from app.presentation.api.models import PaymentCheckResponse, QRCodeQuery

router = APIRouter(prefix="/payments", tags=["payments"])

def get_container(request: Request) -> ServicesContainer:
    return request.app.state.container 

@router.get("/{payment_id}/check", response_model=PaymentCheckResponse)
async def check_payment(
        payment_id: UUID, 
        container: ServicesContainer = Depends(get_container)
    ):
    """ Проверяет факт платежа из БД и возвращает токен"""
    payment_service = container.get_payment_processor()
    return PaymentCheckResponse(payment_service.check_payment(payment_id))

# TODO: переделать под GET
@router.post("/qr-code")
async def get_qr_code_image(
        query: QRCodeQuery, 
        container: ServicesContainer = Depends(get_container)
    ):
    """Генерирует QR-код для указанного пользователем тарифа."""
    transaction_service = container.get_transaction_service()
    qr_service = container.get_qr_service()

    tariff_name = await transaction_service.get_tariff_by_name(query.tariff_name)
    payment_hash = await transaction_service.create_transaction(query.user_id, tariff_name)
    qr_data = qr_service.build_qr_payload(payment_hash_hex=payment_hash)
    qr_image = qr_service.generate_qr_code_image(data=qr_data)
    
    return StreamingResponse(
        qr_image,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=qr_code_{query.user_id}_{query.tariff_name}.png",
            "X-Payment-Hash": payment_hash
        }
    )
