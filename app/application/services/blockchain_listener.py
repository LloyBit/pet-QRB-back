import asyncio
import logging
from typing import Dict

from app.config import Settings
from app.infrastructure.blockchain import AsyncWeb3Service
from app.infrastructure.db.redis.repositories import TransactionsRepository as TransactionsRepositoryRedis
from app.infrastructure.db.postgres.repositories.transactions import TransactionsRepository as TransactionsRepositoryPostgres
from app.application.services.payment_processor import TransactionService

logging.basicConfig(
    level=logging.INFO,  # уровень логирования
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

class PaymentPoller:
    def __init__(
            self, 
            settings: Settings, 
            redis_repository: TransactionsRepositoryRedis, 
            transactions_pg: TransactionsRepositoryPostgres, 
            blockchain_helper: AsyncWeb3Service, 
            transaction_service: TransactionService
        ):
        self.settings = settings
        self.redis_repository = redis_repository
        self.transactions_pg = transactions_pg
        self.blockchain_helper = blockchain_helper
        self.transaction_service = transaction_service
        
        self.last_block = None
        self.queue: asyncio.Queue[Dict] = asyncio.Queue()  # очередь событий

    async def start(self):
    # Получаем последнюю обработанную точку
        self.last_block = await self.get_last_processed_block() or 0
        
        # Запускаем все три задачи параллельно
        await asyncio.gather(
            self.catch_up_pending_transactions(),
            self.listen_new_transactions(),
            self.process_queue()  # единый обработчик очереди
        )
    
    async def get_last_processed_block(self) -> int:
        last_tx = await self.redis_repository.get_last_block_number()
        return last_tx
    
    async def catch_up_pending_transactions(self):
        current_block = await self.blockchain_helper.get_current_block()
        if self.last_block < current_block:
            logger.info(f"Catching up from block {self.last_block + 1} to {current_block}")
            txs = await self.blockchain_helper.get_pending_payments(
                from_block=self.last_block + 1,
                to_block=current_block
            )
            for tx in txs:
                await self.queue.put(tx)  # кладём в очередь

            self.last_block = current_block

    async def listen_new_transactions(self):
        async def callback(tx: Dict):
            await self.queue.put(tx)  # кладём новые события в очередь

        await self.blockchain_helper.listen_payments(callback)

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
        # TODO: error прописать
        valid_tx = await self.redis_repository.find_transaction(tx_hash)
        if valid_tx:
            await self.transaction_service.migrate_transaction(tx_hash)
            await self.redis_repository.delete_transaction(tx_hash)
            logger.info(f"Processed payment {tx_hash}")
