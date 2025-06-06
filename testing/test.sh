#!/bin/bash

# Simple E2E Test Runner
# Usage: ./test.sh [options] [test-file]
# Options:
#   --force-restart    Kill and restart servers even if they're running
#   --headed          Run tests with visible browser

set -e

# Configuration
TEST_BACKEND_PORT=8001
TEST_FRONTEND_PORT=3001
FORCE_RESTART=false
PLAYWRIGHT_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force-restart)
      FORCE_RESTART=true
      shift
      ;;
    --headed)
      PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS --headed"
      shift
      ;;
    *)
      # Assume it's a test file or playwright argument
      PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS $1"
      shift
      ;;
  esac
done

# Function to check if a server is running
is_server_running() {
  local port=$1
  lsof -i:$port | grep LISTEN >/dev/null 2>&1
}

# Function to wait for server with timeout
wait_for_server() {
  local port=$1
  local name=$2
  local timeout=10  # 10 seconds timeout for offline mode
  local elapsed=0
  
  echo "⏳ Waiting for $name on port $port..."
  while ! curl -s "http://localhost:$port" >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
      echo "❌ Timeout waiting for $name to start (${timeout}s)"
      exit 1
    fi
    sleep 0.5
    elapsed=$((elapsed + 1))
  done
  echo "✅ $name is ready"
}

# Check if we need to start servers
NEED_BACKEND_START=false
NEED_FRONTEND_START=false

if [ "$FORCE_RESTART" = true ]; then
  echo "🔄 Force restart requested, killing existing servers..."
  lsof -ti:$TEST_BACKEND_PORT | xargs kill -9 2>/dev/null || true
  lsof -ti:$TEST_FRONTEND_PORT | xargs kill -9 2>/dev/null || true
  NEED_BACKEND_START=true
  NEED_FRONTEND_START=true
  # Always reset database on force restart
  cd ../backend
  echo "📊 Resetting test database..."
  ./venv/bin/python reset_test_db.py
else
  # Check if servers are already running
  if is_server_running $TEST_BACKEND_PORT; then
    echo "✅ Test backend already running on port $TEST_BACKEND_PORT"
  else
    NEED_BACKEND_START=true
  fi
  
  if is_server_running $TEST_FRONTEND_PORT; then
    echo "✅ Test frontend already running on port $TEST_FRONTEND_PORT"
  else
    NEED_FRONTEND_START=true
  fi
fi

# Start backend if needed
if [ "$NEED_BACKEND_START" = true ]; then
  echo "🔧 Starting test backend on port $TEST_BACKEND_PORT..."
  cd ../backend
  # Reset database only if not force restart (already done above)
  if [ "$FORCE_RESTART" != true ]; then
    echo "📊 Resetting test database..."
    ./venv/bin/python reset_test_db.py
  fi
  echo "🚀 Starting backend in OFFLINE mode (using VCR fixtures)..."
  # Run backend in offline mode by default for E2E tests
  POWERIT_ENV=test POWERIT_OFFLINE=1 ./venv/bin/python run_api.py --test &
  BACKEND_PID=$!
  wait_for_server $TEST_BACKEND_PORT "backend"
  
  # Verify test data
  echo "🔍 Verifying test presentations..."
  curl -s "http://localhost:$TEST_BACKEND_PORT/test/presentations" | grep -o '"id":[0-9]*' | head -5 || {
    echo "❌ Failed to verify test data"
    exit 1
  }
fi

# Start frontend if needed
if [ "$NEED_FRONTEND_START" = true ]; then
  echo "🌐 Starting test frontend on port $TEST_FRONTEND_PORT..."
  cd ../frontend
  NEXT_PUBLIC_API_URL="http://localhost:$TEST_BACKEND_PORT" PORT=$TEST_FRONTEND_PORT npm run dev &
  FRONTEND_PID=$!
  wait_for_server $TEST_FRONTEND_PORT "frontend"
fi

# Run tests with short timeouts for offline mode
cd ../testing
echo "🧪 Running tests in OFFLINE mode with fast timeouts..."
echo "📝 Test command: npx playwright test $PLAYWRIGHT_ARGS"

# Set aggressive timeouts for offline mode
export PLAYWRIGHT_BASE_URL="http://localhost:$TEST_FRONTEND_PORT"
export POWERIT_OFFLINE_E2E=true

# Run tests with custom timeout configuration and test frontend URL
PLAYWRIGHT_BASE_URL=http://localhost:$TEST_FRONTEND_PORT npx playwright test \
  --timeout=15000 \
  --retries=1 \
  $PLAYWRIGHT_ARGS

TEST_RESULT=$?

# Only cleanup if we started the servers
if [ "$NEED_BACKEND_START" = true ] && [ -n "$BACKEND_PID" ]; then
  echo "🧹 Stopping test backend..."
  kill $BACKEND_PID 2>/dev/null || true
fi

if [ "$NEED_FRONTEND_START" = true ] && [ -n "$FRONTEND_PID" ]; then
  echo "🧹 Stopping test frontend..."
  kill $FRONTEND_PID 2>/dev/null || true
fi

if [ $TEST_RESULT -eq 0 ]; then
  echo "✅ Tests passed!"
else
  echo "❌ Tests failed!"
fi

exit $TEST_RESULT