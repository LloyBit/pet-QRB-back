from app.config import settings

from .blockchain_checker import BlockchainChecker
from .payment_api import PaymentAPIService
from .payment_manager import PaymentManager
from .payment_processor import PaymentProcessor
from .qr_generator import QRCodeService
from .tariffs import TariffsService
from .users import UsersService
from ..infrastructure.db.postgres.database import db_helper

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
        
        # API сервисы
        self.payment_api_service = PaymentAPIService(
            payment_manager=self.payment_manager,
            payment_processor=self.payment_processor
        )
        
        self.users_service = UsersService()
        self.tariffs_service = TariffsService()
    
    # Геттеры для сервисов
    def get_payment_api_service(self) -> PaymentAPIService:
        return self.payment_api_service
    
    def get_users_service(self) -> UsersService:
        return self.users_service
    
    def get_tariffs_service(self) -> TariffsService:
        return self.tariffs_service
    
    def get_qr_service(self) -> QRCodeService:
        return self.qr_code_service
        




