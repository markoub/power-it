#!/bin/bash

# Script to run tests using the virtual environment

# Activate the virtual environment
source venv/bin/activate

# Run tests with specified arguments or all tests if none provided
if [ $# -eq 0 ]; then
    # Run all tests, but exclude problematic ones
    python -m pytest tests/ -v -k "not image and not openai and not pptx_core and not test_orchestrator"
else
    # Run specific test file or with specific options
    python -m pytest "$@"
fi

# Deactivate the virtual environment when done
deactivate 