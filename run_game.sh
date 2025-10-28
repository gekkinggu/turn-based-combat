#!/bin/bash
# run_game.sh - Unix/Linux/Mac shell script to run the game

echo "================================"
echo "Turn-Based Combat System"
echo "================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "Python found!"
echo

# Check if pygame is installed
python3 -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "pygame is not installed. Installing now..."
    pip3 install pygame
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install pygame"
        exit 1
    fi
    echo "pygame installed successfully!"
    echo
fi

echo "Starting game..."
echo
echo "Controls:"
echo "  Arrow Keys or WASD - Navigate menus"
echo "  Enter or Space - Confirm selection"
echo "  Escape - Go back / Cancel"
echo
echo "Press Ctrl+C or close window to exit"
echo

python3 game.py

if [ $? -ne 0 ]; then
    echo
    echo "Game exited with errors"
    read -p "Press Enter to continue..."
fi
