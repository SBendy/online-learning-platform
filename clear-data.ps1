# Скрипт для очистки всех данных (логины, курсы, уроки)

Write-Host "=== Clearing All Data ===" -ForegroundColor Yellow
Write-Host ""

# Подтверждение
$confirmation = Read-Host "This will delete ALL data (users, courses, lessons). Continue? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Operation cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "1. Stopping services..." -ForegroundColor Cyan
docker stack rm learning-platform

Write-Host ""
Write-Host "2. Waiting for services to stop (10 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "3. Removing volumes..." -ForegroundColor Cyan

# Удаление volumes
$volumes = @(
    "learning-platform_auth_db",
    "learning-platform_course_db",
    "learning-platform_learning_db"
)

foreach ($volume in $volumes) {
    try {
        docker volume rm $volume 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Removed: $volume" -ForegroundColor Green
        } else {
            Write-Host "   ⚠ Volume not found or in use: $volume" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠ Could not remove: $volume" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "4. Cleaning up unused volumes..." -ForegroundColor Cyan
docker volume prune -f | Out-Null

Write-Host ""
Write-Host "=== Data Cleared Successfully! ===" -ForegroundColor Green
Write-Host ""
Write-Host "To redeploy with clean databases:" -ForegroundColor Yellow
Write-Host "  1. docker stack deploy -c docker-compose.swarm.yml learning-platform" -ForegroundColor Cyan
Write-Host "  2. .\init-test-data.ps1" -ForegroundColor Cyan
Write-Host ""

