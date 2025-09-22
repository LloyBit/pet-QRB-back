"""Kafka Producer сервис - инфраструктура"""
import json
import logging
from typing import Any, Dict

from app.infrastructure.kafka.client import KafkaClient

logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(self, client: KafkaClient):
        self.client = client
    
    async def send_message(self, topic: str, message: Dict[Any, Any]) -> bool:
        """Отправка сообщения - техническая операция"""
        if not self.client.is_connected:
            logger.error("Kafka client is not connected")
            return False
        
        try:
            await self.client.producer.send_and_wait(
                topic, 
                json.dumps(message).encode()
            )
            logger.debug(f"Message sent to topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to topic {topic}: {e}")
            return False