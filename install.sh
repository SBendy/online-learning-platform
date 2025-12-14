#!/bin/bash
# Автоматическая установка и запуск приложения (Linux/Mac)

echo "=== Online Learning Platform - Installation ==="
echo ""

# Проверка Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    echo "   OK: $(docker --version)"
else
    echo "   ERROR: Docker is not installed"
    echo "   Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверка Docker запущен
if docker info &> /dev/null; then
    echo "   OK: Docker is running"
else
    echo "   ERROR: Docker is not running"
    echo "   Please start Docker"
    exit 1
fi

# Инициализация Swarm
echo ""
echo "2. Initializing Docker Swarm..."
if docker info 2>&1 | grep -q "Swarm: active"; then
    echo "   OK: Swarm is already active"
else
    echo "   Initializing Swarm..."
    docker swarm init
    if [ $? -eq 0 ]; then
        echo "   OK: Swarm initialized"
    else
        echo "   WARNING: Swarm may already be initialized"
    fi
fi

# Создание JWT секрета
echo ""
echo "3. Creating JWT secret..."
if docker secret ls 2>&1 | grep -q "jwt_secret"; then
    echo "   OK: JWT secret already exists"
else
    echo "jwt-secret-key-change-in-production" | docker secret create jwt_secret -
    if [ $? -eq 0 ]; then
        echo "   OK: JWT secret created"
    else
        echo "   ERROR: Failed to create secret"
        exit 1
    fi
fi

# Сборка образов
echo ""
echo "4. Building Docker images..."
echo "   This may take several minutes..."
if [ -f "build-images.sh" ]; then
    chmod +x build-images.sh
    ./build-images.sh
    if [ $? -ne 0 ]; then
        echo "   ERROR: Failed to build images"
        exit 1
    fi
else
    echo "   ERROR: build-images.sh not found"
    exit 1
fi

# Развертывание
echo ""
echo "5. Deploying application..."
docker stack deploy -c docker-compose.swarm.yml learning-platform
if [ $? -eq 0 ]; then
    echo "   OK: Stack deployed"
else
    echo "   ERROR: Failed to deploy stack"
    exit 1
fi

# Ожидание запуска
echo ""
echo "6. Waiting for services to start (30 seconds)..."
sleep 30

# Проверка статуса
echo ""
echo "7. Checking service status..."
docker service ls

# Финальная проверка
echo ""
echo "8. Final check..."
echo "   Testing API Gateway..."
curl -s http://localhost:5000/health | head -1
echo ""
echo "   Testing Courses API..."
curl -s http://localhost:5000/api/courses | head -1
echo ""

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Application is available at:"
echo "  Frontend: http://localhost:8080"
echo "  API Gateway: http://localhost:5000"
echo ""
echo "Test credentials:"
echo "  Teacher: teacher / teacher123"
echo "  Admin: admin / admin123"
echo ""
echo "Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8080
elif command -v open &> /dev/null; then
    open http://localhost:8080
fi

