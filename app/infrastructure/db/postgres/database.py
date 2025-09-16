# TODO: Вынести в класс DatabaseHelper

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings

class DatabaseHelper:
    def __init__(self):
        self.database_url = settings.db_url.replace("postgresql://", "postgresql+asyncpg://")
        # Конфигурируем движок с пулом соединений для асинхронного использования
        self.engine = create_async_engine(
            self.database_url, 
            echo=False, 
            pool_size=10, 
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30
            )
        # Создаем фабрику сессий с конфигурацией пула
        self.async_session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        # Создаем базу данных
        self.Base = declarative_base()

    @asynccontextmanager
    async def session_only(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер только для сессии без автоматического коммита"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        ''' Функция для создания транзакции '''
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()  # Автоматический коммит
            except Exception:
                await session.rollback()
                raise

    async def close(self):
        """Мягкое закрытие соединения с базой данных"""
        await self.engine.dispose()
        
db_helper = DatabaseHelper()