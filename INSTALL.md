# Инструкция по установке и запуску

## 🎯 Быстрая установка (Windows)

Откройте PowerShell в папке проекта и выполните:

```powershell
# 1. Инициализация Swarm
docker swarm init

# 2. Создание секрета
echo jwt-secret-key-change-in-production | docker secret create jwt_secret -

# 3. Сборка и развертывание
.\build-images.bat
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 4. Ожидание запуска
Start-Sleep -Seconds 20

# 5. Инициализация данных
.\init-test-data.ps1

# 6. Проверка
.\check-app.ps1

# 7. Открыть в браузере
Start-Process "http://localhost:8080"
```

## 🎯 Быстрая установка (Linux/Mac)

Откройте терминал в папке проекта и выполните:

```bash
# 1. Инициализация Swarm
docker swarm init

# 2. Создание секрета
echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -

# 3. Сборка и развертывание
chmod +x build-images.sh deploy-swarm.sh
./build-images.sh
docker stack deploy -c docker-compose.swarm.yml learning-platform

# 4. Ожидание запуска
sleep 20

# 5. Проверка
curl http://localhost:5000/health
curl http://localhost:5000/api/courses

# 6. Открыть в браузере
# Linux:
xdg-open http://localhost:8080
# Mac:
open http://localhost:8080
```

## 📋 Пошаговая инструкция

### Шаг 1: Установка Docker

**Windows/Mac:**
1. Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop
2. Установите и запустите Docker Desktop
3. Дождитесь полной загрузки (иконка Docker в трее должна быть зеленая)

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Выйдите и войдите снова для применения изменений
```

### Шаг 2: Копирование проекта

Скопируйте всю папку `online-learning-platform` на новый компьютер.

### Шаг 3: Открытие терминала

**Windows:**
- Откройте PowerShell в папке проекта (Shift + ПКМ → "Открыть PowerShell здесь")

**Linux/Mac:**
- Откройте терминал и перейдите в папку проекта:
```bash
cd /path/to/online-learning-platform
```

### Шаг 4: Выполнение команд установки

Следуйте инструкциям из раздела "Быстрая установка" выше.

## ✅ Проверка успешной установки

После выполнения всех команд проверьте:

1. **Статус сервисов:**
   ```powershell
   docker service ls
   ```
   Все сервисы должны быть `2/2` (2 реплики запущены)

2. **Health checks:**
   ```powershell
   Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing
   ```
   Должен вернуть: `{"status": "healthy", "service": "api-gateway"}`

3. **Веб-интерфейс:**
   Откройте http://localhost:8080 в браузере

## 🔑 Учетные данные

- **Преподаватель:** `teacher` / `teacher123`
- **Администратор:** `admin` / `admin123`

## 🆘 Проблемы?

См. раздел "Устранение проблем" в файле `DEPLOYMENT_GUIDE.md`

