# Руководство по развертыванию на другом компьютере

## 📋 Требования

- Windows 10/11 или Linux/Mac
- Docker Desktop установлен и запущен
- Git (опционально, для клонирования репозитория)

## 🚀 Шаг 1: Подготовка проекта

### Вариант A: Клонирование из Git (если проект в репозитории)

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd online-learning-platform
```

### Вариант B: Копирование проекта

1. Скопируйте всю папку `online-learning-platform` на новый компьютер
2. Откройте терминал в этой папке

## 🐳 Шаг 2: Проверка Docker

### Windows (PowerShell)

```powershell
# Проверить версию Docker
docker --version

# Проверить, что Docker запущен
docker info
```

### Linux/Mac

```bash
# Проверить версию Docker
docker --version

# Проверить, что Docker запущен
docker info
```

Если Docker не установлен:
- **Windows/Mac**: Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop
- **Linux**: 
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

## 🔧 Шаг 3: Инициализация Docker Swarm

### Windows (PowerShell)

```powershell
# Проверить статус Swarm
docker info | Select-String "Swarm:"

# Если Swarm не активен, инициализировать
docker swarm init
```

### Linux/Mac

```bash
# Проверить статус Swarm
docker info | grep "Swarm:"

# Если Swarm не активен, инициализировать
docker swarm init
```

## 🔐 Шаг 4: Создание JWT секрета

### Windows (PowerShell)

```powershell
# Проверить, существует ли секрет
docker secret ls | Select-String "jwt_secret"

# Если не существует, создать
echo jwt-secret-key-change-in-production | docker secret create jwt_secret -
```

### Linux/Mac

```bash
# Проверить, существует ли секрет
docker secret ls | grep jwt_secret

# Если не существует, создать
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
```

## 🏗️ Шаг 5: Сборка Docker образов

### Windows (PowerShell)

```powershell
# Запустить скрипт сборки
.\build-images.bat

# Или вручную:
docker build -t learning-platform/auth-service:latest ./services/auth_service
docker build -t learning-platform/course-service:latest ./services/course_service
docker build -t learning-platform/learning-service:latest ./services/learning_service
docker build -t learning-platform/api-gateway:latest ./services/api_gateway
docker build -t learning-platform/frontend-service:latest ./services/frontend_service
```

### Linux/Mac

```bash
# Запустить скрипт сборки
chmod +x build-images.sh
./build-images.sh

# Или вручную:
docker build -t learning-platform/auth-service:latest ./services/auth_service
docker build -t learning-platform/course-service:latest ./services/course_service
docker build -t learning-platform/learning-service:latest ./services/learning_service
docker build -t learning-platform/api-gateway:latest ./services/api_gateway
docker build -t learning-platform/frontend-service:latest ./services/frontend_service
```

## 📦 Шаг 6: Развертывание приложения

### Windows (PowerShell)

```powershell
# Автоматическое развертывание
.\deploy-swarm.bat

# Или вручную:
docker stack deploy -c docker-compose.swarm.yml learning-platform
```

### Linux/Mac

```bash
# Автоматическое развертывание
chmod +x deploy-swarm.sh
./deploy-swarm.sh

# Или вручную:
docker stack deploy -c docker-compose.swarm.yml learning-platform
```

## ⏳ Шаг 7: Ожидание запуска сервисов

Подождите 15-30 секунд, пока все сервисы запустятся:

```powershell
# Windows
Start-Sleep -Seconds 20

# Linux/Mac
sleep 20
```

## ✅ Шаг 8: Проверка статуса

### Windows (PowerShell)

```powershell
# Проверить статус всех сервисов
docker service ls

# Должно быть 5 сервисов, все с 2/2 репликами
```

### Linux/Mac

```bash
# Проверить статус всех сервисов
docker service ls

# Должно быть 5 сервисов, все с 2/2 репликами
```

## 🧪 Шаг 9: Инициализация тестовых данных

### Windows (PowerShell)

```powershell
# Создать преподавателя и тестовый курс
.\init-test-data.ps1
```

### Linux/Mac

```bash
# Создать преподавателя и тестовый курс
# (Нужно будет создать bash версию скрипта или использовать curl)
```

## 🔍 Шаг 10: Проверка работы

### Windows (PowerShell)

```powershell
# Быстрая проверка
.\check-app.ps1

# Или вручную:
# Проверка здоровья сервисов
Invoke-WebRequest -Uri http://localhost:5001/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5002/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5003/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing

# Проверка курсов
Invoke-WebRequest -Uri http://localhost:5000/api/courses -UseBasicParsing

# Открыть в браузере
Start-Process "http://localhost:8080"
```

### Linux/Mac

```bash
# Проверка здоровья сервисов
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5000/health

