#!/bin/bash
# GUI launcher for project

cd "$(dirname "$0")"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Launch GUI
python3 -m tkinter src/main.py "$@"
# Or use specific GUI module
# python3 src/gui.py "$@"