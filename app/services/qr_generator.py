from io import BytesIO
import logging

import qrcode

from app.config import settings

logger = logging.getLogger(__name__)

class QRCodeService:
    def __init__(self, transaction_address: str | None = None):
        # можно передать адрес явно, или взять из настроек по умолчанию
        self.transaction_address = transaction_address or settings.admin_wallet_address

    def _prepare_qr_data(
        self, tariff_name: str, user_id: str, payment_id: str | None = None
    ) -> str:
        """
        Подготавливает строку данных для QR-кода.
        """
        return (
            f"tarif:{tariff_name},"
            f"user_id:{user_id},"
            f"transaction_address:{self.transaction_address}"
        )

    def _generate_qr_code(self, data: str) -> BytesIO:
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

    def build_qr_image(
        self, tariff_name: str, user_id: str, payment_id: str | None = None
    ) -> BytesIO:
        """
        Главная точка входа: подготавливает данные и генерирует QR-код.
        """
        data = self._prepare_qr_data(tariff_name, user_id, payment_id)
        logger.info(f"QR Data: {data}")
        return self._generate_qr_code(data)
