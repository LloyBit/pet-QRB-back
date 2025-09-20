from enum import Enum

class EventStatus(str, Enum):
    """Статусы обработки событий"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class EventPriority(str, Enum):
    """Приоритеты событий"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"