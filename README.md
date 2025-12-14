# Облачная платформа онлайн-обучения (Микросервисная архитектура)

Веб-приложение для системы онлайн-обучения с микросервисной архитектурой.

## Архитектура

Система состоит из 5 микросервисов:

### Backend сервисы (3):
1. **Auth Service** (порт 5001) - Аутентификация и авторизация, управление пользователями, JWT токены
2. **Course Service** (порт 5002) - Управление курсами (создание, редактирование, публикация)
3. **Learning Service** (порт 5003) - Управление уроками, записями на курсы, отслеживание прогресса

### Frontend сервисы (2):
4. **API Gateway** (порт 5000) - Единая точка входа, маршрутизация запросов к backend сервисам
5. **Frontend Service** (порт 8080) - Веб-интерфейс приложения

## Технологии

- Python 3.11
- Flask - веб-фреймворк
- SQLAlchemy - ORM
- JWT - аутентификация
- Docker & Docker Compose - контейнеризация
- Docker Swarm - оркестрация контейнеров (рекомендуется)
- Kubernetes - оркестрация контейнеров (альтернатива)
- SQLite - база данных (хранится в Docker volumes или PersistentVolumes)

## Быстрый старт

### Вариант 1: Docker Compose (рекомендуется для разработки)

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8080

### Вариант 2: Kubernetes (для продакшена)

**⚠️ Важно:** Перед развертыванием убедитесь, что Kubernetes кластер запущен!

```bash
# Проверка подключения к кластеру
cd k8s
./check-cluster.sh  # Linux/Mac
# или
check-cluster.bat   # Windows

# Если кластер не настроен, см. k8s/setup-local-cluster.md

# 1. Сборка образов
./build-images.sh

# 2. Развертывание в Kubernetes
cd k8s
./deploy.sh

# Или вручную:
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f persistent-volumes.yaml
kubectl apply -f auth-service-deployment.yaml
kubectl apply -f course-service-deployment.yaml
kubectl apply -f learning-service-deployment.yaml
kubectl apply -f api-gateway-deployment.yaml
kubectl apply -f frontend-service-deployment.yaml
kubectl apply -f ingress.yaml

# 3. Доступ к приложению
kubectl port-forward -n learning-platform service/frontend-service 8080:80
```

**Если кластер не настроен:** Используйте Docker Compose (Вариант 1) или настройте локальный кластер (см. [k8s/setup-local-cluster.md](k8s/setup-local-cluster.md))

Подробнее см. [DEPLOYMENT.md](DEPLOYMENT.md) и [k8s/README.md](k8s/README.md)

### Вариант 3: Docker Swarm (для продакшена)

**⚠️ Важно:** Перед развертыванием убедитесь, что Docker Swarm инициализирован!

```bash
# Инициализация Swarm (если еще не инициализирован)
docker swarm init

# 1. Сборка образов
./build-images.sh  # Linux/Mac
# или
build-images.bat   # Windows

# 2. Создание секрета JWT
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -

# 3. Развертывание в Docker Swarm
./deploy-swarm.sh  # Linux/Mac
# или
deploy-swarm.bat   # Windows

# 4. Проверка статуса
docker stack services learning-platform
docker service ls

# 5. Доступ к приложению
# Приложение будет доступно на http://localhost:8080
```

**Управление:**

```bash
# Просмотр логов
docker service logs -f learning-platform_auth-service

# Масштабирование сервиса
docker service scale learning-platform_auth-service=3

# Обновление сервиса
docker service update --image learning-platform/auth-service:new-tag learning-platform_auth-service

# Удаление stack
docker stack rm learning-platform
```

Подробнее см. [SWARM_DEPLOYMENT.md](SWARM_DEPLOYMENT.md)

### Вариант 4: Локальный запуск (без Docker)

1. Запустите сервисы в отдельных терминалах:

```bash
# Terminal 1 - Auth Service
cd services/auth_service
pip install -r requirements.txt
python app.py

# Terminal 2 - Course Service
cd services/course_service
pip install -r requirements.txt
python app.py

# Terminal 3 - Learning Service
cd services/learning_service
pip install -r requirements.txt
python app.py

# Terminal 4 - API Gateway
cd services/api_gateway
pip install -r requirements.txt
python app.py

# Terminal 5 - Frontend Service
cd services/frontend_service
pip install -r requirements.txt
python app.py
```

