# Автоматическая установка и запуск приложения (Windows)

Write-Host "=== Online Learning Platform - Installation ===" -ForegroundColor Green
Write-Host ""

# Проверка Docker
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   OK: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Проверка Docker запущен
try {
    docker info | Out-Null
    Write-Host "   OK: Docker is running" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Docker is not running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Инициализация Swarm
Write-Host ""
Write-Host "2. Initializing Docker Swarm..." -ForegroundColor Yellow
$swarmStatus = docker info 2>&1 | Select-String "Swarm: active"
if (-not $swarmStatus) {
    Write-Host "   Initializing Swarm..." -ForegroundColor Cyan
    docker swarm init 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK: Swarm initialized" -ForegroundColor Green
    } else {
        Write-Host "   WARNING: Swarm may already be initialized" -ForegroundColor Yellow
    }
} else {
    Write-Host "   OK: Swarm is already active" -ForegroundColor Green
}

# Создание JWT секрета
Write-Host ""
Write-Host "3. Creating JWT secret..." -ForegroundColor Yellow
$secretExists = docker secret ls 2>&1 | Select-String "jwt_secret"
if (-not $secretExists) {
    echo jwt-secret-key-change-in-production | docker secret create jwt_secret - 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK: JWT secret created" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: Failed to create secret" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   OK: JWT secret already exists" -ForegroundColor Green
}

# Сборка образов
Write-Host ""
Write-Host "4. Building Docker images..." -ForegroundColor Yellow
Write-Host "   This may take several minutes..." -ForegroundColor Cyan
if (Test-Path "build-images.bat") {
    & .\build-images.bat
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ERROR: Failed to build images" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   ERROR: build-images.bat not found" -ForegroundColor Red
    exit 1
}

# Развертывание
Write-Host ""
Write-Host "5. Deploying application..." -ForegroundColor Yellow
docker stack deploy -c docker-compose.swarm.yml learning-platform
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK: Stack deployed" -ForegroundColor Green
} else {
    Write-Host "   ERROR: Failed to deploy stack" -ForegroundColor Red
    exit 1
}

# Ожидание запуска
Write-Host ""
Write-Host "6. Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Проверка статуса
Write-Host ""
Write-Host "7. Checking service status..." -ForegroundColor Yellow
docker service ls

# Инициализация данных
Write-Host ""
Write-Host "8. Initializing test data..." -ForegroundColor Yellow
if (Test-Path "init-test-data.ps1") {
    & .\init-test-data.ps1
} else {
    Write-Host "   WARNING: init-test-data.ps1 not found, skipping" -ForegroundColor Yellow
}

# Финальная проверка
Write-Host ""
Write-Host "9. Final check..." -ForegroundColor Yellow
if (Test-Path "check-app.ps1") {
    & .\check-app.ps1
}

Write-Host ""
Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Application is available at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:8080" -ForegroundColor Yellow
Write-Host "  API Gateway: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Test credentials:" -ForegroundColor Cyan
Write-Host "  Teacher: teacher / teacher123" -ForegroundColor Yellow
Write-Host "  Admin: admin / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:8080"

