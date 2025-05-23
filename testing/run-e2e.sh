#!/bin/bash

# Run e2e tests with offline mode enabled by default for faster, more reliable tests
# 
# Usage:
#   ./run-e2e.sh                    # Run with offline mode (default)
#   POWERIT_OFFLINE_E2E=false ./run-e2e.sh  # Run with online mode (actual API calls)

echo "🧪 Running PowerIt E2E Tests"
echo "=============================="

# Check if POWERIT_OFFLINE_E2E is set, default to true for faster tests
OFFLINE_MODE=${POWERIT_OFFLINE_E2E:-true}

if [ "$OFFLINE_MODE" = "false" ]; then
    echo "🌐 Running tests in ONLINE mode (will make actual API calls)"
    echo "⚠️  This may take longer and requires valid API keys"
    BACKEND_OFFLINE="false"
    TEST_TIMEOUT="900" # 15 minutes for online tests
else
    echo "⚡ Running tests in OFFLINE mode (using mock responses)"
    echo "💡 To run with actual API calls, use: POWERIT_OFFLINE_E2E=false ./run-e2e.sh"
    BACKEND_OFFLINE="true"
    TEST_TIMEOUT="300" # 5 minutes for offline tests
fi

echo ""
echo "📋 Prerequisites:"
echo "  ✓ Frontend server running on http://localhost:3000"
echo "  ✓ Backend server running on http://localhost:8000"
echo ""

# Configure backend for offline mode before running tests
echo "🔧 Configuring backend for offline mode..."

# Check if backend is running
if curl -s -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is accessible"
    
    # Try to check if the health endpoint is available (new backend)
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "🎯 Using backend API to configure offline mode..."
        
        # Configure backend offline mode via the /health/config endpoint
        if [ "$BACKEND_OFFLINE" = "true" ]; then
            RESPONSE=$(curl -s -X POST "http://localhost:8000/health/config" \
                -H "Content-Type: application/json" \
                -d '{"offline": true}' 2>/dev/null)
        else
            RESPONSE=$(curl -s -X POST "http://localhost:8000/health/config" \
                -H "Content-Type: application/json" \
                -d '{"offline": false}' 2>/dev/null)
        fi
        
        if echo "$RESPONSE" | grep -q '"status": "updated"' 2>/dev/null; then
            echo "✅ Backend configured successfully for $BACKEND_OFFLINE mode"
        else
            echo "⚠️  Backend configuration response: $RESPONSE"
        fi
    else
        echo "ℹ️  Using older backend - relying on environment variables"
    fi
    
    # Export environment variables for test processes
    export POWERIT_OFFLINE=$BACKEND_OFFLINE
    export POWERIT_OFFLINE_E2E=$OFFLINE_MODE
    
    echo "⚙️  Environment variables set:"
    echo "   • POWERIT_OFFLINE: $POWERIT_OFFLINE"
    echo "   • POWERIT_OFFLINE_E2E: $POWERIT_OFFLINE_E2E"
    
else
    echo "❌ Backend not accessible at http://localhost:8000"
    echo "   Please start the backend server before running e2e tests"
    exit 1
fi

# Check if frontend is running
if curl -s -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not accessible at http://localhost:3000"
    echo "   Please start the frontend server before running e2e tests"
    exit 1
fi

echo ""

# Function to run tests with timeout
run_tests_with_timeout() {
    echo "🚀 Starting Playwright tests (timeout: ${TEST_TIMEOUT}s)..."
    echo "⏱️  Progress will be shown below:"
    echo ""
    
    # Run playwright with timeout using GNU timeout if available, otherwise use built-in timeout
    if command -v timeout > /dev/null 2>&1; then
        timeout ${TEST_TIMEOUT}s npx playwright test "$@"
    elif command -v gtimeout > /dev/null 2>&1; then
        # macOS with coreutils
        gtimeout ${TEST_TIMEOUT}s npx playwright test "$@"
    else
        # Fallback: run normally but warn about no timeout
        echo "⚠️  No timeout utility found - tests may run indefinitely"
        npx playwright test "$@"
    fi
}

# Run the playwright tests with environment variables set
run_tests_with_timeout "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo ""
    echo "⏰ Tests timed out after ${TEST_TIMEOUT} seconds"
    echo "   This may indicate hanging tests or slow performance"
    exit 1
elif [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All e2e tests passed!"
else
    echo ""
    echo "❌ Some e2e tests failed (exit code: $EXIT_CODE)"
    echo "📊 To view test results: npx playwright show-report"
fi

exit $EXIT_CODE 