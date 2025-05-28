# healthchecks.ps1
# PowerShell script to check the health status of SmileAdventure microservices

Write-Host "Starting SmileAdventure Health Checks..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Function to check HTTP services
function Test-HttpService {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$ExpectedCode = 200
    )
    
    $paddedName = $ServiceName.PadRight(20)
    $paddedUrl = $Url.PadRight(35)
    Write-Host "$paddedName $paddedUrl " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq $ExpectedCode) {
            Write-Host "✓ OK" -ForegroundColor Green -NoNewline
            Write-Host " ($($response.StatusCode))"
            return $true
        }
        else {
            Write-Host "✗ FAIL" -ForegroundColor Red -NoNewline
            Write-Host " ($($response.StatusCode))"
            return $false
        }
    }
    catch {
        Write-Host "✗ FAIL" -ForegroundColor Red -NoNewline
        Write-Host " (Connection failed)"
        return $false
    }
}

# Function to check Docker container health
function Test-DockerHealth {
    param(
        [string]$ServiceName,
        [string]$ContainerName
    )
    
    $paddedName = $ServiceName.PadRight(20)
    $paddedContainer = "Container: $ContainerName".PadRight(35)
    Write-Host "$paddedName $paddedContainer " -NoNewline
    
    try {
        # Check if Docker is available
        $null = docker --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠ SKIP" -ForegroundColor Yellow -NoNewline
            Write-Host " (Docker not available)"
            return $null
        }
        
        # Check if container exists and is running
        $containerStatus = docker inspect --format='{{.State.Status}}' $ContainerName 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ NOT FOUND" -ForegroundColor Red
            return $false
        }
        
        if ($containerStatus -eq "running") {
            # Check health status if available
            $healthStatus = docker inspect --format='{{.State.Health.Status}}' $ContainerName 2>$null
            
            switch ($healthStatus) {
                "healthy" {
                    Write-Host "✓ HEALTHY" -ForegroundColor Green
                    return $true
                }
                "unhealthy" {
                    Write-Host "✗ UNHEALTHY" -ForegroundColor Red
                    return $false
                }
                "starting" {
                    Write-Host "⟳ STARTING" -ForegroundColor Yellow
                    return $null
                }
                default {
                    Write-Host "✓ RUNNING" -ForegroundColor Green -NoNewline
                    Write-Host " (no healthcheck)"
                    return $true
                }
            }
        }
        else {
            Write-Host "✗ NOT RUNNING" -ForegroundColor Red -NoNewline
            Write-Host " ($containerStatus)"
            return $false
        }
    }
    catch {
        Write-Host "✗ ERROR" -ForegroundColor Red -NoNewline
        Write-Host " ($($_.Exception.Message))"
        return $false
    }
}

# Initialize counters
$totalChecks = 0
$passedChecks = 0
$failedChecks = 0
$skippedChecks = 0

# Function to update counters
function Update-Counters {
    param($result)
    
    $script:totalChecks++
    if ($result -eq $true) {
        $script:passedChecks++
    }
    elseif ($result -eq $false) {
        $script:failedChecks++
    }
    else {
        $script:skippedChecks++
    }
}

Write-Host ""
Write-Host "HTTP Service Health Checks:" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

# API Gateway
Update-Counters (Test-HttpService "API Gateway" "http://localhost:8000/status")

# Auth Service
Update-Counters (Test-HttpService "Auth Service" "http://localhost:8001/status")

# Users Service
Update-Counters (Test-HttpService "Users Service" "http://localhost:8006/status")

# Reports Service
Update-Counters (Test-HttpService "Reports Service" "http://localhost:8007/status")

# Web Frontend
Update-Counters (Test-HttpService "Web Frontend" "http://localhost:3000")

Write-Host ""
Write-Host "Docker Container Health Checks:" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

# PostgreSQL Database
Update-Counters (Test-DockerHealth "PostgreSQL DB" "smileadventure-postgres-db")

# API Gateway Container
Update-Counters (Test-DockerHealth "API Gateway" "smileadventure-api-gateway")

# Auth Service Container
Update-Counters (Test-DockerHealth "Auth Service" "smileadventure-auth-service")

# Users Service Container
Update-Counters (Test-DockerHealth "Users Service" "smileadventure-users-service")

# Reports Service Container
Update-Counters (Test-DockerHealth "Reports Service" "smileadventure-reports-service")

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Health Check Summary:" -ForegroundColor Cyan
Write-Host "  Total checks: $totalChecks"
Write-Host "  Passed: $passedChecks" -ForegroundColor Green
Write-Host "  Failed: $failedChecks" -ForegroundColor Red
Write-Host "  Skipped: $skippedChecks" -ForegroundColor Yellow

if ($failedChecks -eq 0) {
    Write-Host ""
    Write-Host "🎉 All services are healthy!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host ""
    Write-Host "⚠️  Some services have issues. Check the logs above." -ForegroundColor Red
    exit 1
}