# Проверка курсов
curl http://localhost:5000/api/courses

# Открыть в браузере (Linux)
xdg-open http://localhost:8080
# Mac
open http://localhost:8080
```

## 📝 Все команды в одном месте (Windows PowerShell)

```powershell
# 1. Проверка Docker
docker --version
docker info

# 2. Инициализация Swarm
docker swarm init

# 3. Создание JWT секрета
echo jwt-secret-key-change-in-production | docker secret create jwt_secret -

# 4. Сборка образов
.\build-images.bat

# 5. Развертывание
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 6. Ожидание (20 секунд)
Start-Sleep -Seconds 20

# 7. Проверка статуса
docker service ls

# 8. Инициализация данных
.\init-test-data.ps1

# 9. Проверка работы
.\check-app.ps1

# 10. Открыть в браузере
Start-Process "http://localhost:8080"
```

## 📝 Все команды в одном месте (Linux/Mac)

```bash
# 1. Проверка Docker
docker --version
docker info

# 2. Инициализация Swarm
docker swarm init

# 3. Создание JWT секрета
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -

# 4. Сборка образов
chmod +x build-images.sh
./build-images.sh

# 5. Развертывание
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 6. Ожидание (20 секунд)
sleep 20

# 7. Проверка статуса
docker service ls

# 8. Проверка работы
curl http://localhost:5000/health
curl http://localhost:5000/api/courses

# 9. Открыть в браузере
# Linux:
xdg-open http://localhost:8080
# Mac:
open http://localhost:8080
```

## 🛑 Остановка приложения

### Windows (PowerShell)

```powershell
# Удалить стек
docker stack rm learning-platform

# Или использовать скрипт
.\remove-swarm.bat
```

### Linux/Mac

```bash
# Удалить стек
docker stack rm learning-platform

# Или использовать скрипт
chmod +x remove-swarm.sh
./remove-swarm.sh
```

## 🔧 Устранение проблем

### Проблема: Docker Swarm не инициализирован

```powershell
# Windows
docker swarm init

# Linux/Mac
docker swarm init
```

### Проблема: Порт занят

```powershell
# Windows - проверить, что использует порт
netstat -ano | findstr :8080
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :8080
lsof -i :5000
```

### Проблема: Сервисы не запускаются

```powershell
# Проверить логи
docker service logs learning-platform_auth-service

# Пересобрать и обновить
.\build-images.bat
docker service update --force --image learning-platform/auth-service:latest learning-platform_auth-service
```

### Проблема: База данных не работает

Данные хранятся в памяти, поэтому при перезапуске теряются. Для восстановления:

```powershell
# Windows
.\init-test-data.ps1
```

## 📊 Полезные команды

```powershell
# Просмотр логов сервиса
docker service logs -f learning-platform_auth-service

# Масштабирование сервиса
docker service scale learning-platform_auth-service=3

# Обновление сервиса
docker service update --force --image learning-platform/auth-service:latest learning-platform_auth-service

# Детали сервиса
docker service ps learning-platform_auth-service

# Удаление сервиса
docker service rm learning-platform_auth-service
```

## 🌐 Доступ к приложению

После успешного развертывания:

- **Frontend (веб-интерфейс):** http://localhost:8080
- **API Gateway:** http://localhost:5000
- **Auth Service:** http://localhost:5001
- **Course Service:** http://localhost:5002
- **Learning Service:** http://localhost:5003

## 👤 Учетные данные для тестирования

- **Преподаватель:** `teacher` / `teacher123`
- **Администратор:** `admin` / `admin123`
- **Студент:** Зарегистрируйтесь через веб-интерфейс

## 📦 Что нужно скопировать на другой компьютер

Убедитесь, что скопированы все файлы:

```
online-learning-platform/
├── services/
│   ├── auth_service/
│   ├── course_service/
│   ├── learning_service/
│   ├── api_gateway/
│   └── frontend_service/
├── docker-compose.swarm.yml
├── build-images.bat (Windows) или build-images.sh (Linux/Mac)
├── deploy-swarm.bat (Windows) или deploy-swarm.sh (Linux/Mac)
├── init-test-data.ps1 (Windows)
└── check-app.ps1 (Windows)
```

## ⚡ Быстрый старт (одна команда)

### Windows (PowerShell)

```powershell
# Если все скрипты на месте:
.\deploy-swarm.bat; Start-Sleep -Seconds 20; .\init-test-data.ps1; .\check-app.ps1
```

### Linux/Mac

```bash
# Если все скрипты на месте:
chmod +x *.sh && ./deploy-swarm.sh && sleep 20 && curl http://localhost:5000/health
```

