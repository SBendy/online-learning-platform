@echo off
REM Скрипт для развертывания приложения в Docker Swarm

set STACK_NAME=learning-platform

echo Проверка Docker Swarm...
docker info | findstr /C:"Swarm: active" >nul
if errorlevel 1 (
    echo Docker Swarm не активен
    echo.
    echo Инициализация Docker Swarm...
    docker swarm init
    echo.
)

echo Docker Swarm активен
echo.

REM Проверка секрета JWT
echo Проверка секрета JWT...
docker secret ls | findstr /C:"jwt_secret" >nul
if errorlevel 1 (
    echo Создание секрета JWT...
    echo jwt-secret-key-change-in-production | docker secret create jwt_secret -
    echo Секрет создан
) else (
    echo Секрет уже существует
)
echo.

REM Сборка образов
echo Сборка Docker образов...
call build-images.bat
echo.

REM Развертывание stack
echo Развертывание stack '%STACK_NAME%'...
docker stack deploy -c docker-compose.swarm.yml %STACK_NAME%

echo.
echo Развертывание завершено!
echo.
echo Проверка статуса:
docker stack services %STACK_NAME%
echo.
echo Проверка сервисов:
docker service ls
echo.
echo Для просмотра логов используйте:
echo docker service logs -f %STACK_NAME%_auth-service
echo.
echo Приложение будет доступно на http://localhost:8080
pause

