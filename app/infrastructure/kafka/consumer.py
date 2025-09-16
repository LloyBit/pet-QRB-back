"""Kafka Consumer сервис - инфраструктура"""
import json
from typing import Any, Dict

from .client import KafkaClient

class KafkaConsumerService:
    def __init__(self, client: KafkaClient):
        self.client = client
    
    async def consume_message(self, topic: str, message: Dict[Any, Any]):
        """Отправка сообщения - техническая операция"""
        await self.client.consumer.consume_and_wait(
            topic, 
            json.dumps(message).encode()
        )