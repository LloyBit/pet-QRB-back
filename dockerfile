FROM python:3.13-slim as builder

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Копируем только нужные для установки файлы
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv pip compile pyproject.toml --output-file requirements.txt && \
    uv pip install --system -r requirements.txt

# Копируем остальные файлы
COPY . .

# Финальный образ
FROM python:3.13-slim

WORKDIR /app

# Runtime зависимости
RUN apt-get update && apt-get install -y libpq5 curl && rm -rf /var/lib/apt/lists/*

# Копируем установленные пакеты
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем код приложения
COPY --from=builder /app /app

# Критически важные настройки путей
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Запуск приложения
CMD ["sh", "-c", "cd /app && python -m app.infrastructure.db.postgres.init_db && uvicorn main:app --host 0.0.0.0 --port 8000"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]