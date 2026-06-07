@echo off
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title ME Terminal

echo ==========================================
echo   ME Terminal - Chest Tracker
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    pause
    exit /b 1
)

echo [1/2] Starting Python API server on :8000...
start "" /b python "%~dp0server.py"

echo [2/2] Starting Next.js frontend on :3000...
cd /d "%~dp0frontend"
start "" /b cmd /c "npm run dev"

echo.
echo   Frontend: http://127.0.0.1:3000
echo   API:      http://127.0.0.1:8000
echo.
echo   Press any key to stop...
echo ==========================================
pause >nul
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
