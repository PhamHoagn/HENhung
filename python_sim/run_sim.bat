@echo off
REM HIL Robocar Simulation - Windows Launcher
REM This script runs the Python simulation

echo =========================================
echo   HIL ROBOCAR SIMULATION - LAUNCHER
echo =========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [1/2] Checking dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo   OK - Dependencies installed

echo.
echo [2/2] Starting simulation...
echo.
echo =========================================
echo.

REM Run the simulation
python -m robocar_sim.main %*

echo.
echo =========================================
echo   Simulation ended
echo =========================================
pause
