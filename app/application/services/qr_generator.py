from datetime import datetime
import hashlib
from io import BytesIO
import logging
from uuid import UUID
import uuid

import qrcode
from sqlalchemy import select

from app.config import settings
from app.infrastructure.db.postgres.schemas import Tariffs, Transactions, Users
from app.infrastructure.db.postgres.database import db_helper

logger = logging.getLogger(__name__)

class QRCodeService:
    def __init__(self):
        self.address = settings.admin_wallet_address
        self.chain_id = settings.chain_id
        self.gas_limit = None
        
    def _build_calldata(self, payment_id: UUID) -> str:
        """
        Строит calldata для вызова функции payForTariff(bytes32 paymentId).
        Функция payForTariff имеет сигнатуру: payForTariff(bytes32)
        """
        # Конвертируем payment_id в bytes32
        # Сначала хешируем строку, чтобы получить 32 байта
        payment_hash = hashlib.sha256(payment_id.encode()).digest()
        
        # Вычисляем селектор функции payForTariff(bytes32)
        # Сигнатура: "payForTariff(bytes32)"
        function_signature = "payForTariff(bytes32)"
        # Для простоты используем предвычисленный селектор
        # В реальном проекте лучше использовать web3.py или eth-utils
        function_selector = "0x" + hashlib.sha256(function_signature.encode()).hexdigest()[:8]
        
        # Добавляем параметр (32 байта)
        param = payment_hash.hex()
        
        # Собираем calldata
        calldata = function_selector + param
        
        return calldata
        
    def _prepare_qr_data(self, address, chain_id, value_wei, gas_limit, calldata) -> str:
        """
        Подготавливает ссылку для QR-кода вида:
        https://metamask.app.link/send/<address>@<chainId>?value=<wei>&gas=<limit>&data=<calldata>
        <address> - адрес кошелька, на который будет отправлен платеж
        <chainId> - идентификатор сети, на которой будет отправлен платеж
        <wei> - сумма платежа в wei, запрашиваеися из бэкенда
        <limit> - лимит газа для транзакции
        <calldata> - данные для вызова функции контракта
        """
        url = (
            "https://metamask.app.link/send/"
            f"{address}@{chain_id}"
            f"?value={value_wei}&gas={gas_limit}&data={calldata}"
        )
        return url
    
    def _generate_qr_code_image(self, data: str) -> BytesIO:
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

    async def build_qr_image(self, tariff_name: str, user_id: str, gas_limit: int = 100000) -> BytesIO:
        """ 
        Генерирует bytesIO QR-код для платежа.
        
        Создает транзакцию в БД по tariff_name и user_id, затем генерирует QR-код с calldata.
        """
        async with db_helper.transaction() as session:
            # Убеждаемся, что пользователь существует в PostgreSQL
            await self._ensure_user_exists_internal(user_id, session)
            
            # Получаем тариф
            tariff = await self._get_tariff_by_name_internal(tariff_name, session)
            if not tariff:
                raise ValueError(f"Tariff '{tariff_name}' not found")
            
            # Генерируем payment_id
            payment_id = uuid.uuid4()
            
            # Создаем запись транзакции в БД
            transaction = Transactions(
                payment_id=payment_id,
                user_id=user_id,
                tariff_id=tariff.tariff_id,
                amount=tariff.price,
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(transaction)
            
            # Генерируем calldata с payment_id
            calldata = self._build_calldata(payment_id)
            data = self._prepare_qr_data(self.address, self.chain_id, tariff.price, gas_limit, calldata)
            
            logger.info(f"Created transaction {payment_id} for user {user_id}, tariff {tariff_name}")
            logger.info(f"QR Data: {data}")
            return self._generate_qr_code_image(data)
    
    async def _ensure_user_exists_internal(self, user_id: str, session) -> None:
        """Убеждается, что пользователь существует в PostgreSQL"""
        query = select(Users).where(Users.user_id == user_id)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user = Users(user_id=user_id)
            session.add(user)
            logger.info(f"Created user {user_id} in PostgreSQL")
    
    async def _get_tariff_by_name_internal(self, tariff_name: str, session) -> Tariffs:
        """ Получает тариф по названию. """
        query = select(Tariffs).where(Tariffs.name == tariff_name, Tariffs.is_active == True)
        result = await session.execute(query)
        return result.scalar_one_or_none()