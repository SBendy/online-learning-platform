# Решение проблем с Docker Swarm

## Проблема: "Failed to resolve 'auth-service'"

Эта ошибка возникает, когда API Gateway не может разрешить имена сервисов в Docker Swarm.

### Решение 1: Проверка статуса сервисов

```bash
# Проверить, что все сервисы запущены
docker service ls

# Проверить конкретный сервис
docker service ps learning-platform_auth-service

# Проверить логи
docker service logs learning-platform_api-gateway
```

### Решение 2: Использование полных имен сервисов

В Docker Swarm имена сервисов могут быть в формате `<stack-name>_<service-name>`.

Если короткие имена не работают, обновите переменные окружения в `docker-compose.swarm.yml`:

```yaml
environment:
  - AUTH_SERVICE_URL=http://learning-platform_auth-service:5001
  - COURSE_SERVICE_URL=http://learning-platform_course-service:5002
  - LEARNING_SERVICE_URL=http://learning-platform_learning-service:5003
```

### Решение 3: Проверка сети

```bash
# Проверить сеть
docker network ls
docker network inspect learning-platform_learning-platform-network

# Убедиться, что все сервисы в сети
docker service inspect learning-platform_auth-service | grep -A 10 Networks
docker service inspect learning-platform_api-gateway | grep -A 10 Networks
```

### Решение 4: Пересоздание stack

```bash
# Удалить stack
docker stack rm learning-platform

# Подождать несколько секунд
sleep 10

# Пересоздать
docker stack deploy -c docker-compose.swarm.yml learning-platform
```

### Решение 5: Проверка DNS внутри контейнера

```bash
# Зайти в контейнер API Gateway
docker ps | grep api-gateway
docker exec -it <container-id> /bin/bash

# Внутри контейнера проверить DNS
nslookup auth-service
ping auth-service

# Проверить переменные окружения
env | grep SERVICE
```

### Решение 6: Использование IP адресов (временное решение)

Если DNS не работает, можно использовать IP адреса:

```bash
# Получить IP адреса сервисов
docker service inspect learning-platform_auth-service | grep -A 5 VirtualIPs

# Обновить docker-compose.swarm.yml с IP адресами
# (не рекомендуется для продакшена)
```

### Решение 7: Проверка порядка запуска

API Gateway может пытаться подключиться к сервисам до того, как они полностью запустились.

Добавьте задержку в deploy конфигурацию:

```yaml
deploy:
  restart_policy:
    condition: on-failure
    delay: 10s  # Увеличить задержку
    max_attempts: 5
```

### Решение 8: Использование Docker Compose вместо Swarm

Если проблемы продолжаются, используйте обычный Docker Compose для разработки:

```bash
docker-compose up --build
```

## Типичные проблемы

### Проблема: Сервисы не могут связаться друг с другом

**Причина:** Сервисы не в одной сети или сеть не overlay

**Решение:** Убедитесь, что в `docker-compose.swarm.yml`:
- Все сервисы используют `learning-platform-network`
- Сеть настроена как `driver: overlay`

### Проблема: DNS не разрешает имена

**Причина:** DNS в Swarm еще не настроен или сервисы не запущены

**Решение:**
1. Проверить, что все сервисы запущены: `docker service ls`
2. Подождать несколько секунд после развертывания
3. Использовать полные имена сервисов

### Проблема: Порты не доступны

**Причина:** Порты не проброшены или заняты

**Решение:**
```bash
# Проверить занятые порты
netstat -an | grep 5000
netstat -an | grep 5001

# Изменить порты в docker-compose.swarm.yml если нужно
```

## Отладка

### Включить детальное логирование

В `services/api_gateway/app.py` уже добавлено логирование. Проверьте логи:

```bash
docker service logs -f learning-platform_api-gateway
```

### Проверить конфигурацию

```bash
# Проверить переменные окружения сервиса
docker service inspect learning-platform_api-gateway | grep -A 20 Env
```

### Тестирование подключения

```bash
# Из контейнера API Gateway
docker exec -it <api-gateway-container> python -c "
import requests
import os
url = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
print(f'Testing {url}')
try:
    r = requests.get(f'{url}/health', timeout=5)
    print(f'Success: {r.status_code}')
except Exception as e:
    print(f'Error: {e}')
"
```

