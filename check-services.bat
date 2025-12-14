@echo off
REM Скрипт для проверки доступности сервисов

echo Проверка доступности сервисов...
echo.

REM Проверка Auth Service
echo 1. Проверка Auth Service (http://localhost:5001/health)...
curl -s http://localhost:5001/health >nul 2>&1
if errorlevel 1 (
    echo    ❌ Auth Service недоступен
) else (
    echo    ✅ Auth Service доступен
)

REM Проверка Course Service
echo 2. Проверка Course Service (http://localhost:5002/health)...
curl -s http://localhost:5002/health >nul 2>&1
if errorlevel 1 (
    echo    ❌ Course Service недоступен
) else (
    echo    ✅ Course Service доступен
)

REM Проверка Learning Service
echo 3. Проверка Learning Service (http://localhost:5003/health)...
curl -s http://localhost:5003/health >nul 2>&1
if errorlevel 1 (
    echo    ❌ Learning Service недоступен
) else (
    echo    ✅ Learning Service доступен
)

REM Проверка API Gateway
echo 4. Проверка API Gateway (http://localhost:5000/health)...
curl -s http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo    ❌ API Gateway недоступен
) else (
    echo    ✅ API Gateway доступен
)

REM Проверка Frontend Service
echo 5. Проверка Frontend Service (http://localhost:8080/health)...
curl -s http://localhost:8080/health >nul 2>&1
if errorlevel 1 (
    echo    ❌ Frontend Service недоступен
) else (
    echo    ✅ Frontend Service доступен
)

echo.
echo Проверка завершена!
pause

