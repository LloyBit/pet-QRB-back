"""Kafka Producer сервис - инфраструктура"""
import json
from typing import Any, Dict

from .client import KafkaClient

class KafkaProducerService:
    def __init__(self, client: KafkaClient):
        self.client = client
    
    async def send_message(self, topic: str, message: Dict[Any, Any]):
        """Отправка сообщения - техническая операция"""
        await self.client.producer.send_and_wait(
            topic, 
            json.dumps(message).encode()
        )