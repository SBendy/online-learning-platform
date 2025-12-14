# Развертывание в Kubernetes

## Предварительные требования

- Kubernetes кластер (minikube, kind, или облачный кластер)
- kubectl настроен и подключен к кластеру
- Docker образы собраны и доступны в registry

## Быстрое развертывание

### 1. Сборка Docker образов

```bash
# Linux/Mac
./build-images.sh

# Windows
build-images.bat
```

### 2. Загрузка образов в registry (если используется удаленный кластер)

```bash
# Пример для Docker Hub
docker tag learning-platform/auth-service:latest yourusername/auth-service:latest
docker push yourusername/auth-service:latest

# И так для всех сервисов:
# - course-service
# - learning-service
# - api-gateway
# - frontend-service
```

### 3. Обновление образов в манифестах (если используется удаленный registry)

Отредактируйте файлы deployment и замените `learning-platform/` на ваш registry:
- `yourregistry.com/auth-service:latest`
- `yourregistry.com/course-service:latest`
- и т.д.

### 4. Развертывание в Kubernetes

```bash
cd k8s

# Использование скрипта
./deploy.sh

# Или вручную
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f persistent-volumes.yaml
kubectl apply -f auth-service-deployment.yaml
kubectl apply -f course-service-deployment.yaml
kubectl apply -f learning-service-deployment.yaml
kubectl apply -f api-gateway-deployment.yaml
kubectl apply -f frontend-service-deployment.yaml
kubectl apply -f ingress.yaml
```

### 5. Использование Kustomize (альтернатива)

```bash
kubectl apply -k .
```

## Проверка статуса

```bash
# Проверка подов
kubectl get pods -n learning-platform

# Проверка сервисов
kubectl get services -n learning-platform

# Проверка PersistentVolumes
kubectl get pv -n learning-platform
kubectl get pvc -n learning-platform

# Просмотр логов
kubectl logs -f deployment/auth-service -n learning-platform
kubectl logs -f deployment/course-service -n learning-platform
kubectl logs -f deployment/learning-service -n learning-platform
kubectl logs -f deployment/api-gateway -n learning-platform
kubectl logs -f deployment/frontend-service -n learning-platform
```

## Доступ к приложению

### Вариант 1: Port Forwarding

```bash
# Frontend Service
kubectl port-forward -n learning-platform service/frontend-service 8080:80

# API Gateway
kubectl port-forward -n learning-platform service/api-gateway 5000:5000
```

Откройте браузер: http://localhost:8080

### Вариант 2: LoadBalancer (если поддерживается)

```bash
kubectl get service frontend-service -n learning-platform
# Используйте EXTERNAL-IP из вывода
```

### Вариант 3: Ingress

Если у вас настроен Ingress Controller (например, nginx-ingress):

```bash
# Добавить в /etc/hosts (Linux/Mac) или C:\Windows\System32\drivers\etc\hosts (Windows)
<INGRESS_IP> learning-platform.local
```

Откройте браузер: http://learning-platform.local

## Масштабирование

```bash
# Увеличить количество реплик
kubectl scale deployment auth-service --replicas=3 -n learning-platform
kubectl scale deployment course-service --replicas=3 -n learning-platform
kubectl scale deployment learning-service --replicas=3 -n learning-platform
kubectl scale deployment api-gateway --replicas=3 -n learning-platform
kubectl scale deployment frontend-service --replicas=3 -n learning-platform
```

## Обновление приложения

```bash
# После обновления образов
kubectl rollout restart deployment/auth-service -n learning-platform
kubectl rollout restart deployment/course-service -n learning-platform
kubectl rollout restart deployment/learning-service -n learning-platform
kubectl rollout restart deployment/api-gateway -n learning-platform
kubectl rollout restart deployment/frontend-service -n learning-platform
```

## Удаление

```bash
# Удалить все ресурсы
kubectl delete namespace learning-platform

# Или удалить по отдельности
kubectl delete -f .
```

## Базы данных SQLite

Все сервисы используют SQLite базы данных, которые хранятся в PersistentVolumes:
- `auth.db` - база данных Auth Service
- `courses.db` - база данных Course Service  
- `learning.db` - база данных Learning Service

Данные сохраняются между перезапусками подов благодаря PersistentVolumes.

## Troubleshooting

### Проблема: Поды не запускаются

```bash
# Проверить статус подов
kubectl describe pod <pod-name> -n learning-platform

# Проверить логи
kubectl logs <pod-name> -n learning-platform
```

### Проблема: Сервисы не могут связаться друг с другом

Проверьте, что все сервисы находятся в одном namespace и используют правильные имена сервисов.

### Проблема: PersistentVolume не монтируется

```bash
# Проверить статус PVC
kubectl describe pvc auth-pvc -n learning-platform

# Убедиться, что директории созданы на узлах (для hostPath)
# На каждом узле кластера:
sudo mkdir -p /data/learning-platform/{auth,course,learning}
sudo chmod 777 /data/learning-platform/{auth,course,learning}
```

