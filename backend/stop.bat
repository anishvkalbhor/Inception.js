@echo off
REM filepath: d:\meow\stop-offline.bat
REM Stop all VICTOR services

title VICTOR Offline System - Shutdown

echo.
echo ============================================================
echo    STOPPING VICTOR OFFLINE SYSTEM
echo ============================================================
echo.

echo [1/3] Stopping Docker services...
cd /d d:\meow\infrastructure\docker
docker-compose down

echo.
echo [2/3] Stopping Ollama...
taskkill /FI "WINDOWTITLE eq Ollama*" /T /F 2>nul

echo.
echo [3/3] Stopping Backend and Frontend...
taskkill /FI "WINDOWTITLE eq VICTOR*" /T /F 2>nul

echo.
echo ============================================================
echo    ALL SERVICES STOPPED!
echo ============================================================
echo.
pause