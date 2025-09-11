import redis.exceptions
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.db.postgres.schemas import Users
from ..infrastructure.db.redis.redis import redis_client
from ..models import PaymentState, UserOut


class UsersService:
    '''Сервис для работы с пользователями.'''
    def __init__(self, session: AsyncSession):
        self.session = session

    async def init_user(self, user_id: int):
        """Инициализация пользователя в Redis"""
        try:
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

    async def get_user(self, user_id: int):
        """Получение пользователя из Postgres"""
        result = await self.session.execute(select(Users).where(Users.user_id == user_id))
        return result.scalar_one_or_none()

    async def change_user(self, user_id: int, user_data: UserOut):
        """Изменение данных пользователя"""
        result = await self.session.execute(select(Users).where(Users.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int):
        """Удаление пользователя"""
        result = await self.session.execute(select(Users).where(Users.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        await self.session.delete(user)
        await self.session.commit()
        return True
