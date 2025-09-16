import redis.exceptions
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.db.postgres.schemas import Users
from ..infrastructure.db.postgres.database import db_helper
from ..infrastructure.db.redis.redis import redis_client
from ..models import PaymentState, UserOut


class UsersService:
    '''Сервис для работы с пользователями.'''
    async def init_user(self, user_id: int):
        """Инициализация пользователя в Redis и PostgreSQL"""
        async with db_helper.transaction() as session:
            try:
                # Проверяем, существует ли пользователь в PostgreSQL
                existing_user = await self._get_user_internal(session, user_id)
                if not existing_user:
                    # Создаем пользователя в PostgreSQL
                    user = Users(user_id=user_id)
                    session.add(user)
                    # Коммит произойдет автоматически в контекстном менеджере
                
                # Инициализируем пользователя в Redis
                await redis_client.hset(
                    f"user:{user_id}",
                    mapping={
                        "tariff_id": "basic",
                        "payment_state": PaymentState.NOT_PAID.value,
                    },
                )
            except redis.exceptions.ConnectionError:
                print(f"Warning: Redis not available, skipping user {user_id} initialization")

            return {
                "user_id": user_id,
                "tariff": "basic",
                "payment_state": PaymentState.NOT_PAID,
            }

    async def ensure_user_exists(self, user_id: int) -> bool:
        """Убеждается, что пользователь существует в PostgreSQL"""
        async with db_helper.transaction() as session:
            existing_user = await self._get_user_internal(session, user_id)
            if not existing_user:
                user = Users(user_id=user_id)
                session.add(user)
                return True
            return True

    async def get_user(self, user_id: int):
        """Получение пользователя из Postgres"""
        async with db_helper.session_only() as session:
            return await self._get_user_internal(session, user_id)

    async def _get_user_internal(self, session, user_id: int):  # ← Переименовали
        """Внутренний метод для получения пользователя"""
        result = await session.execute(select(Users).where(Users.user_id == user_id))
        return result.scalar_one_or_none()

    async def change_user(self, user_id: int, user_data: UserOut):
        """Изменение данных пользователя"""
        async with db_helper.transaction() as session:
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
        async with db_helper.transaction() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return False

            await session.delete(user)
            return True