import logging
import sys
import os
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
        # Определяем путь к корню проекта (рядом с папкой app)
        project_root = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(project_root, "..", ".."))
        log_file_path = os.path.join(root_dir, "logs", "app.log")

        # Создаем директорию для логов если её нет
        os.makedirs(os.path.join(root_dir, "logs"), exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Все логи в файл
        file_handler.setFormatter(file_formatter)
        file_handler.set_name("file_handler")
        root_logger.addHandler(file_handler)
        
        print(f"✅ Log file created at: {log_file_path}")
        
    except Exception as e:
        print(f"❌ Warning: Could not create file handler: {e}")
    
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