#!/bin/bash
# Скрипт для полной очистки (данные + stack)

echo "=== Full Cleanup (Data + Stack) ==="
echo ""

# Подтверждение
read -p "This will delete ALL data AND remove the entire stack. Continue? (yes/no): " confirmation
if [ "$confirmation" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "1. Removing stack..."
docker stack rm learning-platform

echo ""
echo "2. Waiting for stack removal (15 seconds)..."
sleep 15

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
        echo "   ⚠ Volume not found: $volume"
    fi
done

echo ""
echo "4. Cleaning up unused volumes..."
docker volume prune -f > /dev/null

echo ""
echo "5. Removing unused networks..."
docker network prune -f > /dev/null

echo ""
echo "=== Full Cleanup Complete! ==="
echo ""
echo "To redeploy:"
echo "  1. docker stack deploy -c docker-compose.swarm.yml learning-platform"
echo "  2. ./init-test-data.ps1 (or create test data manually)"
echo ""

