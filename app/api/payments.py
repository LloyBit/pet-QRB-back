from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..application.container import ServicesContainer
from ..models import CreatePaymentRequest, CreatePaymentResponse, UpdateFromAddressRequest, qr_code_query

router = APIRouter(prefix="/payments", tags=["payments"])

# Инициализируем контейнер
container = ServicesContainer()

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(request: CreatePaymentRequest):
    """Создает новый платеж."""
    api_service = container.get_payment_api_service()
    return await api_service.create_payment(request)

@router.post("/{payment_id}/from_address")
async def update_from_address(payment_id: str, request: UpdateFromAddressRequest):
    """Обновляет адрес отправителя в платеже."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.update_from_address(payment_id, request)

@router.get("/check/{payment_id}")
async def check_payment(payment_id: str):
    """Проверяет статус платежа с мануальным опросом блокчейна."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.check_payment(payment_id)

@router.get("/status/{payment_id}")
async def get_payment_status_only(payment_id: str):
    """Только проверяет статус платежа без обработки."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.get_payment_status(payment_id)

@router.get("/info/{payment_id}")
async def get_payment_info(payment_id: str):
    """Получает информацию о платеже из Redis."""
    payment_api_service = container.get_payment_api_service()
    return await payment_api_service.get_payment_info(payment_id)

@router.post("/qr_code")
async def get_qr_code_image(query: qr_code_query):
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
