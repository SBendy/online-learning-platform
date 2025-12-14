#!/bin/bash

# Скрипт для проверки доступности сервисов

echo "Проверка доступности сервисов..."
echo ""

# Проверка Auth Service
echo "1. Проверка Auth Service (http://localhost:5001/health)..."
if curl -s http://localhost:5001/health > /dev/null; then
    echo "   ✅ Auth Service доступен"
else
    echo "   ❌ Auth Service недоступен"
fi

# Проверка Course Service
echo "2. Проверка Course Service (http://localhost:5002/health)..."
if curl -s http://localhost:5002/health > /dev/null; then
    echo "   ✅ Course Service доступен"
else
    echo "   ❌ Course Service недоступен"
fi

# Проверка Learning Service
echo "3. Проверка Learning Service (http://localhost:5003/health)..."
if curl -s http://localhost:5003/health > /dev/null; then
    echo "   ✅ Learning Service доступен"
else
    echo "   ❌ Learning Service недоступен"
fi

# Проверка API Gateway
echo "4. Проверка API Gateway (http://localhost:5000/health)..."
if curl -s http://localhost:5000/health > /dev/null; then
    echo "   ✅ API Gateway доступен"
else
    echo "   ❌ API Gateway недоступен"
fi

# Проверка Frontend Service
echo "5. Проверка Frontend Service (http://localhost:8080/health)..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "   ✅ Frontend Service доступен"
else
    echo "   ❌ Frontend Service недоступен"
fi

echo ""
echo "Проверка завершена!"

