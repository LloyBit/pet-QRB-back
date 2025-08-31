from functools import wraps
from fastapi import HTTPException
from typing import Callable
import logging

logger = logging.getLogger(__name__)

def handle_errors(default_message: str = "Internal server error"):
    """Декоратор для обработки ошибок в API endpoints."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise HTTPException(status_code=500, detail=default_message)
        return wrapper
    return decorator
