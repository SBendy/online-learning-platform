# Application Status Check Script

Write-Host ""
Write-Host "=== Checking Application Status ===" -ForegroundColor Green

# 1. Docker Services Status
Write-Host ""
Write-Host "1. Docker Services Status:" -ForegroundColor Yellow
docker service ls --format "table {{.Name}}`t{{.Replicas}}`t{{.Image}}"

# 2. Health Checks
Write-Host ""
Write-Host "2. Health Checks:" -ForegroundColor Yellow

$services = @(
    @{Name='Auth Service'; Url='http://localhost:5001/health'},
    @{Name='Course Service'; Url='http://localhost:5002/health'},
    @{Name='Learning Service'; Url='http://localhost:5003/health'},
    @{Name='API Gateway'; Url='http://localhost:5000/health'}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 2
        $status = $response.Content | ConvertFrom-Json
        Write-Host "   OK: $($service.Name) - $($status.status)" -ForegroundColor Green
    } catch {
        Write-Host "   FAILED: $($service.Name)" -ForegroundColor Red
    }
}

# 3. Check Courses
Write-Host ""
Write-Host "3. Available Courses:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:5000/api/courses -UseBasicParsing -TimeoutSec 2
    $courses = $response.Content | ConvertFrom-Json
    if ($courses.Count -eq 0) {
        Write-Host "   No courses available" -ForegroundColor Yellow
        Write-Host "   Run .\init-test-data.ps1 to create test data" -ForegroundColor Cyan
    } else {
        Write-Host "   Found $($courses.Count) course(s):" -ForegroundColor Green
        foreach ($course in $courses) {
            Write-Host "     - $($course.title) (ID: $($course.id)) by $($course.creator)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Test Registration
Write-Host ""
Write-Host "4. Testing Registration:" -ForegroundColor Yellow
try {
    $randomUser = "checkuser_$(Get-Random)"
    $body = @{
        username=$randomUser
        password="checkpass123"
        email="check@example.com"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/register `
        -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing -TimeoutSec 5
    Write-Host "   OK: Registration works" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: Registration - $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8080" -ForegroundColor Cyan
Write-Host "API Gateway: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test credentials:" -ForegroundColor Yellow
Write-Host "  Teacher: teacher / teacher123" -ForegroundColor Cyan
Write-Host "  Admin: admin / admin123" -ForegroundColor Cyan
