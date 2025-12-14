# Скрипт для инициализации тестовых данных
# Создает преподавателя и тестовый курс

Write-Host "=== Инициализация тестовых данных ===" -ForegroundColor Green

# 1. Создать или войти как преподаватель
Write-Host "`n1. Создание/проверка преподавателя..." -ForegroundColor Yellow
try {
    $body = @{
        username='teacher'
        password='teacher123'
        email='teacher@example.com'
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/register `
        -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
    Write-Host "   Teacher created!" -ForegroundColor Green
} catch {
    Write-Host "   Teacher already exists, logging in..." -ForegroundColor Yellow
}

# 2. Login as teacher
Write-Host "`n2. Logging in as teacher..." -ForegroundColor Yellow
$body = @{
    username='teacher'
    password='teacher123'
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/login `
    -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
$token = ($response.Content | ConvertFrom-Json).token
Write-Host "   Token obtained!" -ForegroundColor Green

# 3. Create test course
Write-Host "`n3. Creating test course..." -ForegroundColor Yellow
$headers = @{
    Authorization="Bearer $token"
}

$courseBody = @{
    title='Introduction to Programming'
    description='Basic programming course for beginners. Learn Python basics, algorithms and data structures.'
    is_published=$true
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri http://localhost:5000/api/courses `
        -Method POST -Body $courseBody -ContentType 'application/json' `
        -Headers $headers -UseBasicParsing
    Write-Host "   Course created successfully!" -ForegroundColor Green
    $course = $response.Content | ConvertFrom-Json
    Write-Host "   ID: $($course.id) | Title: $($course.title)" -ForegroundColor Cyan
} catch {
    Write-Host "   Course already exists or error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. Show all published courses
Write-Host "`n4. List of all published courses:" -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri http://localhost:5000/api/courses -UseBasicParsing
$courses = $response.Content | ConvertFrom-Json

if ($courses.Count -eq 0) {
    Write-Host "   No published courses" -ForegroundColor Red
} else {
    foreach ($course in $courses) {
        Write-Host "   - ID: $($course.id) | $($course.title) | Teacher: $($course.creator)" -ForegroundColor Cyan
    }
}

Write-Host "`n=== Done! ===" -ForegroundColor Green
Write-Host "`nCredentials:" -ForegroundColor Yellow
Write-Host "  Teacher: teacher / teacher123" -ForegroundColor Cyan
Write-Host "  Student: newuser / newpass123 (or create new)" -ForegroundColor Cyan
Write-Host "`nFrontend: http://localhost:8080" -ForegroundColor Yellow

