@echo off
REM Скрипт для запуска всех микросервисов локально (Windows)

echo Запуск микросервисной платформы онлайн-обучения...

REM Запуск Auth Service
echo Запуск Auth Service на порту 5001...
start "Auth Service" cmd /k "cd services\auth_service && python app.py"

timeout /t 3 /nobreak >nul

REM Запуск Course Service
echo Запуск Course Service на порту 5002...
start "Course Service" cmd /k "cd services\course_service && python app.py"

timeout /t 3 /nobreak >nul

REM Запуск Learning Service
echo Запуск Learning Service на порту 5003...
start "Learning Service" cmd /k "cd services\learning_service && python app.py"

timeout /t 3 /nobreak >nul

REM Запуск API Gateway
echo Запуск API Gateway на порту 5000...
start "API Gateway" cmd /k "cd services\api_gateway && python app.py"

timeout /t 3 /nobreak >nul

REM Запуск Frontend Service
echo Запуск Frontend Service на порту 8080...
start "Frontend Service" cmd /k "cd services\frontend_service && python app.py"

echo.
echo Все сервисы запущены!
echo Frontend доступен по адресу: http://localhost:8080
echo API Gateway доступен по адресу: http://localhost:5000
echo.
echo Для остановки закройте все окна командной строки
pause

