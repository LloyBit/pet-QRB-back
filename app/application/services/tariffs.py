from sqlalchemy import delete, select
from fastapi import HTTPException

from app.infrastructure.db.postgres.schemas import Tariffs
from app.infrastructure.db.postgres.database import db_helper
from app.application.models import PatchTariffModel, TariffCreate

class TariffsService:
    '''Сервис для работы с тарифами.'''
    
    async def create(self, data: TariffCreate):
        async with db_helper.transaction() as session:
            tariff = Tariffs(**data.model_dump())
            session.add(tariff)
            return tariff

    async def get_all(self):
        async with db_helper.session_only() as session:
            result = await session.execute(select(Tariffs))
            return result.scalars().all()

    async def get_by_name(self, name: str):
        async with db_helper.session_only() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            return result.scalar_one_or_none()

    async def update(self, name: str, data: PatchTariffModel):
        async with db_helper.transaction() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            tariff = result.scalar_one_or_none()
            if not tariff:
                raise HTTPException(status_code=404, detail="Тариф не найден")

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(tariff, key, value)

            session.add(tariff)
            return tariff

    async def delete_by_name(self, name: str):
        async with db_helper.transaction() as session:
            result = await session.execute(delete(Tariffs).where(Tariffs.name == name))
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Тарифы не найдены")
            return result.rowcount
