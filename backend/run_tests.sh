#!/bin/bash

# Script to run tests using the virtual environment

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
    # Run all tests with the RUN_ORCHESTRATOR_TEST=true environment variable
    RUN_ORCHESTRATOR_TEST=true python -m pytest tests/ -v
else
    # Run specific test file or with specific options with the RUN_ORCHESTRATOR_TEST=true environment variable
    RUN_ORCHESTRATOR_TEST=true python -m pytest "$@"
fi

# Deactivate the virtual environment when done
deactivate
