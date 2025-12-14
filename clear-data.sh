#!/bin/bash
# Скрипт для очистки всех данных (логины, курсы, уроки)

echo "=== Clearing All Data ==="
echo ""

# Подтверждение
read -p "This will delete ALL data (users, courses, lessons). Continue? (yes/no): " confirmation
if [ "$confirmation" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "1. Stopping services..."
docker stack rm learning-platform

echo ""
echo "2. Waiting for services to stop (10 seconds)..."
sleep 10

echo ""
echo "3. Removing volumes..."

# Удаление volumes
volumes=(
    "learning-platform_auth_db"
    "learning-platform_course_db"
    "learning-platform_learning_db"
)

for volume in "${volumes[@]}"; do
    if docker volume rm "$volume" 2>/dev/null; then
        echo "   ✓ Removed: $volume"
    else
        echo "   ⚠ Volume not found or in use: $volume"
    fi
done

echo ""
echo "4. Cleaning up unused volumes..."
docker volume prune -f > /dev/null

echo ""
echo "=== Data Cleared Successfully! ==="
echo ""
echo "To redeploy with clean databases:"
echo "  1. docker stack deploy -c docker-compose.swarm.yml learning-platform"
echo "  2. ./init-test-data.ps1 (or create test data manually)"
echo ""

