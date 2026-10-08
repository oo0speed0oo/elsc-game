#!/bin/bash
# ELSC Game - Finished Version 3 (Linux)
# Run it from a terminal:   ./"Finished Version 3 - Linux.sh"
# (or right-click it in your file manager and choose "Run as a Program").

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Install it with your package manager, for example:"
    echo "    sudo apt install python3 python3-pip"
    exit 1
fi

if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame, one moment..."
    if ! python3 -m pip install --user pygame; then
        echo "pip could not install pygame here. Try your package manager instead, for example:"
        echo "    sudo apt install python3-pygame"
        exit 1
    fi
fi

python3 main.py
