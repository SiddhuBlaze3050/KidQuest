#!/bin/bash

# Script to set up dependencies for KidQuest backend

echo "Setting up dependencies for KidQuest backend..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Virtual environment found."
    # Activate virtual environment
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify requests module is installed
echo "Verifying requests module..."
python3 -c "import requests; print('Requests module installed successfully!')" || {
    echo "Installing requests module specifically..."
    pip install requests
}

echo "Setup complete! You can now run the application with 'python3 app.py'"