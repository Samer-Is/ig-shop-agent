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
export PORT=${PORT:-8000}

# Make app.py executable
chmod +x app.py

# Start the application
echo "Starting FastAPI application..."
exec python app.py 