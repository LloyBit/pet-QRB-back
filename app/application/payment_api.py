from typing import Any, Dict

from fastapi import HTTPException

from ..models import CreatePaymentRequest, UpdateFromAddressRequest
from .payment_manager import PaymentManager
from .payment_processor import PaymentProcessor

class PaymentAPIService:
    """Сервисный слой для API платежей."""
    
    def __init__(self, payment_manager: PaymentManager, payment_processor: PaymentProcessor):
        self.payment_manager = payment_manager
        self.payment_processor = payment_processor
    
    async def create_payment(self, request: CreatePaymentRequest) -> Dict[str, Any]:
        """Создает новый платеж."""
        return await self.payment_manager.create_payment(
            user_id=request.user_id,
            tariff_name=request.tariff_name
        )
    
    async def update_from_address(self, payment_id: str, request: UpdateFromAddressRequest) -> Dict[str, Any]:
        """Обновляет адрес отправителя."""
        success = await self.payment_manager.update_payment_from_address(
            payment_id=payment_id,
            from_address=request.from_address
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {"status": "success", "message": "From address updated"}
    
    async def check_payment(self, payment_id: str) -> Dict[str, Any]:
        """Проверяет статус платежа."""
        status = await self.payment_manager.check_and_process_payment(
            payment_id=payment_id
        )
        
        if status == "not_found":
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "payment_id": payment_id,
            "status": status,
            "message": "Payment status checked and processed if confirmed"
        }
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Получает статус платежа без обработки."""
        status = await self.payment_processor.get_payment_status_safe(payment_id)
        
        if status == "not_found":
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {"payment_id": payment_id, "status": status}
    
    async def get_payment_info(self, payment_id: str) -> Dict[str, Any]:
        """Получает информацию о платеже."""
        payment_info = await self.payment_manager.get_payment_info(payment_id)
        
        if not payment_info:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return payment_info
