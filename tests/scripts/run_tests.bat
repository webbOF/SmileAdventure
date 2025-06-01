@echo off
REM Windows batch script to run tests easily

echo 🧪 SeriousGame Test Runner
echo ========================

set TEST_DIR=%~dp0..\
set PROJECT_ROOT=%~dp0..\..\

if "%1"=="" (
    echo Running ALL tests...
    python -m pytest "%TEST_DIR%" -v --tb=short
) else if "%1"=="unit" (
    echo Running UNIT tests...
    python -m pytest "%TEST_DIR%unit\" -v --tb=short
) else if "%1"=="integration" (
    echo Running INTEGRATION tests...
    python -m pytest "%TEST_DIR%integration\" -v --tb=short
) else if "%1"=="functional" (
    echo Running FUNCTIONAL tests...
    python -m pytest "%TEST_DIR%functional\" -v --tb=short
) else if "%1"=="e2e" (
    echo Running END-TO-END tests...
    python -m pytest "%TEST_DIR%end_to_end\" -v --tb=short
) else if "%1"=="performance" (
    echo Running PERFORMANCE tests...
    python -m pytest "%TEST_DIR%performance\" -v --tb=short
) else (
    echo Invalid test category: %1
    echo Usage: %0 [unit^|integration^|functional^|e2e^|performance]
    echo        %0          ^(runs all tests^)
    exit /b 1
)

echo.
echo ✅ Test execution completed!
