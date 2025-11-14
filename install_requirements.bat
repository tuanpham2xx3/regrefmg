@echo off
REM Batch script to install Python requirements

echo ========================================
echo Installing Python Requirements
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

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Installing requirements from requirements.txt...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install requirements
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to install requirements
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Requirements installed successfully!
echo ========================================
echo.
echo You can now run the bot using:
echo   run.bat
echo   or
echo   run_loop.bat
echo.
pause

