from sqlalchemy import delete, select
from fastapi import HTTPException, Response, status
from app.infrastructure.db.postgres.schemas import Tariffs
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.application.models import PatchTariffModel, TariffCreate, TariffActivateQuery
import logging

logger = logging.getLogger(__name__)

class TariffsService:
    '''Сервис для работы с тарифами.'''
    def __init__(self, db_helper: AsyncDatabaseHelper):
        self.db_helper = db_helper
        
    async def create(self, data: TariffCreate):
        async with self.db_helper.transaction() as session:
            tariff = Tariffs(**data.model_dump())
            session.add(tariff)
            return Response(status_code=status.HTTP_201_CREATED)

    async def get_all(self):
        async with self.db_helper.session_only() as session:
            result = await session.execute(select(Tariffs))
            return result.scalars().all()

    async def get_by_name(self, name: str):
        async with self.db_helper.session_only() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            return result.scalar_one_or_none()

    async def update(self, name: str, data: PatchTariffModel):
        async with self.db_helper.transaction() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            tariff = result.scalar_one_or_none()
            if not tariff:
                raise HTTPException(status_code=404, detail="Тариф не найден")

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(tariff, key, value)

            session.add(tariff)
            return tariff

    async def set_activate(self, name: str, data: TariffActivateQuery):
        async with self.db_helper.transaction() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            tariff = result.scalar_one_or_none()
            if not tariff:
                raise HTTPException(status_code=404, detail="Тариф не найден")

            tariff.is_active = data.is_active
            session.add(tariff)

            return tariff
        
    # TODO: Добавить проверку по активным пользователям(можно добавить поле с последним приобритением тарифа и по нему допускать удаление)
    async def delete_by_name(self, name: str):
        async with self.db_helper.transaction() as session:
            result = await session.execute(delete(Tariffs).where(Tariffs.name == name))
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Тарифы не найдены")
            return result.rowcount
