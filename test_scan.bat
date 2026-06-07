@echo off
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title Chest Tracker NBT Scanner

echo ===================================================
echo   Chest Tracker NBT Scanner
echo ===================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Install Python: https://python.org/downloads
    echo.
    pause
    exit /b 1
)

echo Python OK.
echo.
echo Drag and drop the .nbt file here, or paste the path:
echo.
set /p "NBT_PATH=Path: "

set NBT_PATH=%NBT_PATH:"=%

if not exist "%NBT_PATH%" (
    echo.
    echo [ERROR] File not found: %NBT_PATH%
    echo.
    pause
    exit /b 1
)

echo.
echo Scanning...
echo.

python "%~dp0test_scan.py" "%NBT_PATH%"

echo.
pause
