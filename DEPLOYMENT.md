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

### 2. Docker Swarm (Production)

Для продакшн развертывания в Docker Swarm кластере.

#### Предварительные требования:
- Docker Swarm инициализирован
- Docker образы собраны

#### Шаги развертывания:

1. **Инициализация Swarm (если еще не инициализирован):**
```bash
docker swarm init
```

2. **Создание JWT секрета:**
```bash
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
```

3. **Сборка образов:**
```bash
./build-images.sh  # Linux/Mac
# или
build-images.bat   # Windows
```

4. **Развертывание:**
```bash
docker stack deploy -c docker-compose.swarm.yml learning-platform
```

5. **Проверка:**
```bash
docker stack services learning-platform
docker service ls
```

6. **Доступ к приложению:**
Приложение будет доступно на http://localhost:8080

Подробнее см. [SWARM_DEPLOYMENT.md](SWARM_DEPLOYMENT.md)

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

### Docker Swarm
Базы данных хранятся в памяти (in-memory SQLite) или в Docker volumes при необходимости.

## Масштабирование

### Docker Compose
Измените количество реплик в `docker-compose.yml`:
```yaml
deploy:
  replicas: 3
```

### Docker Swarm
```bash
docker service scale learning-platform_auth-service=3
docker service scale learning-platform_course-service=3
docker service scale learning-platform_learning-service=3
docker service scale learning-platform_api-gateway=3
docker service scale learning-platform_frontend-service=3
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

**Docker Swarm:**
```bash
docker service logs -f learning-platform_auth-service
docker service logs -f learning-platform_course-service
docker service logs -f learning-platform_learning-service
docker service logs -f learning-platform_api-gateway
docker service logs -f learning-platform_frontend-service
```

## Обновление приложения

### Docker Compose
```bash
docker-compose pull
docker-compose up -d --force-recreate
```

### Docker Swarm
```bash
# После обновления образов
docker service update --force --image learning-platform/auth-service:latest learning-platform_auth-service
docker service update --force --image learning-platform/course-service:latest learning-platform_course-service
docker service update --force --image learning-platform/learning-service:latest learning-platform_learning-service
docker service update --force --image learning-platform/api-gateway:latest learning-platform_api-gateway
docker service update --force --image learning-platform/frontend-service:latest learning-platform_frontend-service
```

## Удаление

### Docker Compose
```bash
docker-compose down -v  # -v удаляет volumes
```

### Docker Swarm
```bash
docker stack rm learning-platform
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

**Docker Swarm:**
- Убедитесь, что все сервисы в одном stack
- Проверьте имена сервисов: `learning-platform_<service-name>`

### Проблема: База данных не сохраняется

**Docker Compose:**
- Проверьте, что volumes созданы: `docker volume ls`
- Убедитесь, что путь к БД правильный: `/app/data/`

**Docker Swarm:**
- Проверьте статус сервисов: `docker service ls`
- Убедитесь, что все реплики запущены: `docker service ps <service-name>`

### Проблема: Health checks не проходят

- Проверьте, что curl установлен в контейнере
- Убедитесь, что сервис отвечает на `/health` endpoint
- Проверьте логи контейнера

