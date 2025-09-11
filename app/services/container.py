from app.config import settings

from .blockchain_checker import BlockchainChecker
from .health import HealthService
from .payment_api import PaymentAPIService
from .payment_manager import PaymentManager
from .payment_processor import PaymentProcessor
from .qr_generator import QRCodeService
from .tariffs import TariffsService
from .users import UsersService

class ServicesContainer:
    """Контейнер для сервисов с зависимостями и синглтонами."""
    def __init__(self):
        # Синглтоны
        self.qr_code_service = QRCodeService()
        self.health_service = HealthService()
        self.blockchain_checker = BlockchainChecker(
            rpc_url=settings.network_rpc_url,
            wallet_address=settings.admin_wallet_address,
            required_confirmations=settings.blockchain_confirmations
        )
        
        # Создаем зависимости без сессий
        self.payment_processor = PaymentProcessor(
            blockchain_checker=self.blockchain_checker
        )
        
        self.payment_manager = PaymentManager(
            payment_processor=self.payment_processor
        )
        
        self.payment_api_service = PaymentAPIService(
            payment_manager=self.payment_manager,
            payment_processor=self.payment_processor
        )
    
    # Фабрики для сервисов, требующих сессию
    def get_tariffs_service(self) -> TariffsService:
        """Фабрика для TariffsService - использует статические методы с сессией"""
        return TariffsService()
    
    def get_users_service(self, session) -> UsersService:
        """Фабрика для UsersService - требует сессию"""
        return UsersService(session)
    
    def get_payment_manager(self) -> PaymentManager:
        """Возвращает PaymentManager - методы принимают сессию"""
        return self.payment_manager
    
    def get_payment_processor(self) -> PaymentProcessor:
        """Возвращает PaymentProcessor - методы принимают сессию"""
        return self.payment_processor
    
    def get_payment_api_service(self) -> PaymentAPIService:
        """Возвращает PaymentAPIService - методы принимают сессию"""
        return self.payment_api_service
    
    # Геттеры для синглтонов
    def get_qr_service(self) -> QRCodeService:
        return self.qr_code_service
    
    def get_health_service(self) -> HealthService:
        return self.health_service
    
    def get_blockchain_checker(self) -> BlockchainChecker:
        return self.blockchain_checker
        




