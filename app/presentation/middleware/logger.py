import json
import logging
import time
from typing import Callable
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов и ответов."""
    
    def __init__(self, app: ASGIApp, log_level: str = None):
        super().__init__(app)
        # Используем настройки из конфига, если не передан log_level
        self.log_level = getattr(logging, (log_level or settings.log_level).upper())
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Генерируем уникальный ID для трейсинга запроса
        request_id = str(uuid.uuid4())
        
        # Логируем начало запроса
        start_time = time.time()
        
        # Подготавливаем данные для логирования
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": time.time()
        }
        
        # Логируем входящий запрос
        logger.info(f"Request started: {json.dumps(log_data, default=str)}")
        
        try:
            # Обрабатываем запрос
            response = await call_next(request)
            
            # Вычисляем время выполнения
            process_time = time.time() - start_time
            
            # Логируем успешный ответ
            response_log_data = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "timestamp": time.time()
            }
            
            if response.status_code >= 400:
                logger.warning(f"Request completed with warning: {json.dumps(response_log_data, default=str)}")
            else:
                logger.info(f"Request completed successfully: {json.dumps(response_log_data, default=str)}")
            
            # Добавляем request_id в заголовки ответа для трейсинга
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Логируем ошибку
            process_time = time.time() - start_time
            error_log_data = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time": round(process_time, 4),
                "timestamp": time.time()
            }
            
            logger.error(f"Request failed: {json.dumps(error_log_data, default=str)}")
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Получает реальный IP клиента с учетом прокси."""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"