# GitHub Actions Workflows

## CI Pipeline (ci.yml)

Автоматически запускается при:
- Push в ветки `main`, `master`, `develop`
- Pull Request в эти ветки

**Этапы:**
1. Сборка всех Docker образов
2. Тестирование через docker-compose
3. Линтинг Python кода
4. Сканирование безопасности

## Deploy Pipeline (deploy.yml)

Автоматически запускается при:
- Push в `main` или `master`
- Создание тега `v*` (например, `v1.0.0`)

**Этапы:**
1. Сборка и публикация образов в Docker Hub
2. Версионирование образов
3. Создание GitHub Release (при теге)

## Настройка

1. Добавьте секреты в GitHub:
   - `DOCKER_USERNAME` - Docker Hub username
   - `DOCKER_PASSWORD` - Docker Hub password/token

2. Пайплайны запустятся автоматически при следующем push

