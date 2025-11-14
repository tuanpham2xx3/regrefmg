@echo off
REM Batch script to run the account registration bot in a loop
REM This script will restart the bot if it crashes

echo ========================================
echo Account Registration Bot (Auto Restart)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

:LOOP
echo ========================================
echo Starting bot... (Press Ctrl+C twice to exit)
echo ========================================
echo.

REM Run the Python script
python main.py
set EXIT_CODE=%errorlevel%

if %EXIT_CODE%==0 (
    echo.
    echo ========================================
    echo Bot stopped normally
    echo ========================================
    pause
    exit /b 0
)

if %EXIT_CODE%==130 (
    echo.
    echo ========================================
    echo Bot stopped by user (Ctrl+C)
    echo ========================================
    pause
    exit /b 0
)

echo.
echo ========================================
echo Bot crashed with error code: %EXIT_CODE%
echo Restarting in 5 seconds...
echo Press Ctrl+C to stop
echo ========================================
echo.

timeout /t 5 /nobreak >nul

goto LOOP

