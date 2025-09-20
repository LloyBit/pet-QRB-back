from app.config import settings

from app.application.services.blockchain_checker import BlockchainChecker
from app.application.services.payment_manager import PaymentManager
from app.application.services.payment_processor import PaymentProcessor
from app.application.services.qr_generator import QRCodeService
from app.application.services.tariffs import TariffsService
from app.application.services.users import UsersService

class ServicesContainer:
    """Контейнер для сервисов с зависимостями и синглтонами."""
    def __init__(self):
        # Синглтоны
        self.qr_code_service = QRCodeService()
        self.blockchain_checker = BlockchainChecker(
            rpc_url=settings.network_rpc_url,
            wallet_address=settings.admin_wallet_address,
            required_confirmations=settings.blockchain_confirmations
        )
        
        # Сервисы с зависимостями
        self.payment_processor = PaymentProcessor(
            blockchain_checker=self.blockchain_checker
        )
        
        self.payment_manager = PaymentManager(
            payment_processor=self.payment_processor
        )
        
        self.users_service = UsersService()
        self.tariffs_service = TariffsService()
    
    # Геттеры для сервисов
    def get_payment_manager(self) -> PaymentManager:
        return self.payment_manager
    
    def get_payment_processor(self) -> PaymentProcessor:
        return self.payment_processor
    
    def get_users_service(self) -> UsersService:
        return self.users_service
    
    def get_tariffs_service(self) -> TariffsService:
        return self.tariffs_service
    
    def get_qr_service(self) -> QRCodeService:
        return self.qr_code_service
        




