from typing import  Dict
from .models import TariffModel

# Словарь тарифов — можно использовать как реестр
TARIFFS: Dict[str, TariffModel] = {
    "basic": TariffModel(name="basic", price=100, features=["QR"]),
    "pro": TariffModel(name="pro", price=200, features=["QR", "Priority Support"]),
    "premium": TariffModel(name="premium", price=300, features=["QR", "Support", "Reports"]),
}

def get_tariff_price(tariff: str) -> TariffModel:
    return TARIFFS.get(tariff, TariffModel(name="basic", price=100, features=["QR"]))
