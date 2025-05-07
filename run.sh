#!/bin/bash

# Start backend server in the background
cd backend
echo "Starting backend API server..."
./venv/bin/python run_api.py &
BACKEND_PID=$!

# Wait a bit for the backend to start
sleep 2

# Start frontend server
cd ../frontend
echo "Starting frontend Next.js server..."
npm run dev

# Clean up when script is terminated
function cleanup {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  exit
}

# Set up trap for script termination
trap cleanup SIGINT SIGTERM

# Wait for child processes
wait 