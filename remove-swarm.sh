#!/bin/bash

STACK_NAME="learning-platform"

echo "Удаление stack '$STACK_NAME'..."
docker stack rm $STACK_NAME

echo ""
echo "Ожидание завершения удаления..."
sleep 10

echo ""
echo "Проверка статуса:"
docker stack services $STACK_NAME 2>/dev/null || echo "Stack удален"

echo ""
echo "Удаление секрета JWT (опционально):"
echo "docker secret rm jwt_secret"

