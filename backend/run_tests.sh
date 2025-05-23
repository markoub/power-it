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
# Ensure test environment variables
export POWERIT_ENV=test
# Use dedicated test database file if provided
export DATABASE_FILE="${TEST_DATABASE_FILE:-${DATABASE_FILE:-presentations_test.db}}"

if [ $# -eq 0 ]; then
    # Run all tests with offline mode enabled
    POWERIT_OFFLINE=true python -m pytest tests/ -v
else
    # Run specific test file or with specific options
    POWERIT_OFFLINE=true python -m pytest "$@"
fi

# Deactivate the virtual environment when done
deactivate
