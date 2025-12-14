#!/bin/bash
set -e

# Создать директорию для базы данных
mkdir -p /app/data
chmod 777 /app/data

# Убедиться, что /app/data доступен для записи
echo "Checking /app/data write permissions..."
touch /app/data/.test_write && rm /app/data/.test_write && echo "✓ /app/data is writable" || echo "⚠ Warning: /app/data may not be writable"

# Запустить приложение
echo "Starting application..."
exec python app.py

