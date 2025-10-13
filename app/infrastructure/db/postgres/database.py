from contextlib import asynccontextmanager
from contextlib import contextmanager
import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

class AsyncDatabaseHelper:
    """Асинхронный хелпер для работы с БД и управлением сессиями."""

    def __init__(self, database_url: str | None = None):
        self.database_url = (database_url or settings.db_url).replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        self.engine = None
        self.async_session_factory = None
        self.Base = declarative_base()

    async def connect(self):
        """Создает подключение и инициализирует пул соединений."""
        if self.engine:
            return  # уже инициализирован

        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30
        )
        self.async_session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    @asynccontextmanager
    async def session_only(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для работы с сессией без автоматического коммита."""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер с автоматическим коммитом."""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self):
        """Закрывает соединения и пул."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session_factory = None


class SyncDatabaseHelper:
    """Синхронный хелпер для работы с БД и управлением сессиями (для Celery)."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.db_url
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()

    def connect(self):
        """Создает движок и фабрику сессий."""
        if self.engine:
            return  # уже инициализировано

        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30,
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    @contextmanager
    def session_only(self):
        """Контекстный менеджер для работы с сессией без автокоммита."""
        if not self.SessionLocal:
            raise RuntimeError("DatabaseHelper not connected. Call connect() first.")

        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def transaction(self):
        """Контекстный менеджер с автоматическим коммитом."""
        if not self.SessionLocal:
            raise RuntimeError("DatabaseHelper not connected. Call connect() first.")

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        """Закрывает движок и соединения."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None
