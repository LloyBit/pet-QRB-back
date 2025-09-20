import json
import logging
import traceback
from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)

class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware для централизованной обработки исключений."""
    
    def __init__(self, app: ASGIApp, debug: bool = None):
        super().__init__(app)
        # Используем настройки из конфига, если не передан debug
        self.debug = debug if debug is not None else getattr(settings, 'debug', False)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
            
        except HTTPException as http_exc:
            # Обрабатываем HTTP исключения FastAPI
            return await self._handle_http_exception(request, http_exc)
            
        except StarletteHTTPException as starlette_exc:
            # Обрабатываем HTTP исключения Starlette
            return await self._handle_http_exception(request, starlette_exc)
            
        except Exception as exc:
            # Обрабатываем все остальные исключения
            return await self._handle_generic_exception(request, exc)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Обрабатывает HTTP исключения."""
        error_data = {
            "error": "HTTP Error",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
        
        # Логируем HTTP ошибки
        logger.warning(f"HTTP Exception: {json.dumps(error_data, default=str)}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_data
        )
    
    async def _handle_generic_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Обрабатывает общие исключения."""
        error_data = {
            "error": "Internal Server Error",
            "status_code": 500,
            "detail": "An unexpected error occurred",
            "path": request.url.path,
            "method": request.method
        }
        
        # В режиме отладки добавляем детали ошибки
        if self.debug:
            error_data.update({
                "detail": str(exc),
                "traceback": traceback.format_exc()
            })
        
        # Логируем ошибку с полным стектрейсом
        logger.error(
            f"Unhandled Exception: {str(exc)}\n"
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        return JSONResponse(
            status_code=500,
            content=error_data
        )