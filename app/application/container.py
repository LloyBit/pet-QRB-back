from app.application.services.blockchain_listener import PaymentPoller
from app.application.services.payment_processor import PaymentProcessor, TransactionService
from app.application.services.qr_generator import QRCodeService
from app.application.services.tariffs import TariffsService
from app.infrastructure.container import InfrastructureContainer
from app.config import Settings

class ServicesContainer:
    """ Контейнер для сервисов с зависимостями, синглтонами. Ленивая инициализация """
    def __init__(self, settings: Settings, infra: InfrastructureContainer):
        self._settings = settings
        self._infra = infra
        self._qr_service = None
        self._payment_processor = None
        self._tariffs_service = None
        self._transaction_service = None
        self._blockchain_listener = None
        
    @property
    def qr_service(self) -> QRCodeService:
        if self._qr_service is None:
            self._qr_service = QRCodeService(
                settings = self._settings,
                transaction_service=self.transaction_service,
                blockchain_helper=self._infra.blockchain_helper
            )
        return self._qr_service

    @property
    def payment_processor(self) -> PaymentProcessor:
        if self._payment_processor is None:
            self._payment_processor = PaymentProcessor(
                transactions_pg=self._infra.transactions_pg
            )
        return self._payment_processor

    @property
    def tariffs_service(self) -> TariffsService:
        if self._tariffs_service is None:
            self._tariffs_service = TariffsService(
                tariffs_repo=self._infra.tariffs_pg
            )
        return self._tariffs_service

    @property
    def transaction_service(self) -> TransactionService:
        if self._transaction_service is None:
            self._transaction_service = TransactionService(
                redis_repository=self._infra.transactions_redis,
                transactions_pg=self._infra.transactions_pg
            )
        return self._transaction_service

    @property
    def blockchain_listener(self) -> PaymentPoller:
        if self._blockchain_listener is None:
            self._blockchain_listener = PaymentPoller(
                settings=self._settings,
                redis_repository=self._infra.transactions_redis,
                transactions_pg=self._infra.transactions_pg,
                blockchain_helper=self._infra.blockchain_helper,
                transaction_service=self.transaction_service
            )
        return self._blockchain_listener