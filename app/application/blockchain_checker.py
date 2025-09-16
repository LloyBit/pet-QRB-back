import hashlib
import logging
from typing import Any, Dict, Optional

from web3 import Web3
from web3.exceptions import InvalidAddress, TransactionNotFound

from app.config import settings

logger = logging.getLogger(__name__)

class BlockchainChecker:
    """Сервис для проверки транзакций в блокчейне Ethereum."""
    
    def __init__(self, rpc_url: str, wallet_address: str, required_confirmations: int = 3):
        """
        Инициализация сервиса проверки блокчейна.
        
        Args:
            rpc_url: URL RPC узла Ethereum (например, Infura, Alchemy)
            wallet_address: Адрес кошелька для проверки входящих транзакций
            required_confirmations: Количество подтверждений для валидации транзакции
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.required_confirmations = required_confirmations
        
        # Валидируем и устанавливаем адрес кошелька
        try:
            self.wallet_address = Web3.to_checksum_address(wallet_address)
        except (InvalidAddress, ValueError) as e:
            logger.error(f"Invalid wallet address: {wallet_address}")
            # raise ValueError(f"Invalid wallet address format: {wallet_address}. Must be a valid Ethereum address.")
            self.wallet_address = None  # Не роняем приложение, но адрес невалидный
        
        # Проверяем подключение
        if not self.w3.is_connected():
            # raise ConnectionError("Failed to connect to Ethereum RPC")
            logger.error("Failed to connect to Ethereum RPC")
        
        logger.info(f"Blockchain checker initialized for wallet: {self.wallet_address}")
    
    async def check_transaction_confirmation(self, payment_id: str, **kwargs):
        # Конвертируем payment_id в bytes32
        payment_hash = hashlib.sha256(payment_id.encode()).digest()[:32]
        
        # Ищем событие PaymentReceived
        contract = self.w3.eth.contract(
            address=settings.contract_address,
            abi=settings.contract_abi
        )
        
        # Фильтруем события по payment_hash
        event_filter = contract.events.PaymentReceived.create_filter(
            fromBlock='latest',
            argument_filters={'paymentId': payment_hash}
        )
        
        events = event_filter.get_all_entries()
        
        for event in events:
            if event.args.paymentId == payment_hash:
                return True
        
        return False
    
    async def _validate_transaction(
        self, 
        tx: Dict[str, Any], 
        expected_amount: int, 
        from_address: Optional[str],
        payment_id: str
    ) -> bool:
        """
        Валидирует транзакцию по заданным критериям.
        
        Args:
            tx: Транзакция из блокчейна
            expected_amount: Ожидаемая сумма
            from_address: Ожидаемый адрес отправителя
            payment_id: ID платежа для дополнительной валидации
            
        Returns:
            bool: True если транзакция соответствует критериям
        """
        try:
            # Проверяем, что транзакция направлена на наш кошелек
            if tx.to and tx.to.lower() != self.wallet_address.lower():
                return False
            
            # Проверяем сумму
            if tx.value != expected_amount:
                return False
            
            # Проверяем адрес отправителя если указан
            if from_address and tx['from'].lower() != from_address.lower():
                return False
            
            # Проверяем статус транзакции
            if tx.get('status') == 0:  # 0 = failed, 1 = successful
                return False
            
            # Дополнительная валидация по payment_id может быть добавлена здесь
            # Например, проверка данных транзакции (input data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating transaction {tx.hash.hex()}: {e}")
            return False
    
    async def get_transaction_details(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """ Получает детали транзакции по хешу. """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                'hash': tx_hash,
                'from': tx['from'],
                'to': tx['to'],
                'value': tx['value'],
                'gas_used': tx_receipt['gasUsed'],
                'status': tx_receipt['status'],
                'block_number': tx['blockNumber'],
                'timestamp': self.w3.eth.get_block(tx['blockNumber']).timestamp
            }
            
        except TransactionNotFound:
            logger.warning(f"Transaction not found: {tx_hash}")
            return None
        except Exception as e:
            logger.error(f"Error getting transaction details for {tx_hash}: {e}")
            return None
    
    def get_wallet_balance(self) -> int:
        """ Получает баланс кошелька в wei """
        try:
            return self.w3.eth.get_balance(self.wallet_address)
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return 0
