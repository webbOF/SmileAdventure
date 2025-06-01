#!/bin/bash
# PowerShell script to run tests with better Windows integration

param(
    [Parameter(Position = 0)]
    [ValidateSet("unit", "integration", "functional", "e2e", "performance", "all", "")]
    [string]$TestCategory = "all",
    
    [switch]$Quiet,
    [switch]$Coverage,
    [switch]$Watch
)

# Get script directory and project paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$TestsDir = Join-Path $ScriptDir ".."
$ProjectRoot = Join-Path $ScriptDir "..\..\"

Write-Host "🧪 SeriousGame Test Runner" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Build pytest command
$PytestCmd = @("python", "-m", "pytest")

# Determine test directory
if ($TestCategory -eq "all" -or $TestCategory -eq "") {
    $PytestCmd += $TestsDir
    Write-Host "Running ALL tests..." -ForegroundColor Yellow
}
else {
    $CategoryDir = Join-Path $TestsDir $TestCategory
    if (-not (Test-Path $CategoryDir)) {
        Write-Error "Test category '$TestCategory' directory does not exist at $CategoryDir"
        exit 1
    }
    $PytestCmd += $CategoryDir
    Write-Host "Running $($TestCategory.ToUpper()) tests..." -ForegroundColor Yellow
}

# Add verbosity options
if (-not $Quiet) {
    $PytestCmd += @("-v", "--tb=short")
}

# Add coverage options
if ($Coverage) {
    $PytestCmd += @("--cov=microservices", "--cov-report=html", "--cov-report=term")
    Write-Host "📊 Coverage reporting enabled" -ForegroundColor Green
}

# Add watch mode (if pytest-watch is installed)
if ($Watch) {
    $PytestCmd[1] = "ptw"  # Replace pytest with pytest-watch
    Write-Host "👀 Watch mode enabled" -ForegroundColor Green
}

Write-Host "📁 Test directory: $TestsDir" -ForegroundColor Gray
Write-Host "💻 Command: $($PytestCmd -join ' ')" -ForegroundColor Gray
Write-Host ""

# Change to project root and run tests
Push-Location $ProjectRoot
try {
    & $PytestCmd[0] $PytestCmd[1..($PytestCmd.Length - 1)]
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Tests completed successfully!" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "❌ Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
