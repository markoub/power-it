#!/bin/bash

# Run E2E tests with test backend and pre-seeded database
# This script starts a test backend server and runs E2E tests against it

set -e

echo "🚀 Starting E2E Tests with Test Backend"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_BACKEND_PORT=8001
BACKEND_DIR="../backend"
FRONTEND_PORT=3000

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up background processes...${NC}"
    
    # Kill test backend if running
    if [[ -n $BACKEND_PID ]]; then
        echo "Stopping test backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on test port
    lsof -ti:$TEST_BACKEND_PORT | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set up cleanup trap
trap cleanup EXIT

# Check if backend directory exists
if [[ ! -d "$BACKEND_DIR" ]]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

# Check if frontend is running on port 3000
if ! lsof -i:$FRONTEND_PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend not running on port $FRONTEND_PORT${NC}"
    echo "Please start the frontend with: cd frontend && npm run dev"
    exit 1
fi

echo -e "${BLUE}🔧 Setting up test environment...${NC}"

# Navigate to backend directory
cd "$BACKEND_DIR"

# Check if Python environment is set up
if [[ ! -f "venv/bin/python" ]]; then
    echo -e "${RED}❌ Python virtual environment not found${NC}"
    echo "Please set up the backend environment first"
    exit 1
fi

# Initialize test database
echo -e "${BLUE}🗄️  Initializing test database...${NC}"
./venv/bin/python reset_test_db.py

# Start test backend server in the background
echo -e "${BLUE}🚀 Starting test backend on port $TEST_BACKEND_PORT...${NC}"
./venv/bin/python run_api.py --test &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for test backend to start...${NC}"
sleep 5

# Check if backend is running
if ! lsof -i:$TEST_BACKEND_PORT > /dev/null 2>&1; then
    echo -e "${RED}❌ Test backend failed to start on port $TEST_BACKEND_PORT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Test backend is running on port $TEST_BACKEND_PORT${NC}"

# Verify test environment
echo -e "${BLUE}🔍 Verifying test environment...${NC}"
RESPONSE=$(curl -s "http://localhost:$TEST_BACKEND_PORT/test/environment" || echo "ERROR")

if [[ "$RESPONSE" == "ERROR" ]]; then
    echo -e "${RED}❌ Could not connect to test backend${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Test backend is responding${NC}"

# Go back to testing directory
cd - > /dev/null

# Set environment variable to use test backend
export E2E_USE_TEST_BACKEND=true
export POWERIT_OFFLINE_E2E=true

echo -e "${BLUE}🧪 Running E2E tests...${NC}"
echo "Environment variables:"
echo "  E2E_USE_TEST_BACKEND=$E2E_USE_TEST_BACKEND"
echo "  POWERIT_OFFLINE_E2E=$POWERIT_OFFLINE_E2E"
echo ""

# Parse command line arguments
TEST_ARGS=""
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --test=*)
            SPECIFIC_TEST="${1#*=}"
            TEST_ARGS="$TEST_ARGS --grep=\"$SPECIFIC_TEST\""
            shift
            ;;
        --headed)
            TEST_ARGS="$TEST_ARGS --headed"
            shift
            ;;
        --debug)
            TEST_ARGS="$TEST_ARGS --debug"
            shift
            ;;
        *)
            TEST_ARGS="$TEST_ARGS $1"
            shift
            ;;
    esac
done

# Run the tests
if [[ -n "$SPECIFIC_TEST" ]]; then
    echo -e "${BLUE}Running specific test: ${SPECIFIC_TEST}${NC}"
    npx playwright test e2e/ --grep="$SPECIFIC_TEST" $TEST_ARGS
else
    echo -e "${BLUE}Running all E2E tests with test backend${NC}"
    npx playwright test e2e/ $TEST_ARGS
fi

TEST_EXIT_CODE=$?

if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo -e "\n${BLUE}📊 Test run complete${NC}"

exit $TEST_EXIT_CODE