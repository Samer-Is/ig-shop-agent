#!/bin/bash

# Azure Web App startup script for Python Flask application
echo "Starting IG-Shop-Agent Backend..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH
export PORT=${PORT:-8000}

# Change to the application directory
cd /home/site/wwwroot

# Install any missing dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start the application with Gunicorn
echo "Starting Gunicorn server on port $PORT..."
exec gunicorn --bind=0.0.0.0:$PORT --timeout 600 --workers 1 --worker-class sync app_simple:app 