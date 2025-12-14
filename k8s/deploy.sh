#!/bin/bash

# Скрипт для развертывания приложения в Kubernetes

# Проверка подключения к кластеру
echo "Проверка подключения к Kubernetes кластеру..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Ошибка: Не удалось подключиться к Kubernetes кластеру"
    echo ""
    echo "Проверьте:"
    echo "1. Запущен ли Kubernetes кластер (minikube, Docker Desktop, kind)"
    echo "2. Правильно ли настроен kubectl: kubectl config get-contexts"
    echo ""
    echo "Для настройки локального кластера см. setup-local-cluster.md"
    echo "Или используйте Docker Compose: docker-compose up --build"
    exit 1
fi

echo "✅ Подключение к кластеру успешно"
echo ""

echo "Развертывание микросервисной платформы в Kubernetes..."

# Создание namespace
echo "Создание namespace..."
kubectl apply -f namespace.yaml

# Создание ConfigMap
echo "Создание ConfigMap..."
kubectl apply -f configmap.yaml

# Создание PersistentVolumes
echo "Создание PersistentVolumes..."
kubectl apply -f persistent-volumes.yaml

# Создание Deployments и Services
echo "Создание Deployments и Services..."
kubectl apply -f auth-service-deployment.yaml
kubectl apply -f course-service-deployment.yaml
kubectl apply -f learning-service-deployment.yaml
kubectl apply -f api-gateway-deployment.yaml
kubectl apply -f frontend-service-deployment.yaml

# Создание Ingress (опционально)
echo "Создание Ingress..."
kubectl apply -f ingress.yaml

echo ""
echo "Развертывание завершено!"
echo ""
echo "Проверка статуса:"
kubectl get pods -n learning-platform
kubectl get services -n learning-platform
echo ""
echo "Для просмотра логов используйте:"
echo "kubectl logs -f deployment/auth-service -n learning-platform"

