#!/bin/bash

# Script to run all tests in recording mode, making real API calls
# This is useful to verify that all tests work properly with actual APIs

echo "⚠️  WARNING: Running ALL tests with REAL API CALLS ⚠️"
echo "This will incur costs for API usage and may take a long time."
echo "Make sure your API keys are set in .env or environment variables."
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Aborted."
    exit 0
fi

# Determine script directory and use its virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate the virtual environment
source venv/bin/activate

# Set all VCR environment variables to record mode
export GEMINI_VCR_MODE=record
export OPENAI_VCR_MODE=record
export PRESENTATION_VCR_MODE=record
export TOC_FONT_VCR_MODE=record
export TEMPLATE_PPTX_VCR_MODE=record
export IMAGE_API_VCR_MODE=record

# Check for API keys
if [ -z "$GEMINI_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    if [ -f .env ]; then
        echo "Loading API keys from .env file"
        source .env
    else
        echo "WARNING: API keys not found. Tests will likely fail."
        echo "Create a .env file with GEMINI_API_KEY and OPENAI_API_KEY."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]
        then
            echo "Aborted."
            exit 0
        fi
    fi
fi

# Warn about API integration tests
echo ""
echo "⚠️  NOTE: API integration tests require the API server to be running."
echo "If you want to test API integration, start the server in another terminal with:"
echo "./run_api.py"
echo ""
read -p "Continue with test run? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]
then
    echo "Aborted."
    exit 0
fi

# Run all tests with recording mode
echo "Running all tests in RECORDING mode..."
python -m pytest tests/ -v

# Unset recording mode variables
unset GEMINI_VCR_MODE
unset OPENAI_VCR_MODE
unset PRESENTATION_VCR_MODE
unset TOC_FONT_VCR_MODE
unset TEMPLATE_PPTX_VCR_MODE
unset IMAGE_API_VCR_MODE

# Deactivate the virtual environment when done
deactivate

echo ""
echo "✅ All tests completed in recording mode."
echo "New fixtures have been created in the tests/fixtures directory."
echo "Future test runs will use these fixtures by default unless recording mode is enabled."
