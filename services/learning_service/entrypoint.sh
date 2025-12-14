#!/bin/bash
set -e

# Убедиться, что /app доступен для записи
echo "Checking /app write permissions..."
touch /app/.test_write && rm /app/.test_write && echo "✓ /app is writable" || echo "⚠ Warning: /app may not be writable"

# Запустить приложение
echo "Starting application..."
exec python app.py

