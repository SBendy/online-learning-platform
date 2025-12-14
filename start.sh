#!/bin/bash

# Скрипт для запуска всех микросервисов локально

echo "Запуск микросервисной платформы онлайн-обучения..."

# Запуск Auth Service
echo "Запуск Auth Service на порту 5001..."
cd services/auth_service
python app.py &
AUTH_PID=$!
cd ../..

# Ожидание запуска Auth Service
sleep 2

# Запуск Course Service
echo "Запуск Course Service на порту 5002..."
cd services/course_service
python app.py &
COURSE_PID=$!
cd ../..

# Ожидание запуска Course Service
sleep 2

# Запуск Learning Service
echo "Запуск Learning Service на порту 5003..."
cd services/learning_service
python app.py &
LEARNING_PID=$!
cd ../..

# Ожидание запуска Learning Service
sleep 2

# Запуск API Gateway
echo "Запуск API Gateway на порту 5000..."
cd services/api_gateway
python app.py &
GATEWAY_PID=$!
cd ../..

# Ожидание запуска API Gateway
sleep 2

# Запуск Frontend Service
echo "Запуск Frontend Service на порту 8080..."
cd services/frontend_service
python app.py &
FRONTEND_PID=$!
cd ../..

echo ""
echo "Все сервисы запущены!"
echo "Frontend доступен по адресу: http://localhost:8080"
echo "API Gateway доступен по адресу: http://localhost:5000"
echo ""
echo "Для остановки всех сервисов нажмите Ctrl+C"

# Ожидание сигнала завершения
trap "kill $AUTH_PID $COURSE_PID $LEARNING_PID $GATEWAY_PID $FRONTEND_PID; exit" INT TERM
wait

