""" Точка входа в основное приложение """
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.presentation.api import router as all_routers
from app.config import Settings
from app.presentation.middleware import ExceptionMiddleware, LoggingMiddleware
from app.application.container import ServicesContainer
from app.infrastructure.container import InfrastructureContainer

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик событий жизненного цикла FastAPI"""
    # Startup
    
    # Создаем контейнер репозиториев
    app.state.infra = InfrastructureContainer(settings=settings)
    await app.state.infra.db_helper.connect()
    
    # Билдим образ контейнера сервисов
    app.state.service_container = ServicesContainer(infra=app.state.infra, settings=settings)

    yield
    
    # Shutdown
    
    # Закрываем соединения
    await app.state.infra.db_helper.close()
    
app = FastAPI(title="QR-Blockchain Server", version="1.0.0", lifespan=lifespan)

# Добавляем middleware. Порядок важен: ExceptionMiddleware должен быть первым
app.add_middleware(ExceptionMiddleware, debug=settings.debug)
app.add_middleware(LoggingMiddleware, log_level=settings.log_level)

# Подключаем предварительно собранные роуты
app.include_router(all_routers)
