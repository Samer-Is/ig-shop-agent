#!/bin/bash

# Azure Web Apps startup script for Python FastAPI application
echo "Starting IG-Shop-Agent Backend API..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Change to application directory
cd /home/site/wwwroot

# Install dependencies if not already installed
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Start the FastAPI application with Gunicorn
echo "Starting FastAPI application with Gunicorn on port $PORT..."
python -m gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 600 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 --log-level info
