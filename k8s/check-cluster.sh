#!/bin/bash

# Скрипт для проверки подключения к Kubernetes кластеру

echo "Проверка подключения к Kubernetes кластеру..."
echo ""

# Проверка kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl не установлен"
    echo "Установите kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo "✅ kubectl установлен"
echo ""

# Проверка текущего контекста
echo "Текущий контекст:"
kubectl config current-context
echo ""

# Проверка подключения к кластеру
echo "Проверка подключения к кластеру..."
if kubectl cluster-info &> /dev/null; then
    echo "✅ Подключение к кластеру успешно"
    echo ""
    echo "Информация о кластере:"
    kubectl cluster-info
    echo ""
    echo "Узлы кластера:"
    kubectl get nodes
else
    echo "❌ Не удалось подключиться к кластеру"
    echo ""
    echo "Доступные контексты:"
    kubectl config get-contexts
    echo ""
    echo "Для настройки локального кластера см. setup-local-cluster.md"
    echo ""
    echo "Или используйте Docker Compose вместо Kubernetes:"
    echo "docker-compose up --build"
    exit 1
fi

