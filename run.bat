@echo off
REM Batch script to run the account registration bot
REM This script will run the main.py Python script

echo ========================================
echo Account Registration Bot
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

echo Starting bot...
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Run the Python script
python main.py

REM Check if script exited with error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Script exited with error code: %errorlevel%
    echo ========================================
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo Script completed successfully
echo ========================================
pause

