# Script to create a lesson with images
# Usage: .\create-lesson-with-images.ps1 -CourseId 1 -Title "Lesson Title" -Content "Lesson content" -ImagePath "path/to/image.png"

param(
    [Parameter(Mandatory=$true)]
    [int]$CourseId,
    
    [Parameter(Mandatory=$true)]
    [string]$Title,
    
    [Parameter(Mandatory=$true)]
    [string]$Content,
    
    [string[]]$ImagePaths = @()
)

Write-Host "=== Creating Lesson with Images ===" -ForegroundColor Green

# 1. Login as teacher
Write-Host "`n1. Logging in as teacher..." -ForegroundColor Yellow
$body = @{
    username='teacher'
    password='teacher123'
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/login `
        -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
    $token = ($response.Content | ConvertFrom-Json).token
    Write-Host "   Token obtained!" -ForegroundColor Green
} catch {
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Process images
Write-Host "`n2. Processing images..." -ForegroundColor Yellow
$images = @()

if ($ImagePaths.Count -gt 0) {
    foreach ($imagePath in $ImagePaths) {
        if (Test-Path $imagePath) {
            try {
                $imageBytes = [System.IO.File]::ReadAllBytes($imagePath)
                $imageBase64 = [Convert]::ToBase64String($imageBytes)
                $imageExtension = [System.IO.Path]::GetExtension($imagePath).TrimStart('.')
                $mimeType = switch ($imageExtension.ToLower()) {
                    'jpg' { 'image/jpeg' }
                    'jpeg' { 'image/jpeg' }
                    'png' { 'image/png' }
                    'gif' { 'image/gif' }
                    'webp' { 'image/webp' }
                    default { 'image/png' }
                }
                
                $images += @{
                    data = $imageBase64
                    type = $mimeType
                    name = [System.IO.Path]::GetFileName($imagePath)
                }
                Write-Host "   Added: $imagePath" -ForegroundColor Green
            } catch {
                Write-Host "   Error processing $imagePath : $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "   File not found: $imagePath" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   No images provided (using text only)" -ForegroundColor Cyan
}

# 3. Create lesson
Write-Host "`n3. Creating lesson..." -ForegroundColor Yellow
$headers = @{
    Authorization="Bearer $token"
}

$lessonBody = @{
    title=$Title
    content=$Content
    images=$images
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri http://localhost:5000/api/courses/$CourseId/lessons `
        -Method POST -Body $lessonBody -ContentType 'application/json' `
        -Headers $headers -UseBasicParsing
    
    $lesson = $response.Content | ConvertFrom-Json
    Write-Host "   Lesson created successfully!" -ForegroundColor Green
    Write-Host "   ID: $($lesson.id)" -ForegroundColor Cyan
    Write-Host "   Title: $($lesson.title)" -ForegroundColor Cyan
    Write-Host "   Images: $($lesson.images.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`n=== Done! ===" -ForegroundColor Green

