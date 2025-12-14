@echo off
REM Скрипт для сборки Docker образов всех микросервисов (Windows)

echo Сборка Docker образов для микросервисной платформы...

REM Auth Service
echo Сборка образа auth-service...
docker build -t learning-platform/auth-service:latest ./services/auth_service

REM Course Service
echo Сборка образа course-service...
docker build -t learning-platform/course-service:latest ./services/course_service

REM Learning Service
echo Сборка образа learning-service...
docker build -t learning-platform/learning-service:latest ./services/learning_service

REM API Gateway
echo Сборка образа api-gateway...
docker build -t learning-platform/api-gateway:latest ./services/api_gateway

REM Frontend Service
echo Сборка образа frontend-service...
docker build -t learning-platform/frontend-service:latest ./services/frontend_service

echo.
echo Все образы успешно собраны!
echo.
echo Для загрузки в registry используйте:
echo docker tag learning-platform/auth-service:latest ^<registry^>/auth-service:latest
echo docker push ^<registry^>/auth-service:latest
echo (и так для всех сервисов)
pause

