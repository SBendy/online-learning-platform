@echo off
REM Скрипт для обновления API Gateway после изменений

set STACK_NAME=learning-platform

echo Обновление API Gateway...

REM Пересборка образа
echo 1. Пересборка образа API Gateway...
docker build -t learning-platform/api-gateway:latest ./services/api_gateway

echo.
echo 2. Обновление сервиса API Gateway...
docker service update --image learning-platform/api-gateway:latest %STACK_NAME%_api-gateway

echo.
echo 3. Ожидание обновления...
timeout /t 5 /nobreak >nul

echo.
echo 4. Проверка статуса...
docker service ps %STACK_NAME%_api-gateway

echo.
echo 5. Просмотр логов (последние 20 строк)...
docker service logs --tail 20 %STACK_NAME%_api-gateway

echo.
echo Обновление завершено!
echo.
echo Для просмотра логов в реальном времени:
echo docker service logs -f %STACK_NAME%_api-gateway
pause

