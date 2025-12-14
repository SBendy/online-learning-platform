# Быстрый старт - Как запустить и проверить приложение

## 🚀 Запуск приложения

### Шаг 1: Развертывание в Docker Swarm

```powershell
# Запустить скрипт развертывания
.\deploy-swarm.bat
```

Или вручную:

```powershell
# 1. Проверить/инициализировать Swarm
docker swarm init

# 2. Создать JWT секрет (если еще не создан)
echo jwt-secret-key-change-in-production | docker secret create jwt_secret -

# 3. Собрать образы
.\build-images.bat

# 4. Развернуть стек
docker stack deploy -c docker-compose.swarm.yml learning-platform
```

### Шаг 2: Проверка статуса сервисов

```powershell
# Проверить статус всех сервисов
docker service ls

# Должно быть 5 сервисов, все с 2/2 репликами:
# - learning-platform_auth-service
# - learning-platform_course-service
# - learning-platform_learning-service
# - learning-platform_api-gateway
# - learning-platform_frontend-service
```

### Шаг 3: Инициализация тестовых данных

```powershell
# Создать преподавателя и тестовый курс
.\init-test-data.ps1
```

## ✅ Проверка работы приложения

### 1. Проверка здоровья сервисов

```powershell
# Auth Service
Invoke-WebRequest -Uri http://localhost:5001/health -UseBasicParsing

# Course Service
Invoke-WebRequest -Uri http://localhost:5002/health -UseBasicParsing

# Learning Service
Invoke-WebRequest -Uri http://localhost:5003/health -UseBasicParsing

# API Gateway
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing
```

Все должны вернуть: `{"status": "healthy", "service": "..."}`

### 2. Проверка регистрации и входа

```powershell
# Регистрация нового пользователя
$body = @{
    username='testuser'
    password='testpass123'
    email='test@example.com'
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/auth/register `
    -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing

# Вход
$body = @{
    username='testuser'
    password='testpass123'
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/login `
    -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing

$token = ($response.Content | ConvertFrom-Json).token
Write-Host "Token: $token"
```

### 3. Проверка создания курса (как преподаватель)

```powershell
# Войти как преподаватель
$body = @{username='teacher'; password='teacher123'} | ConvertTo-Json
$response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/login `
    -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
$token = ($response.Content | ConvertFrom-Json).token

# Создать курс
$headers = @{Authorization="Bearer $token"}
$courseBody = @{
    title='Test Course'
    description='Test course description'
    is_published=$true
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/courses `
    -Method POST -Body $courseBody -ContentType 'application/json' `
    -Headers $headers -UseBasicParsing
```

### 4. Проверка просмотра курсов (как студент)

```powershell
# Получить список всех опубликованных курсов
$response = Invoke-WebRequest -Uri http://localhost:5000/api/courses -UseBasicParsing
$courses = $response.Content | ConvertFrom-Json

Write-Host "Available courses:"
foreach ($course in $courses) {
    Write-Host "  - $($course.title) by $($course.creator)"
}
```

### 5. Проверка веб-интерфейса

Откройте в браузере: **http://localhost:8080**

## 📋 Учетные данные для тестирования

### Преподаватель
- **Логин:** `teacher`
- **Пароль:** `teacher123`
- **Возможности:** Создание и управление курсами

### Студент (создать нового)
- Зарегистрируйтесь через веб-интерфейс или API
- Или используйте: `newuser` / `newpass123` (если уже создан)

### Администратор
- **Логин:** `admin`
- **Пароль:** `admin123`
- **Возможности:** Полный доступ

## 🔍 Просмотр логов

```powershell
# Логи Auth Service
docker service logs -f learning-platform_auth-service

# Логи Course Service
docker service logs -f learning-platform_course-service

# Логи API Gateway
docker service logs -f learning-platform_api-gateway

# Логи всех сервисов
docker service logs -f learning-platform_auth-service
docker service logs -f learning-platform_course-service
docker service logs -f learning-platform_learning-service
docker service logs -f learning-platform_api-gateway
```

## 🛑 Остановка приложения

```powershell
# Удалить стек
docker stack rm learning-platform

# Или использовать скрипт
.\remove-swarm.bat
```

## 🔧 Устранение проблем

### Сервисы не запускаются

```powershell
# Проверить статус
docker service ls

# Проверить логи
docker service logs learning-platform_auth-service

# Пересобрать и обновить
.\build-images.bat
docker service update --force --image learning-platform/auth-service:latest learning-platform_auth-service
```

### База данных не работает

Приложение использует базы данных в памяти (in-memory SQLite), поэтому:
- Данные теряются при перезапуске контейнеров
- Для восстановления данных запустите `.\init-test-data.ps1`

### Порт занят

```powershell
# Проверить, что использует порт
netstat -ano | findstr :8080
netstat -ano | findstr :5000

# Остановить другие приложения или изменить порты в docker-compose.swarm.yml
```

## 📝 Полезные команды

```powershell
# Проверить статус всех сервисов
docker service ls

# Проверить детали сервиса
docker service ps learning-platform_auth-service

# Масштабировать сервис
docker service scale learning-platform_auth-service=3

# Обновить сервис
docker service update --force --image learning-platform/auth-service:latest learning-platform_auth-service

# Удалить сервис
docker service rm learning-platform_auth-service
```

## 🌐 Доступные эндпоинты

- **Frontend:** http://localhost:8080
- **API Gateway:** http://localhost:5000
- **Auth Service:** http://localhost:5001
- **Course Service:** http://localhost:5002
- **Learning Service:** http://localhost:5003

### API Endpoints

- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/courses` - Список курсов (публичные)
- `POST /api/courses` - Создать курс (требуется роль teacher)
- `GET /api/courses/{id}` - Информация о курсе
- `GET /health` - Проверка здоровья сервиса
