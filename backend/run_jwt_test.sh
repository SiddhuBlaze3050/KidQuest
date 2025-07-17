#!/bin/bash

# Script to run JWT RBAC authentication tests

echo "Starting JWT RBAC Authentication Test"
echo "===================================="

# Check if the Flask app is running
if ! curl -s http://localhost:5000/ > /dev/null; then
    echo "Starting Flask application in the background..."
    python3 app.py > app.log 2>&1 &
    APP_PID=$!
    
    # Wait for the app to start
    echo "Waiting for Flask app to start..."
    sleep 5
    
    # Check if app started successfully
    if ! curl -s http://localhost:5000/ > /dev/null; then
        echo "Failed to start Flask application. Check app.log for details."
        exit 1
    fi
    
    echo "Flask application started with PID: $APP_PID"
else
    echo "Flask application is already running."
    APP_PID=""
fi

# Set up test users
echo "Setting up test users..."
python3 setup_test_users.py

# Run the test script
echo "Running JWT RBAC tests..."
python3 test_jwt_rbac.py

# Capture the test result
TEST_RESULT=$?

# If we started the app, shut it down
if [ -n "$APP_PID" ]; then
    echo "Stopping Flask application (PID: $APP_PID)..."
    kill $APP_PID
fi

echo "Test completed with exit code: $TEST_RESULT"
exit $TEST_RESULT