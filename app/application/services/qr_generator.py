from io import BytesIO
import logging
import urllib.parse

import qrcode

from app.application.services.payment_processor import TransactionService
from app.config import Settings
from app.application.models import ContractData, TransactionData
from app.infrastructure.blockchain import AsyncWeb3Service

logger = logging.getLogger(__name__)

class QRCodeService:
    def __init__(self, settings: Settings, transaction_service: TransactionService, blockchain_helper: AsyncWeb3Service):
        self._settings = settings
        self.transaction_service = transaction_service
        self.blockchain_helper = blockchain_helper
        
    def build_qr_payload(self, data: TransactionData) -> str:
        """Генерирует calldata и собирает данные для QR-кода."""
        paymentId=data.payment_id  
        tariffId=data.tariff_id
        price=data.amount
        
        contract_data = ContractData(
            paymentId=paymentId, 
            tariffId=tariffId,
            price=price
        )
        
        calldata = self.blockchain_helper.build_calldata(data=contract_data)
        return self._build_url(self._settings.contract_address, self._settings.chain_id, price, calldata)
    
    def generate_qr_code_image(self, url: str) -> BytesIO:
        """
        Генерирует PNG QR-код по заданной строке, возвращает BytesIO-объект.
        """
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        return bio
    
    def _build_url(self, address, chain_id, value_wei, calldata) -> str:
        """
        Подготавливает ссылку для QR-кода вида:
        https://metamask.app.link/send/<address>@<chainId>?value=<wei>&data=<calldata>
        """
        url = (
            "https://metamask.app.link/send/"
            f"{address}@{chain_id}"
            f"?value={value_wei}&data={calldata}"
        )
        return url
    