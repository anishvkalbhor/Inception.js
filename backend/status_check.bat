@echo off
REM filepath: d:\meow\check-status.bat
REM Check if all services are running

title VICTOR Status Check

echo.
echo ============================================================
echo    VICTOR OFFLINE SYSTEM - STATUS CHECK
echo ============================================================
echo.

echo Checking services...
echo.

REM Check Docker containers
echo [Docker Services]
docker ps --filter "name=victor" --filter "name=milvus" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] Ollama:    RUNNING on http://localhost:11434
) else (
    echo [✗] Ollama:    NOT RUNNING
)

REM Check Backend
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] Backend:   RUNNING on http://localhost:8000
) else (
    echo [✗] Backend:   NOT RUNNING
)

REM Check Frontend
curl -s http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] Frontend:  RUNNING on http://localhost:3000
) else (
    echo [✗] Frontend:  NOT RUNNING
)

echo.
echo ============================================================
echo.
pause   