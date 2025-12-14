# Развертывание в Docker Swarm

## Предварительные требования

- Docker Engine 20.10+
- Docker Swarm инициализирован
- Доступ к Docker daemon

## Быстрое развертывание

### 1. Инициализация Docker Swarm

```bash
# Если Swarm еще не инициализирован
docker swarm init

# Для multi-host кластера добавьте worker узлы:
# docker swarm join --token <token> <manager-ip>:2377
```

### 2. Создание секрета JWT

```bash
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
```

**Важно:** В продакшене используйте безопасный секретный ключ!

### 3. Сборка образов

```bash
# Linux/Mac
./build-images.sh

# Windows
build-images.bat
```

### 4. Развертывание

```bash
# Linux/Mac
./deploy-swarm.sh

# Windows
deploy-swarm.bat

# Или вручную
docker stack deploy -c docker-compose.swarm.yml learning-platform
```

### 5. Проверка статуса

```bash
# Проверка stack
docker stack services learning-platform

# Проверка сервисов
docker service ls

# Проверка подов (задач)
docker service ps learning-platform_auth-service
```

## Доступ к приложению

Приложение будет доступно на http://localhost:8080

Если используете multi-host кластер, используйте IP адрес manager узла.

## Управление

### Просмотр логов

```bash
# Логи конкретного сервиса
docker service logs -f learning-platform_auth-service

# Логи всех сервисов в stack
docker stack ps learning-platform --no-trunc
```

### Масштабирование

```bash
# Увеличить количество реплик
docker service scale learning-platform_auth-service=3
docker service scale learning-platform_course-service=3
docker service scale learning-platform_learning-service=3
docker service scale learning-platform_api-gateway=3
docker service scale learning-platform_frontend-service=3
```

### Обновление сервиса

```bash
# После сборки нового образа
docker service update --image learning-platform/auth-service:new-tag learning-platform_auth-service

# Или принудительное обновление
docker service update --force learning-platform_auth-service
```

### Откат обновления

```bash
docker service rollback learning-platform_auth-service
```

## Удаление

```bash
# Удаление stack
docker stack rm learning-platform

# Удаление секрета (опционально)
docker secret rm jwt_secret

# Покинуть swarm (если нужно)
docker swarm leave --force
```

## Особенности Docker Swarm

### Volumes

Базы данных SQLite хранятся в именованных volumes:
- `learning-platform_auth_db`
- `learning-platform_course_db`
- `learning-platform_learning_db`

Volumes создаются автоматически при развертывании.

### Secrets

JWT секрет хранится в Docker Swarm secrets и монтируется в контейнеры как файл `/run/secrets/jwt_secret`.

### Networking

Используется overlay network для коммуникации между сервисами в multi-host кластере.

### Health Checks

Все сервисы имеют health checks для автоматического перезапуска нездоровых контейнеров.

## Troubleshooting

### Проблема: Сервисы не запускаются

```bash
# Проверить статус сервисов
docker service ls

# Проверить задачи
docker service ps learning-platform_auth-service --no-trunc

# Проверить логи
docker service logs learning-platform_auth-service
```

### Проблема: Секрет не найден

```bash
# Проверить секреты
docker secret ls

# Создать секрет заново
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
```

### Проблема: Сервисы не могут связаться друг с другом

Проверьте, что все сервисы в одной сети:
```bash
docker network ls
docker network inspect learning-platform_learning-platform-network
```

### Проблема: Volumes не монтируются

```bash
# Проверить volumes
docker volume ls

# Проверить использование volumes
docker service inspect learning-platform_auth-service
```

## Масштабирование в продакшене

Для продакшена рекомендуется:

1. **Увеличить реплики:**
```bash
docker service scale learning-platform_auth-service=3
docker service scale learning-platform_course-service=3
docker service scale learning-platform_learning-service=3
docker service scale learning-platform_api-gateway=3
docker service scale learning-platform_frontend-service=3
```

2. **Настроить ресурсы** в `docker-compose.swarm.yml`:
```yaml
resources:
  limits:
    cpus: '1.0'
    memory: 1G
  reservations:
    cpus: '0.5'
    memory: 512M
```

3. **Использовать внешний Load Balancer** для доступа к приложению

4. **Настроить мониторинг** (Prometheus, Grafana)

## Multi-Host кластер

Для развертывания на нескольких хостах:

1. Инициализируйте Swarm на manager узле:
```bash
docker swarm init --advertise-addr <manager-ip>
```

2. Добавьте worker узлы:
```bash
# На worker узле выполните команду, полученную от manager
docker swarm join --token <token> <manager-ip>:2377
```

3. Развертывание выполняется на manager узле, задачи распределяются по всем узлам.

4. Убедитесь, что volumes доступны на всех узлах или используйте shared storage.

## Сравнение с Kubernetes

### Преимущества Docker Swarm:
- Проще в настройке и использовании
- Встроен в Docker Engine
- Меньше ресурсов
- Быстрее развертывание

### Недостатки:
- Меньше функций, чем в Kubernetes
- Меньше инструментов экосистемы
- Ограниченные возможности автоматического масштабирования

## Миграция с Kubernetes

Если вы мигрируете с Kubernetes:

1. Удалите Kubernetes развертывание:
```bash
kubectl delete namespace learning-platform
```

2. Следуйте инструкциям выше для развертывания в Swarm

3. Обратите внимание на различия:
   - В Swarm нет ConfigMap, используйте environment variables
   - Secrets работают по-другому (файлы вместо переменных)
   - Volumes используют другой синтаксис
   - Нет Ingress, используйте LoadBalancer или внешний прокси

