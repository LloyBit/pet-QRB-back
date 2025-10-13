import asyncio
import logging
from typing import Any, Callable, Dict, List

from web3 import AsyncWeb3
from web3.contract import AsyncContract

from app.config import settings

logger = logging.getLogger(__name__)

class AsyncWeb3Service:
    def __init__(self, ws_url: str, http_url: str, contract_address: str):
        # Асинхронный WS клиент
        self.w3 = AsyncWeb3.WebSocketProvider(ws_url)
        self.w3_http = AsyncWeb3.AsyncHTTPProvider(http_url)

        self.eth_ws = AsyncWeb3(self.w3).eth  # асинхронный eth
        self.eth_http = AsyncWeb3(self.w3_http).eth

        self.contract_address = AsyncWeb3.to_checksum_address(contract_address)
        self.confirmation = settings.blockchain_confirmations

        self.abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "bytes32", "name": "paymentId", "type": "bytes32"},
                    {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
                ],
                "name": "PaymentReceived",
                "type": "event",
            },
        ]

        self.contract_ws: AsyncContract = AsyncWeb3(self.w3).eth.contract(
            address=self.contract_address, abi=self.abi
        )
        self.contract_http: AsyncContract = AsyncWeb3(self.w3_http).eth.contract(
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
                    "amount_eth": await self.eth_http.from_wei(args["amount"], "ether"),
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