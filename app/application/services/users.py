from sqlalchemy import select
import logging
from app.infrastructure.db.postgres.schemas import Users
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.application.models import UserOut

logger = logging.getLogger(__name__)

# TODO: Рефактор класса по принципам SOLID
class UsersService:
    '''Сервис для работы с пользователями.'''
    def __init__(self, db_helper: AsyncDatabaseHelper):
        self.db_helper = db_helper
    
    async def ensure_user_exists(self, user_id: int) -> bool:
        """Убеждается, что пользователь существует в PostgreSQL"""
        async with self.db_helper.transaction() as session:
            existing_user = await self._get_user_internal(session, user_id)
            if not existing_user:
                user = Users(user_id=user_id)
                session.add(user)
                return True
            return True
    
    async def init_user(self, user_id: int):
        """Инициализация пользователя в Redis и PostgreSQL"""
        async with self.db_helper.transaction() as session:
            
            # Проверяем, существует ли пользователь в PostgreSQL
            existing_user = await self._get_user_internal(session, user_id)
            if not existing_user:
                # Создаем пользователя в PostgreSQL
                user = Users(user_id=user_id)
                session.add(user)

            return {
                "user_id": user_id,
                "tariff_id": None,
                "tariff_expires_at": None
                
            }

    async def get_user(self, user_id: int):
        """Получение пользователя из Postgres"""
        async with self.db_helper.session_only() as session:
            return await self._get_user_internal(session, user_id)

    async def change_user(self, user_id: int, user_data: UserOut):
        """Изменение данных пользователя"""
        async with self.db_helper.transaction() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return None

            update_data = user_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user, key, value)

            session.add(user)
            return user

    async def delete_user(self, user_id: int):
        """Удаление пользователя"""
        async with self.db_helper.transaction() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return False

            await session.delete(user)
            return True
        
    async def _get_user_internal(self, session, user_id: int):
        """Внутренний метод для получения пользователя"""
        result = await session.execute(select(Users).where(Users.user_id == user_id))
        return result.scalar_one_or_none()    