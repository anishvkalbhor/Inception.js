@echo off
REM VICTOR Offline System - Optimized Startup Script

title VICTOR Offline System Starter

echo.
echo ============================================================
echo    VICTOR OFFLINE RAG SYSTEM - OPTIMIZED STARTUP
echo ============================================================
echo.
echo This will start all services for OFFLINE operation:
echo   [Docker] MongoDB + Milvus (databases)
echo   [Host]   Ollama (LLM - faster on host!)
echo   [Host]   Backend API (FastAPI)
echo   [Host]   Frontend (Next.js)
echo.
echo ============================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

echo [1/5] Starting databases in Docker...
echo.
cd /d d:\Inception.js\infrastructure\docker
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start Docker services!
    pause
    exit /b 1
)

echo.
echo [2/5] Waiting for databases to initialize (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo [3/5] Starting Ollama (LOCAL LLM - No Internet Required)...
echo.
start "Ollama Server" cmd /k "echo Starting Ollama on http://localhost:11434 && echo. && ollama serve"
timeout /t 5 /nobreak >nul

echo.
echo [4/5] Starting Backend API...
echo.
start "VICTOR Backend" cmd /k "cd /d d:\Inception.js\backend && title VICTOR Backend API && python start_offline.py"
timeout /t 10 /nobreak >nul

echo.
echo [5/5] Starting Frontend...
echo.
start "VICTOR Frontend" cmd /k "cd /d d:\Inception.js\frontend && title VICTOR Frontend && npm run dev"

echo.
echo ============================================================
echo    ALL SERVICES STARTED!
echo ============================================================
echo.
echo Services are running at:
echo.
echo   [Database] MongoDB:   http://localhost:27017
echo   [Database] Milvus:    http://localhost:19530
echo   [LLM]      Ollama:    http://localhost:11434
echo   [Backend]  API:       http://localhost:8000
echo   [Backend]  Docs:      http://localhost:8000/docs
echo   [Frontend] App:       http://localhost:3000
echo.
echo ============================================================
echo   SYSTEM IS RUNNING 100%% OFFLINE!
echo   No Internet Connection Required!
echo ============================================================
echo.
echo To check status: check-status.bat
echo To stop all:     stop-offline.bat
echo.
echo Press any key to exit this window...
echo (Services will continue running in separate windows)
echo.
pause