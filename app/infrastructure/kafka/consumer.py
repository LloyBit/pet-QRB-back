"""Kafka Consumer сервис - инфраструктура"""
import json
import logging
from typing import Any, Dict, AsyncGenerator

from app.infrastructure.kafka.client import KafkaClient

logger = logging.getLogger(__name__)
class KafkaConsumerService:
    def __init__(self, client: KafkaClient):
        self.client = client
    
    async def consume_messages(self, topic: str) -> AsyncGenerator[Dict[Any, Any], None]:
        """Получение сообщений из топика"""
        if not self.client.is_connected:
            raise RuntimeError("Kafka client is not connected")
        
        self.client.consumer.subscribe([topic])
        async for message in self.client.consumer:
            try:
                data = json.loads(message.value.decode())
                yield data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue