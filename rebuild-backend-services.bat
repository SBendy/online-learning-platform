@echo off
REM Скрипт для пересборки и обновления backend сервисов

set STACK_NAME=learning-platform

echo Пересборка backend сервисов...

REM Пересборка образов
echo 1. Пересборка образов...
docker build -t learning-platform/auth-service:latest ./services/auth_service
docker build -t learning-platform/course-service:latest ./services/course_service
docker build -t learning-platform/learning-service:latest ./services/learning_service

echo.
echo 2. Обновление сервисов...
docker service update --image learning-platform/auth-service:latest %STACK_NAME%_auth-service
docker service update --image learning-platform/course-service:latest %STACK_NAME%_course-service
docker service update --image learning-platform/learning-service:latest %STACK_NAME%_learning-service

echo.
echo 3. Ожидание обновления...
timeout /t 10 /nobreak >nul

echo.
echo 4. Проверка статуса...
docker service ls | findstr learning-platform

echo.
echo Пересборка завершена!
echo.
echo Для просмотра логов используйте:
echo docker service logs -f %STACK_NAME%_auth-service
pause

