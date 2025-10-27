""" Точка входа в процесс-поллер транзакций из блокчейна """
import asyncio
import logging

from app.config import Settings
from app.infrastructure.container import InfrastructureContainer
from app.application.container import ServicesContainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    settings = Settings()
    infra = InfrastructureContainer(settings=settings)
    services = ServicesContainer(infra=infra, settings=settings)
    
    await infra.db_helper.connect()
    async with infra.blockchain_helper.w3_ws as w3:
        logger.info("WebSocket connection established")
        
        # Создаём поллер и стартуем его
        poller = services.blockchain_listener
        await poller.start()

    logger.info("WebSocket connection closed, exiting...")

    poller = services.blockchain_listener
    
    await poller.start()

if __name__ == "__main__":
    asyncio.run(main())
