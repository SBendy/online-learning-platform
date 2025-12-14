# Руководство по развертыванию

## Варианты развертывания

### 1. Docker Compose (Локально/Dev)

Самый простой способ для локальной разработки и тестирования.

```bash
docker-compose up --build
```

Приложение будет доступно на http://localhost:8080

**Особенности:**
- Все сервисы в одной сети
- SQLite базы данных в Docker volumes
- Автоматический healthcheck
- Зависимости между сервисами

### 2. Kubernetes (Production)

Для продакшн развертывания в Kubernetes кластере.

#### Предварительные требования:
- Kubernetes кластер (minikube, kind, или облачный)
- kubectl настроен
- Docker образы собраны и доступны в registry

#### Шаги развертывания:

1. **Сборка образов:**
```bash
./build-images.sh
```

2. **Загрузка в registry (если используется удаленный кластер):**
```bash
docker tag learning-platform/auth-service:latest <registry>/auth-service:latest
docker push <registry>/auth-service:latest
# Повторить для всех сервисов
```

3. **Развертывание:**
```bash
cd k8s
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

4. **Проверка:**
```bash
kubectl get pods -n learning-platform
kubectl get services -n learning-platform
```

5. **Доступ к приложению:**
```bash
# Port forwarding
kubectl port-forward -n learning-platform service/frontend-service 8080:80

# Или через LoadBalancer (если поддерживается)
kubectl get service frontend-service -n learning-platform
```

## Базы данных SQLite

Все сервисы используют SQLite базы данных:

- **Auth Service:** `/app/data/auth.db`
- **Course Service:** `/app/data/courses.db`
- **Learning Service:** `/app/data/learning.db`

### Docker Compose
Базы данных хранятся в именованных volumes:
- `auth_db`
- `course_db`
- `learning_db`

### Kubernetes
Базы данных хранятся в PersistentVolumes:
- `auth-pvc` → `auth-pv`
- `course-pvc` → `course-pv`
- `learning-pvc` → `learning-pv`

**Важно:** Для hostPath volumes убедитесь, что директории созданы на узлах:
```bash
sudo mkdir -p /data/learning-platform/{auth,course,learning}
sudo chmod 777 /data/learning-platform/{auth,course,learning}
```

## Масштабирование

### Docker Compose
Измените количество реплик в `docker-compose.yml`:
```yaml
deploy:
  replicas: 3
```

### Kubernetes
```bash
kubectl scale deployment auth-service --replicas=3 -n learning-platform
kubectl scale deployment course-service --replicas=3 -n learning-platform
kubectl scale deployment learning-service --replicas=3 -n learning-platform
kubectl scale deployment api-gateway --replicas=3 -n learning-platform
kubectl scale deployment frontend-service --replicas=3 -n learning-platform
```

## Мониторинг

### Health Checks

Все сервисы имеют health check endpoints:
- `GET /health` - проверка состояния сервиса

### Просмотр логов

**Docker Compose:**
```bash
docker-compose logs -f auth-service
docker-compose logs -f course-service
docker-compose logs -f learning-service
docker-compose logs -f api-gateway
docker-compose logs -f frontend-service
```

**Kubernetes:**
```bash
kubectl logs -f deployment/auth-service -n learning-platform
kubectl logs -f deployment/course-service -n learning-platform
kubectl logs -f deployment/learning-service -n learning-platform
kubectl logs -f deployment/api-gateway -n learning-platform
kubectl logs -f deployment/frontend-service -n learning-platform
```

## Обновление приложения

### Docker Compose
```bash
docker-compose pull
docker-compose up -d --force-recreate
```

### Kubernetes
```bash
# После обновления образов
kubectl rollout restart deployment/auth-service -n learning-platform
kubectl rollout restart deployment/course-service -n learning-platform
kubectl rollout restart deployment/learning-service -n learning-platform
kubectl rollout restart deployment/api-gateway -n learning-platform
kubectl rollout restart deployment/frontend-service -n learning-platform
```

## Удаление

### Docker Compose
```bash
docker-compose down -v  # -v удаляет volumes
```

### Kubernetes
```bash
kubectl delete namespace learning-platform
```

## Переменные окружения

### Auth Service
- `DATABASE_URL` - URL базы данных (по умолчанию: `sqlite:///data/auth.db`)
- `JWT_SECRET` - Секретный ключ для JWT (обязательно изменить в продакшене!)
- `PORT` - Порт сервиса (по умолчанию: 5001)

### Course Service
- `DATABASE_URL` - URL базы данных (по умолчанию: `sqlite:///data/courses.db`)
- `AUTH_SERVICE_URL` - URL Auth Service
- `PORT` - Порт сервиса (по умолчанию: 5002)

### Learning Service
- `DATABASE_URL` - URL базы данных (по умолчанию: `sqlite:///data/learning.db`)
- `AUTH_SERVICE_URL` - URL Auth Service
- `COURSE_SERVICE_URL` - URL Course Service
- `PORT` - Порт сервиса (по умолчанию: 5003)

### API Gateway
- `AUTH_SERVICE_URL` - URL Auth Service
- `COURSE_SERVICE_URL` - URL Course Service
- `LEARNING_SERVICE_URL` - URL Learning Service
- `PORT` - Порт сервиса (по умолчанию: 5000)

### Frontend Service
- `API_GATEWAY_URL` - URL API Gateway
- `PORT` - Порт сервиса (по умолчанию: 8080)

## Troubleshooting

### Проблема: Сервисы не могут связаться друг с другом

**Docker Compose:**
- Убедитесь, что все сервисы в одной сети
- Проверьте имена сервисов в переменных окружения

**Kubernetes:**
- Убедитесь, что все сервисы в одном namespace
- Проверьте DNS имена сервисов: `<service-name>.<namespace>.svc.cluster.local`

### Проблема: База данных не сохраняется

**Docker Compose:**
- Проверьте, что volumes созданы: `docker volume ls`
- Убедитесь, что путь к БД правильный: `/app/data/`

**Kubernetes:**
- Проверьте статус PVC: `kubectl get pvc -n learning-platform`
- Убедитесь, что PersistentVolume создан и доступен

### Проблема: Health checks не проходят

- Проверьте, что curl установлен в контейнере
- Убедитесь, что сервис отвечает на `/health` endpoint
- Проверьте логи контейнера

