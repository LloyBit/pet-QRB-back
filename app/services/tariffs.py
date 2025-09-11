from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException

from ..infrastructure.db.postgres.schemas import Tariffs
from ..models import TariffCreate, PatchTariffModel


class TariffsService:
    '''Сервис для работы с тарифами.'''
    @staticmethod
    async def create(session: AsyncSession, data: TariffCreate):
        tariff = Tariffs(**data.model_dump())
        session.add(tariff)
        await session.commit()
        await session.refresh(tariff)
        return tariff

    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(select(Tariffs))
        return result.scalars().all()

    @staticmethod
    async def get_by_name(session: AsyncSession, name: str):
        result = await session.execute(select(Tariffs).where(Tariffs.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, name: str, data: PatchTariffModel):
        result = await session.execute(select(Tariffs).where(Tariffs.name == name))
        tariff = result.scalar_one_or_none()
        if not tariff:
            raise HTTPException(status_code=404, detail="Тариф не найден")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tariff, key, value)

        session.add(tariff)
        await session.commit()
        await session.refresh(tariff)
        return tariff

    @staticmethod
    async def delete_by_name(session: AsyncSession, name: str):
        result = await session.execute(delete(Tariffs).where(Tariffs.name == name))
        await session.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Тарифы не найдены")
        return result.rowcount
