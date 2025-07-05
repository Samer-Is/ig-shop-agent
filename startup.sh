#!/bin/bash
echo "Starting IG Shop Agent Backend..."
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"

# Change to the application directory
cd /home/site/wwwroot

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=/home/site/wwwroot

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} 