#!/bin/bash

# Comprehensive E2E Test Runner Script
# This script manages the complete test environment:
# 1. Starts test backend on port 8001
# 2. Starts test frontend on port 3001
# 3. Runs E2E tests
# 4. Cleans up everything

set -e

echo "🚀 PowerIt E2E Test Runner"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_BACKEND_PORT=8001
TEST_FRONTEND_PORT=3001
PROD_FRONTEND_PORT=3000
BACKEND_DIR="../backend"
FRONTEND_DIR="../frontend"

# Process tracking
BACKEND_PID=""
FRONTEND_PID=""

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up test environment...${NC}"
    
    # Kill test backend
    if [[ -n $BACKEND_PID ]]; then
        echo "Stopping test backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill test frontend
    if [[ -n $FRONTEND_PID ]]; then
        echo "Stopping test frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on test ports
    lsof -ti:$TEST_BACKEND_PORT | xargs kill -9 2>/dev/null || true
    lsof -ti:$TEST_FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set up cleanup trap
trap cleanup EXIT

# Note: Production frontend can continue running on port 3000
# Test environment will use different ports (backend: 8001, frontend: 3001)

# Step 1: Start test backend
echo -e "\n${BLUE}🔧 Step 1: Starting test backend...${NC}"

cd "$BACKEND_DIR"

# Initialize test database
echo "Initializing test database..."
./venv/bin/python reset_test_db.py

# Start test backend
echo "Starting backend on port $TEST_BACKEND_PORT..."
./venv/bin/python run_api.py --test > /tmp/test-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s "http://localhost:$TEST_BACKEND_PORT/test/environment" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Test backend is running${NC}"
        break
    fi
    if [[ $i -eq 30 ]]; then
        echo -e "${RED}❌ Test backend failed to start${NC}"
        echo "Backend logs:"
        tail -20 /tmp/test-backend.log
        exit 1
    fi
    sleep 1
done

# Step 2: Start test frontend
echo -e "\n${BLUE}🔧 Step 2: Starting test frontend...${NC}"

cd "$FRONTEND_DIR"
CURRENT_DIR=$(pwd)

# Check if node_modules exists
if [[ ! -d "node_modules" ]]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend with test environment
echo "Starting frontend on port $TEST_FRONTEND_PORT with test backend..."
# Use environment variables directly without touching .env.local
NEXT_PUBLIC_API_URL="http://localhost:$TEST_BACKEND_PORT" PORT=$TEST_FRONTEND_PORT npm run dev > /tmp/test-frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
for i in {1..60}; do
    if curl -s "http://localhost:$TEST_FRONTEND_PORT" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Test frontend is running${NC}"
        break
    fi
    if [[ $i -eq 60 ]]; then
        echo -e "${RED}❌ Test frontend failed to start${NC}"
        echo "Frontend logs:"
        tail -20 /tmp/test-frontend.log
        exit 1
    fi
    sleep 1
done

# Step 3: Run E2E tests
echo -e "\n${BLUE}🧪 Step 3: Running E2E tests...${NC}"

# Go back to testing directory
cd - > /dev/null

# Update Playwright to use test frontend
export PLAYWRIGHT_BASE_URL="http://localhost:$TEST_FRONTEND_PORT"
export POWERIT_OFFLINE_E2E=true

# Parse test arguments
TEST_ARGS=""
SPECIFIC_TEST=""
SKIP_RUN=false
TEST_FILES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --test=*)
            SPECIFIC_TEST="${1#*=}"
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
        --ui)
            TEST_ARGS="$TEST_ARGS --ui"
            shift
            ;;
        --check)
            SKIP_RUN=true
            shift
            ;;
        *.spec.ts|*.test.ts)
            TEST_FILES="$TEST_FILES $1"
            shift
            ;;
        *)
            TEST_ARGS="$TEST_ARGS $1"
            shift
            ;;
    esac
done

if [[ "$SKIP_RUN" == "true" ]]; then
    echo -e "${GREEN}✅ Test environment is ready!${NC}"
    echo -e "Test backend: http://localhost:$TEST_BACKEND_PORT"
    echo -e "Test frontend: http://localhost:$TEST_FRONTEND_PORT"
    echo -e "API docs: http://localhost:$TEST_BACKEND_PORT/docs"
    echo -e "\nPress Ctrl+C to stop the test environment"
    
    # Keep running until interrupted
    wait
else
    # Run the tests
    if [[ -n "$SPECIFIC_TEST" ]]; then
        echo -e "${BLUE}Running specific test: ${SPECIFIC_TEST}${NC}"
        npx playwright test --grep="$SPECIFIC_TEST" $TEST_ARGS
    elif [[ -n "$TEST_FILES" ]]; then
        echo -e "${BLUE}Running test files: ${TEST_FILES}${NC}"
        npx playwright test $TEST_FILES $TEST_ARGS
    else
        echo -e "${BLUE}Running all E2E tests${NC}"
        npx playwright test $TEST_ARGS
    fi
    
    TEST_EXIT_CODE=$?
    
    if [[ $TEST_EXIT_CODE -eq 0 ]]; then
        echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    else
        echo -e "\n${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
    fi
    
    echo -e "\n${BLUE}📊 Test run complete${NC}"
    
    # Show logs location
    echo -e "\nLogs available at:"
    echo "  Backend: /tmp/test-backend.log"
    echo "  Frontend: /tmp/test-frontend.log"
    
    exit $TEST_EXIT_CODE
fi