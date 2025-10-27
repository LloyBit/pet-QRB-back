import logging

from fastapi import HTTPException

from app.application.models import PatchTariffModel, TariffActivateQuery, TariffCreate, TariffData
from app.infrastructure.db.postgres.repositories.tariffs import TariffsRepository

logger = logging.getLogger(__name__)


class TariffsService:
    """Сервис для работы с тарифами."""
    def __init__(self, tariffs_repo: TariffsRepository):
        self.tariffs_repo = tariffs_repo
        
    # Добавить генерацию UUID по умолчанию
    async def create(self, data: TariffCreate):
        tariff = await self.tariffs_repo.create(data.model_dump())
        return tariff 

    async def get_all(self):
        return await self.tariffs_repo.get_all()

    async def get_by_name(self, name: str):
        raw_tariff = await self.tariffs_repo.get_by_name(name)
        if not raw_tariff:
            raise HTTPException(status_code=404, detail="Тариф не найден")
        tariff = TariffData.model_validate(raw_tariff)
        return tariff

    async def update(self, name: str, data: PatchTariffModel):
        update_data = data.model_dump(exclude_unset=True)
        tariff = await self.tariffs_repo.update(name, update_data)
        if not tariff:
            raise HTTPException(status_code=404, detail="Тариф не найден")
        return tariff

    async def set_activate(self, name: str, data: TariffActivateQuery):
        tariff = await self.tariffs_repo.get_by_name(name)
        if not tariff:
            raise HTTPException(status_code=404, detail="Тариф не найден")
        tariff.is_active = data.is_active
        updated = await self.tariffs_repo.update(name, {"is_active": data.is_active})
        return updated

    async def delete_by_name(self, name: str):
        deleted_num = await self.tariffs_repo.delete_by_name(name)
        if deleted_num == 0:
            raise HTTPException(status_code=404, detail="Тарифы не найдены")
        return deleted_num
