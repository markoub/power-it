#!/bin/bash

# Script to run the delete-presentation test with proper test environment setup
# This script ensures the test backend and frontend are running with the test database

echo "🧪 Running Delete Presentation Test"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if test backend is running on port 8001
if curl -s -f http://localhost:8001/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Test backend is running on port 8001${NC}"
else
    echo -e "${RED}❌ Test backend not running on port 8001${NC}"
    echo -e "${YELLOW}Please start it with: cd backend && POWERIT_ENV=test ./venv/bin/python run_api.py${NC}"
    exit 1
fi

# Check if test frontend is running on port 3001
if curl -s -f http://localhost:3001/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Test frontend is running on port 3001${NC}"
else
    echo -e "${RED}❌ Test frontend not running on port 3001${NC}"
    echo -e "${YELLOW}Please start it with: cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev -- -p 3001${NC}"
    exit 1
fi

echo ""
echo "🔄 Running delete-presentation test..."
echo ""

# Set the environment variables for the test
export PLAYWRIGHT_BASE_URL=http://localhost:3001
export E2E_USE_TEST_BACKEND=true
export POWERIT_OFFLINE_E2E=false  # Use real backend for these tests

# Run the specific test
cd "$(dirname "$0")"
npx playwright test e2e/delete-presentation.spec.ts

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Delete presentation tests passed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Delete presentation tests failed (exit code: $EXIT_CODE)${NC}"
    echo "📊 To view test results: npx playwright show-report"
fi

exit $EXIT_CODE