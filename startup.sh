#!/bin/bash

# IG-Shop-Agent Backend Startup Script
# Azure Web App startup configuration

set -e

echo "Starting IG-Shop-Agent Backend..."
echo "Environment: $ENVIRONMENT"
echo "Python version: $(python --version)"

# Set environment variables
export PYTHONPATH="/home/site/wwwroot/backend:$PYTHONPATH"
export FLASK_APP=app.py
export FLASK_ENV=production

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the FastAPI application with uvicorn
echo "Starting FastAPI application..."
cd /home/site/wwwroot
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
