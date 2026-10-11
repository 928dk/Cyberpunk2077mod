#!/bin/bash
# CLI launcher for project

cd "$(dirname "$0")"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run CLI
python3 -m src.cli "$@"
# Or run main module
# python3 -m src.main "$@"
# Or run specific script
# python3 src/main.py "$@"