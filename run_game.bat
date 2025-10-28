@echo off
REM run_game.bat - Windows batch file to run the game

echo ================================
echo Turn-Based Combat System
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if pygame is installed
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo pygame is not installed. Installing now...
    pip install pygame
    if errorlevel 1 (
        echo ERROR: Failed to install pygame
        pause
        exit /b 1
    )
    echo pygame installed successfully!
    echo.
)

echo Starting game...
echo.
echo Controls:
echo   Arrow Keys or WASD - Navigate menus
echo   Enter or Space - Confirm selection
echo   Escape - Go back / Cancel
echo.
echo Press Ctrl+C or close window to exit
echo.

python game.py

if errorlevel 1 (
    echo.
    echo Game exited with errors
    pause
)
