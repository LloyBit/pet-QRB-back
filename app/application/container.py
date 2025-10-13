from app.application.services.payment_processor import PaymentProcessor, TransactionService
from app.application.services.qr_generator import QRCodeService
from app.application.services.tariffs import TariffsService
from app.application.services.users import UsersService
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.infrastructure.db.redis.repositories import MigrationRepository

class ServicesContainer:
    """ Контейнер для сервисов с зависимостями, синглтонами. Ленивая инициализация """
    def __init__(self, db_helper: AsyncDatabaseHelper, redis_repository: MigrationRepository):
        self.db_helper = db_helper
        self.redis_repository = redis_repository
        self._qr_service = None
        self._payment_processor = None
        self._users_service = None
        self._tariffs_service = None
    # Синглтоны
    
    def get_qr_service(self) -> QRCodeService:
        if self._qr_service is None:
            self._qr_service = QRCodeService(
                db_helper=self.db_helper, 
                redis_repository = self.redis_repository, 
                transaction_service=self.get_transaction_service()
                )
        return self._qr_service

    def get_payment_processor(self) -> PaymentProcessor:
        if self._payment_processor is None:
            self._payment_processor = PaymentProcessor(
                db_helper=self.db_helper
            )
        return self._payment_processor
    
    def get_users_service(self) -> UsersService:
        if self._users_service is None:
            self._users_service = UsersService(db_helper=self.db_helper)
        return self._users_service
    
    def get_tariffs_service(self) -> TariffsService:
        if self._tariffs_service is None:
            self._tariffs_service = TariffsService(db_helper=self.db_helper)
        return self._tariffs_service
    
    def get_transaction_service(self) -> TransactionService:
        if self._transaction_service is None:
            self._transaction_service = TransactionService(
                db_helper=self.db_helper,
                redis_repository=self.redis_repository
            )
        return self._transaction_service



