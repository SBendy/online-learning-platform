#!/bin/bash

# Скрипт для развертывания приложения в Docker Swarm

STACK_NAME="learning-platform"

# Проверка, что Docker Swarm инициализирован
echo "Проверка Docker Swarm..."
if ! docker info | grep -q "Swarm: active"; then
    echo "❌ Docker Swarm не активен"
    echo ""
    echo "Инициализация Docker Swarm..."
    docker swarm init
    echo ""
fi

echo "✅ Docker Swarm активен"
echo ""

# Проверка секрета JWT
echo "Проверка секрета JWT..."
if ! docker secret ls | grep -q "jwt_secret"; then
    echo "Создание секрета JWT..."
    echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
    echo "✅ Секрет создан"
else
    echo "✅ Секрет уже существует"
fi
echo ""

# Сборка образов
echo "Сборка Docker образов..."
./build-images.sh
echo ""

# Развертывание stack
echo "Развертывание stack '$STACK_NAME'..."
docker stack deploy -c docker-compose.swarm.yml $STACK_NAME

echo ""
echo "Развертывание завершено!"
echo ""
echo "Проверка статуса:"
docker stack services $STACK_NAME
echo ""
echo "Проверка сервисов:"
docker service ls
echo ""
echo "Для просмотра логов используйте:"
echo "docker service logs -f ${STACK_NAME}_auth-service"
echo ""
echo "Приложение будет доступно на http://localhost:8080"

