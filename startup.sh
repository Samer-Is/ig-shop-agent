#!/bin/bash

# Azure Web App startup script for Python Flask application
echo "Starting IG-Shop-Agent Flask Backend..."

# Set environment variables if not already set
export PORT=${PORT:-8080}
export WEBSITES_PORT=${WEBSITES_PORT:-8080}

# Navigate to the application directory
cd /home/site/wwwroot

# Install dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
fi

# Start the Flask application
echo "Starting Flask app on port $PORT..."
exec python app_simple.py 