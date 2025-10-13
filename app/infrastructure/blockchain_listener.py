import asyncio
import logging
from app.config import settings
from app.infrastructure.db.redis.repositories import MigrationRepository
from app.infrastructure.db.redis.redis import asyncio_redis_client
from app.infrastructure.db.postgres.repositories import PaymentRepository
from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.infrastructure.blockchain import AsyncWeb3Service
from typing import Dict

logger = logging.getLogger(__name__)

class PaymentPoller:
    def __init__(self):
        self.db_helper = AsyncDatabaseHelper(settings.db_url)
        self.migration_repo = MigrationRepository(asyncio_redis_client)
        self.payment_repo = PaymentRepository(self.db_helper)
        self.web3_service = AsyncWeb3Service(
            ws_url=settings.network_ws_rpc_url,
            http_url=settings.network_http_rpc_url,
            contract_address=settings.admin_wallet_address
        )
        self.last_block = None
        self.queue: asyncio.Queue[Dict] = asyncio.Queue()  # очередь событий

    async def start(self):
        await self.db_helper.connect()

        # Получаем последнюю обработанную точку
        self.last_block = await self.get_last_processed_block() or 0

        # Запускаем все три задачи параллельно
        await asyncio.gather(
            self.catch_up_pending_transactions(),
            self.listen_new_transactions(),
            self.process_queue()  # единый обработчик очереди
        )

    async def get_last_processed_block(self) -> int:
        last_tx = await self.migration_repo.get_last_block_number()
        return last_tx

    async def catch_up_pending_transactions(self):
        current_block = await self.web3_service.get_current_block()
        if self.last_block < current_block:
            logger.info(f"Catching up from block {self.last_block + 1} to {current_block}")
            txs = await self.web3_service.get_pending_payments(
                from_block=self.last_block + 1,
                to_block=current_block
            )
            for tx in txs:
                await self.queue.put(tx)  # кладём в очередь

            self.last_block = current_block

    async def listen_new_transactions(self):
        async def callback(tx: Dict):
            await self.queue.put(tx)  # кладём новые события в очередь

        await self.web3_service.listen_payments(callback)

    async def process_queue(self):
        while True:
            tx = await self.queue.get()
            try:
                await self.process_payment(tx)
            except Exception as e:
                logger.error(f"Error processing payment {tx.get('tx_hash')}: {e}")
            finally:
                # Обновляем last_block
                self.last_block = max(self.last_block or 0, tx["block_number"])
                self.queue.task_done()

    async def process_payment(self, tx: Dict):
        tx_hash = tx["tx_hash"]
        valid_tx = await self.migration_repo.find_transaction(tx_hash)
        if valid_tx:
            await self.payment_repo.migrate_payment(valid_tx)
            await self.migration_repo.delete_transaction(valid_tx)
            logger.info(f"Processed payment {tx_hash}")

if __name__ == "__main__":
    poller = PaymentPoller()
    asyncio.run(poller.start())