2. Откройте браузер: http://localhost:8080

## Использование

### Администратор по умолчанию
- Имя пользователя: `admin`
- Пароль: `admin123`

### Роли пользователей

- **Студент** - может просматривать курсы, записываться на них и отслеживать прогресс
- **Преподаватель** - может создавать курсы и добавлять уроки
- **Администратор** - полный доступ ко всем функциям

## API Endpoints

Все запросы проходят через API Gateway: `http://localhost:5000/api`

### Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход (возвращает JWT токен)
- `POST /api/auth/validate` - Валидация токена
- `GET /api/auth/user/<id>` - Информация о пользователе

### Курсы
- `GET /api/courses` - Список опубликованных курсов
- `GET /api/courses/my` - Мои курсы (требует авторизации)
- `POST /api/courses` - Создать курс (требует роль teacher/admin)
- `GET /api/courses/<id>` - Информация о курсе
- `PUT /api/courses/<id>` - Обновить курс
- `DELETE /api/courses/<id>` - Удалить курс

### Обучение
- `GET /api/courses/<id>/lessons` - Уроки курса
- `POST /api/courses/<id>/lessons` - Создать урок
- `GET /api/lessons/<id>` - Информация об уроке
- `POST /api/courses/<id>/enroll` - Записаться на курс
- `GET /api/users/<id>/enrollments` - Курсы пользователя
- `POST /api/lessons/<id>/complete` - Отметить урок как пройденный

## Авторизация

Все защищенные endpoints требуют JWT токен в заголовке:
```
Authorization: Bearer <token>
```

Токен получается при входе через `/api/auth/login` и действителен 24 часа.

## Структура проекта

```
.
├── services/
│   ├── auth_service/          # Сервис аутентификации
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── course_service/        # Сервис курсов
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── learning_service/       # Сервис обучения
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── api_gateway/           # API Gateway
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend_service/      # Frontend
│       ├── app.py
│       ├── templates/
│       │   └── index.html
│       ├── requirements.txt
│       └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Облачное развертывание

Система готова к развертыванию на:
- **Docker Swarm:**
  - Локальный Swarm кластер
  - Multi-host Swarm кластер
  - Docker Enterprise
- **Kubernetes кластеры:**
  - AWS EKS
  - Google Cloud GKE
  - Azure AKS
  - Minikube (локально)
  - Kind (локально)
- **Docker платформы:**
  - AWS ECS
  - Google Cloud Run
  - Azure Container Instances
  - Heroku (с Docker)

Подробные инструкции см. в [DEPLOYMENT.md](DEPLOYMENT.md)

### Переменные окружения для продакшена:

- `JWT_SECRET` - секретный ключ для JWT (обязательно изменить!)
- `DATABASE_URL` - URL базы данных (PostgreSQL рекомендуется)
- `AUTH_SERVICE_URL`, `COURSE_SERVICE_URL`, `LEARNING_SERVICE_URL` - URL микросервисов

## Масштабирование

### Docker Compose
Измените количество реплик в `docker-compose.yml` или используйте docker-compose scale.

### Docker Swarm
```bash
docker service scale learning-platform_auth-service=3
docker service scale learning-platform_course-service=3
docker service scale learning-platform_learning-service=3
docker service scale learning-platform_api-gateway=3
docker service scale learning-platform_frontend-service=3
```

### Kubernetes
```bash
kubectl scale deployment auth-service --replicas=3 -n learning-platform
kubectl scale deployment course-service --replicas=3 -n learning-platform
kubectl scale deployment learning-service --replicas=3 -n learning-platform
kubectl scale deployment api-gateway --replicas=3 -n learning-platform
kubectl scale deployment frontend-service --replicas=3 -n learning-platform
```

Каждый микросервис может масштабироваться независимо.

## Мониторинг

Health check endpoints доступны на каждом сервисе:
- `GET /health` - проверка состояния сервиса

### Просмотр логов

**Docker Compose:**
```bash
docker-compose logs -f [service-name]
```

**Docker Swarm:**
```bash
docker service logs -f learning-platform_[service-name]
```

**Kubernetes:**
```bash
kubectl logs -f deployment/[service-name] -n learning-platform
```
