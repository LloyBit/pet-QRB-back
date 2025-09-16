"""Базовый Kafka клиент - чистая инфраструктура"""
import asyncio
import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError

from app.config import settings

logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self._connected = False
    
    async def connect(self, max_retries=10, retry_delay=2):
        """Подключение к Kafka с retry логикой"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Попытка подключения к Kafka (попытка {attempt + 1}/{max_retries})")
                logger.info(f"Kafka URL: {settings.kafka_url}")
                
                # Создаем producer и consumer
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_url,
                    request_timeout_ms=10000,
                    retry_backoff_ms=1000
                )
                self.consumer = AIOKafkaConsumer(
                    bootstrap_servers=settings.kafka_url,
                    group_id="qr_payment_group",
                    request_timeout_ms=10000,
                    retry_backoff_ms=1000
                )
                
                # Пробуем подключиться
                await self.producer.start()
                await self.consumer.start()
                
                # Проверяем, что подключение действительно работает
                await self._test_connection()
                
                self._connected = True
                logger.info("✅ Успешно подключились к Kafka")
                return
                
            except (KafkaConnectionError, KafkaError) as e:
                logger.warning(f"❌ Ошибка подключения к Kafka (попытка {attempt + 1}): {e}")
                await self._cleanup_connections()
                
                if attempt < max_retries - 1:
                    logger.info(f"Повторная попытка через {retry_delay} секунд...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("❌ Исчерпаны все попытки подключения к Kafka")
                    raise KafkaConnectionError(f"Failed to connect to Kafka after {max_retries} attempts")
                    
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка при подключении к Kafka: {e}")
                await self._cleanup_connections()
                raise
    
    async def _test_connection(self):
        """Тестируем подключение, получая метаданные"""
        try:
            # Получаем метаданные кластера для проверки подключения
            metadata = await self.producer.client.fetch_metadata()
            logger.info(f"Kafka cluster metadata: {len(metadata.brokers)} brokers available")
        except Exception as e:
            logger.warning(f"Не удалось получить метаданные Kafka: {e}")
            # Не поднимаем исключение, так как подключение может работать
    
    async def _cleanup_connections(self):
        """Очищаем неудачные подключения"""
        try:
            if self.producer:
                await self.producer.stop()
            if self.consumer:
                await self.consumer.stop()
        except Exception as e:
            logger.debug(f"Ошибка при очистке подключений: {e}")
        finally:
            self.producer = None
            self.consumer = None
            self._connected = False
    
    async def disconnect(self):
        """Отключение от Kafka"""
        try:
            if self.producer:
                await self.producer.stop()
            if self.consumer:
                await self.consumer.stop()
            self._connected = False
            logger.info("✅ Отключились от Kafka")
        except Exception as e:
            logger.error(f"❌ Ошибка при отключении от Kafka: {e}")
        finally:
            self.producer = None
            self.consumer = None
    
    @property
    def is_connected(self):
        """Проверяем, подключены ли мы к Kafka"""
        return self._connected and self.producer is not None and self.consumer is not None