from sqlalchemy import delete, select
from app.infrastructure.db.postgres.schemas import Tariffs
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper

class TariffsRepository:
    def __init__(self, db_helper: AsyncDatabaseHelper):
        self.db_helper = db_helper

    async def create(self, data: dict) -> Tariffs:
        async with self.db_helper.transaction() as session:
            tariff = Tariffs(**data)
            session.add(tariff)
            return tariff

    async def get_all(self):
        async with self.db_helper.session_only() as session:
            result = await session.execute(select(Tariffs))
            tariff = result.scalars().all()
            return tariff

    async def get_by_name(self, name: str):
        async with self.db_helper.session_only() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            tariff = result.scalar_one_or_none()
            return tariff

    async def update(self, name: str, update_data: dict):
        async with self.db_helper.transaction() as session:
            result = await session.execute(select(Tariffs).where(Tariffs.name == name))
            tariff = result.scalar_one_or_none()
            if not tariff:
                return None
            for key, value in update_data.items():
                setattr(tariff, key, value)
            session.add(tariff)
            return tariff

    async def delete_by_name(self, name: str):
        async with self.db_helper.transaction() as session:
            result = await session.execute(delete(Tariffs).where(Tariffs.name == name))
            deleted_num = result.rowcount
            return deleted_num
