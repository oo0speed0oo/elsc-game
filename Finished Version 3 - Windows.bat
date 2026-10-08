@echo off
rem ELSC Game - Finished Version 3 (Windows)
rem Double-click this file to play. It runs main.py in this folder.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 is not installed. Get it from https://www.python.org/downloads/
    echo During the install, tick "Add python.exe to PATH". Then double-click this file again.
    pause
    exit /b
)

python -c "import pygame" >nul 2>nul
if errorlevel 1 (
    echo Installing pygame, one moment...
    python -m pip install pygame
)

start "" pythonw main.py
