#!/bin/bash
# ELSC Game - Finished Version 3 (Mac)
# Double-click this file to play. It runs main.py in this folder with Python 3.
# The first time, macOS may block it: right-click it and choose Open
# (or System Settings > Privacy & Security > Open Anyway).

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Get it from https://www.python.org/downloads/ and try again."
    read -r -p "Press Enter to close."
    exit 1
fi

if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame, one moment..."
    python3 -m pip install --user pygame
fi

python3 main.py
