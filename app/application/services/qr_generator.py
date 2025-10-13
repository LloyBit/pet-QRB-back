import hashlib
from io import BytesIO
import logging

import qrcode

from app.config import settings
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.infrastructure.db.redis.repositories import MigrationRepository
from app.application.services.payment_processor import TransactionService

logger = logging.getLogger(__name__)

class QRCodeService:
    def __init__(self, db_helper: AsyncDatabaseHelper, redis_repository: MigrationRepository, transaction_service: TransactionService):
        self.address = settings.admin_wallet_address
        self.chain_id = settings.chain_id
        self.gas_limit = None
        self.db_helper = db_helper
        self.redis_repository = redis_repository
        self.transaction_service = transaction_service
    
    
    def build_qr_payload(self, payment_hash_hex: str, value_wei: int, gas_limit: int) -> str:
        """Генерирует calldata и собирает данные для QR-кода."""
        calldata = self._build_calldata(payment_hash_hex)
        return self._prepare_qr_data(self.address, self.chain_id, value_wei, gas_limit, calldata)
    
    def generate_qr_code_image(self, data: str) -> BytesIO:
        """
        Генерирует PNG QR-код по заданной строке, возвращает BytesIO-объект.
        """
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        return bio
        
    # async def _ensure_user_and_get(self, user_id: int, session) -> Users:
    #     """Проверяет, есть ли пользователь, создаёт при необходимости и возвращает объект."""
    #     query = select(Users).where(Users.user_id == user_id)
    #     result = await session.execute(query)
    #     user = result.scalar_one_or_none()
    #     if not user:
    #         user = Users(user_id=user_id)
    #         session.add(user)
    #         logger.info(f"Created user {user_id} in PostgreSQL")
    #     return user
    
    def _build_calldata(self, payment_hash_hex: str) -> str:
        function_signature = "payForTariff(bytes32)"
        function_selector = "0x" + hashlib.sha256(function_signature.encode()).hexdigest()[:8]
        calldata = function_selector + payment_hash_hex  # просто соединяем строки
        return calldata
    
    def _prepare_qr_data(self, address, chain_id, value_wei, gas_limit, calldata) -> str:
        """
        Подготавливает ссылку для QR-кода вида:
        https://metamask.app.link/send/<address>@<chainId>?value=<wei>&gas=<limit>&data=<calldata>
        """
        url = (
            "https://metamask.app.link/send/"
            f"{address}@{chain_id}"
            f"?value={value_wei}&gas={gas_limit}&data={calldata}"
        )
        return url
    