import logging
import os
import sys
from pathlib import Path

from app.config import settings

def setup_logging():
    """Настраивает логирование для приложения."""
    
    # Создаем форматтеры
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень для всех обработчиков
    
    # Очищаем существующие обработчики
    root_logger.handlers.clear()
    
    # Создаем обработчик для консоли (только WARNING и выше)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Только WARNING и выше
    console_handler.setFormatter(console_formatter)
    console_handler.set_name("console_handler")
    root_logger.addHandler(console_handler)
    
    # Создаем обработчик для файла (все логи)
    try:
        # Более надежный способ определения корня проекта
        # Ищем папку с main.py или pyproject.toml
        current_file = Path(__file__).resolve()
        project_root = None
        
        # Поднимаемся по директориям вверх, пока не найдем корень проекта
        for parent in current_file.parents:
            if (parent / "main.py").exists() or (parent / "pyproject.toml").exists():
                project_root = parent
                break
        
        if project_root is None:
            # Fallback: используем старый способ
            project_root = current_file.parent.parent.parent
        
        logs_dir = project_root / "logs"
        log_file_path = logs_dir / "app.log"

        # Создаем директорию для логов если её нет
        logs_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Все логи в файл
        file_handler.setFormatter(file_formatter)
        file_handler.set_name("file_handler")
        root_logger.addHandler(file_handler)
        
        print(f"✅ Log file created at: {log_file_path}")
        print(f"📁 Project root detected as: {project_root}")
        
    except Exception as e:
        print(f"❌ Warning: Could not create file handler: {e}")
        # Если не можем создать файловый логгер, продолжаем только с консольным
        print("📝 Continuing with console logging only")
    
    # Настраиваем логирование для сторонних библиотек
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Логируем успешную инициализацию
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized successfully")
    logger.warning("⚠️  Console logging: WARNING and above")
    logger.debug("🔍 File logging: ALL levels (this should only appear in file)")
    logger.error("❌ Error logging: ERROR and above")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Получить логгер с указанным именем."""
    return logging.getLogger(name)