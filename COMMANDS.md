# Все команды для запуска приложения

## 🪟 Windows (PowerShell) - Скопируйте и выполните по порядку

```powershell
# 1. Проверка Docker
docker --version
docker info

# 2. Инициализация Docker Swarm
docker swarm init

# 3. Создание JWT секрета
echo jwt-secret-key-change-in-production | docker secret create jwt_secret -

# 4. Сборка всех Docker образов
.\build-images.bat

# 5. Развертывание приложения
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 6. Ожидание запуска (20 секунд)
Start-Sleep -Seconds 20

# 7. Проверка статуса сервисов
docker service ls

# 8. Инициализация тестовых данных (преподаватель и курс)
.\init-test-data.ps1

# 9. Проверка работы приложения
.\check-app.ps1

# 10. Открыть в браузере
Start-Process "http://localhost:8080"
```

## 🐧 Linux/Mac - Скопируйте и выполните по порядку

```bash
# 1. Проверка Docker
docker --version
docker info

# 2. Инициализация Docker Swarm
docker swarm init

# 3. Создание JWT секрета
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -

# 4. Сборка всех Docker образов
chmod +x build-images.sh
./build-images.sh

# 5. Развертывание приложения
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 6. Ожидание запуска (20 секунд)
sleep 20

# 7. Проверка статуса сервисов
docker service ls

# 8. Проверка работы приложения
curl http://localhost:5000/health
curl http://localhost:5000/api/courses

# 9. Открыть в браузере
# Linux:
xdg-open http://localhost:8080
# Mac:
open http://localhost:8080
```

## ⚡ Автоматическая установка (одна команда)

### Windows (PowerShell)

```powershell
.\install.ps1
```

### Linux/Mac

```bash
chmod +x install.sh
./install.sh
```

## 🔍 Проверка работы

### Windows (PowerShell)

```powershell
# Проверка здоровья всех сервисов
Invoke-WebRequest -Uri http://localhost:5001/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5002/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5003/health -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing

# Проверка курсов
Invoke-WebRequest -Uri http://localhost:5000/api/courses -UseBasicParsing

# Или используйте скрипт
.\check-app.ps1
```

### Linux/Mac

```bash
# Проверка здоровья всех сервисов
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5000/health

# Проверка курсов
curl http://localhost:5000/api/courses
```

## 🛑 Остановка приложения

### Windows (PowerShell)

```powershell
docker stack rm learning-platform
```

### Linux/Mac

```bash
docker stack rm learning-platform
```

## 📝 Создание урока с изображениями

### Windows (PowerShell)

```powershell
# Создать урок с текстом
$body = @{username='teacher'; password='teacher123'} | ConvertTo-Json
$response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/login -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
$token = ($response.Content | ConvertFrom-Json).token

$headers = @{Authorization="Bearer $token"}
$lessonBody = @{
    title='Название урока'
    content='Текст урока с описанием материала...'
    images=@()
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri http://localhost:5000/api/courses/1/lessons -Method POST -Body $lessonBody -ContentType 'application/json' -Headers $headers -UseBasicParsing

# Или используйте скрипт
.\create-lesson-with-images.ps1 -CourseId 1 -Title "Lesson Title" -Content "Lesson content" -ImagePath "path/to/image.png"
```

## 🔑 Учетные данные

- **Преподаватель:** `teacher` / `teacher123`
- **Администратор:** `admin` / `admin123`
- **Студент:** Зарегистрируйтесь через веб-интерфейс

## 🌐 Доступ к приложению

- **Frontend:** http://localhost:8080
- **API Gateway:** http://localhost:5000
- **Auth Service:** http://localhost:5001
- **Course Service:** http://localhost:5002
- **Learning Service:** http://localhost:5003

## 📋 Минимальный набор команд (только самое необходимое)

### Windows

```powershell
docker swarm init
echo jwt-secret-key-change-in-production | docker secret create jwt_secret -
.\build-images.bat
docker stack deploy -c docker-compose.swarm.yml learning-platform
Start-Sleep -Seconds 20
.\init-test-data.ps1
Start-Process "http://localhost:8080"
```

### Linux/Mac

```bash
docker swarm init
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
chmod +x build-images.sh && ./build-images.sh
docker stack deploy -c docker-compose.swarm.yml learning-platform
sleep 20
curl http://localhost:5000/health
```

