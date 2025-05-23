#!/bin/bash

# Script to run tests using the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run tests with specified arguments or all tests if none provided
if [ $# -eq 0 ]; then
    # Run all tests with the POWERIT_OFFLINE=true environment variable for offline testing
    POWERIT_OFFLINE=true python -m pytest tests/ -v
else
    # Run specific test file or with specific options with the POWERIT_OFFLINE=true environment variable
    POWERIT_OFFLINE=true python -m pytest "$@"
fi

# Deactivate the virtual environment when done
deactivate
