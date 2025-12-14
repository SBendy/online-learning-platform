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
- Docker Swarm - оркестрация контейнеров
- SQLite - база данных (хранится в памяти или Docker volumes)

## Быстрый старт

### Вариант 1: Docker Compose (рекомендуется для разработки)

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8080

### Вариант 2: Docker Swarm (для продакшена)

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

### Вариант 3: Локальный запуск (без Docker)

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
- **Docker платформы:**
  - AWS ECS
  - Google Cloud Run
  - Azure Container Instances
  - Heroku (с Docker)

Подробные инструкции см. в [DEPLOYMENT.md](DEPLOYMENT.md) и [SWARM_DEPLOYMENT.md](SWARM_DEPLOYMENT.md)

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

## Очистка данных

Для очистки всех данных (пользователи, курсы, уроки) используйте готовые скрипты:

### Windows (PowerShell)

**Очистка только данных (stack продолжает работать):**
```powershell
.\clear-data.ps1
```

**Полная очистка (данные + stack):**
```powershell
.\clear-all.ps1
```

### Linux/Mac

**Очистка только данных:**
```bash
chmod +x clear-data.sh
./clear-data.sh
```

**Полная очистка:**
```bash
chmod +x clear-all.sh
./clear-all.sh
```

### Ручная очистка

Если нужно очистить данные вручную:

```bash
# 1. Остановить stack
docker stack rm learning-platform

# 2. Подождать завершения (10-15 секунд)
sleep 10

# 3. Удалить volumes с базами данных
docker volume rm learning-platform_auth_db
docker volume rm learning-platform_course_db
docker volume rm learning-platform_learning_db

# 4. Очистить неиспользуемые volumes
docker volume prune -f

# 5. Развернуть заново
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 6. Инициализировать тестовые данные (опционально)
.\init-test-data.ps1  # Windows
# или
./init-test-data.ps1  # Linux/Mac (если есть)
```

**⚠️ Внимание:** Очистка данных удалит:
- Всех пользователей и логины
- Все курсы
- Все уроки и записи на курсы
- Весь прогресс обучения

После очистки базы данных будут пустыми, и потребуется повторная инициализация тестовых данных.

