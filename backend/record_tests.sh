#!/bin/bash

# Script to run tests in recording mode

# Check for API keys
if [ -z "$GEMINI_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: GEMINI_API_KEY or OPENAI_API_KEY not found in environment."
    echo "Make sure they are set in your .env file or directly in the environment."
fi

# Activate the virtual environment
source venv/bin/activate

# Set recording mode environment variables
export GEMINI_VCR_MODE=record
export OPENAI_VCR_MODE=record

# Run tests with specified arguments or all tests if none provided
if [ $# -eq 0 ]; then
    echo "Please specify which test file(s) to record."
    echo "Example: ./record_tests.sh tests/test_integration_research.py"
    exit 1
else
    # Run specific test file(s) with recording mode
    echo "Running tests in RECORDING mode..."
    python -m pytest "$@" -v
fi

# Unset recording mode variables
unset GEMINI_VCR_MODE
unset OPENAI_VCR_MODE

# Deactivate the virtual environment when done
deactivate 