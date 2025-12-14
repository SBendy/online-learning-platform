# Скрипт для полной очистки (данные + stack)

Write-Host "=== Full Cleanup (Data + Stack) ===" -ForegroundColor Yellow
Write-Host ""

# Подтверждение
$confirmation = Read-Host "This will delete ALL data AND remove the entire stack. Continue? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Operation cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "1. Removing stack..." -ForegroundColor Cyan
docker stack rm learning-platform

Write-Host ""
Write-Host "2. Waiting for stack removal (15 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

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
            Write-Host "   ⚠ Volume not found: $volume" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠ Could not remove: $volume" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "4. Cleaning up unused volumes..." -ForegroundColor Cyan
docker volume prune -f | Out-Null

Write-Host ""
Write-Host "5. Removing unused networks..." -ForegroundColor Cyan
docker network prune -f | Out-Null

Write-Host ""
Write-Host "=== Full Cleanup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "To redeploy:" -ForegroundColor Yellow
Write-Host "  1. docker stack deploy -c docker-compose.swarm.yml learning-platform" -ForegroundColor Cyan
Write-Host "  2. .\init-test-data.ps1" -ForegroundColor Cyan
Write-Host ""

