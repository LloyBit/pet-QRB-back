import asyncio
import logging
from typing import Any, Callable, Dict, List
import uuid
from web3 import AsyncWeb3, Web3
from web3.contract import AsyncContract
from web3.providers import AsyncHTTPProvider, WebSocketProvider

from app.config import Settings
from app.infrastructure.models import ContractData

logger = logging.getLogger(__name__)

class AsyncWeb3Service:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.contract_address = AsyncWeb3.to_checksum_address(self.settings.contract_address)
        self.confirmation = self.settings.blockchain_confirmations
        
        self.w3_http = AsyncWeb3(AsyncHTTPProvider(self.settings.network_http_rpc_url))
        self.eth_http = self.w3_http.eth

        self.w3_ws = AsyncWeb3(WebSocketProvider(self.settings.network_ws_rpc_url))
        self.eth_ws = self.w3_ws.eth

        # Автодополнение нулями неправильных bytes переменных
        self.w3_http.strict_bytes_type_checking = False
        self.w3_ws.strict_bytes_type_checking = False

        self.abi = self.settings.contract_abi

        self.contract_ws: AsyncContract = self.w3_ws.eth.contract(
            address=self.contract_address, abi=self.abi
        )
        self.contract_http: AsyncContract = self.w3_http.eth.contract(
            address=self.contract_address, abi=self.abi
        )        

    async def get_pending_payments(self, from_block: int, to_block: int) -> List[Dict[str, Any]]:
        """Догоняющий обход через HTTP для старых блоков"""
        logger.info(f"Fetching events from blocks {from_block} to {to_block} via HTTP")
        try:
            events = await self.contract_http.events.PaymentReceived.get_logs(
                from_block=from_block, to_block=to_block
            )
            parsed = []
            for e in events:
                args = e["args"]
                parsed.append({
                    "payment_id": args["paymentId"].hex(),
                    "from_address": args["from"],
                    "amount_wei": args["amount"],
                    "amount_eth": Web3.from_wei(args["amount"], "ether"),  # <- исправлено
                    "timestamp": args["timestamp"],
                    "block_number": e["blockNumber"],
                    "tx_hash": e["transactionHash"].hex()
                })
            logger.info(f"Found {len(parsed)} payments in historical blocks")
            return parsed
        except Exception as e:
            logger.error(f"Error fetching historical events: {e}")
            return []

    async def get_current_block(self) -> int:
        return await self.eth_http.block_number
    
    async def listen_payments(self, callback: Callable[[Dict[str, Any]], Any]):
        """
        Слушает события PaymentReceived в реальном времени
        и вызывает callback для каждой новой транзакции.
        """
        last_block = await self.get_current_block()
        logger.info(f"Starting WebSocket listener from block {last_block + 1}")

        while True:
            try:
                events = await self.contract_ws.events.PaymentReceived.get_logs(
                    from_block=last_block + 1,
                    to_block="latest"
                )
                for event in events:
                    args = event["args"]
                    parsed_event = {
                        "payment_id": args["paymentId"].hex(),
                        "from_address": args["from"],
                        "amount_wei": args["amount"],
                        "amount_eth": await self.eth_ws.from_wei(args["amount"], "ether"),
                        "timestamp": args["timestamp"],
                        "block_number": event["blockNumber"],
                        "tx_hash": event["transactionHash"].hex()
                    }
                    await callback(parsed_event)

                if events:
                    last_block = max(e["blockNumber"] for e in events)

                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"WebSocket listener error: {e}")
                await asyncio.sleep(5)
    
    def uuid_to_bytes32_web3(self, u: uuid.UUID) -> bytes:
        # UUID → 16 байт, дополняем до 32 байт нулями справа
        return u.bytes.ljust(32, b'\x00')

    def build_calldata(self, data: ContractData) -> str:
        """Генерирует calldata для payForTariff через ABI"""

        payment_hash = Web3.keccak(text=str(data.paymentId)).hex()
        tariff_hash = Web3.keccak(text=str(data.tariffId)).hex()
        price = data.price

        print(payment_hash, tariff_hash, price)
        calldata = self.contract_http.encode_abi(
            "payForTariff",
            args=[payment_hash, tariff_hash, price]
        )
        print(calldata)
        return calldata