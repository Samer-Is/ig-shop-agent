#!/bin/bash

# Navigate to app directory
cd /home/site/wwwroot

# Create and activate virtual environment if it doesn't exist
if [ ! -d "antenv" ]; then
    python -m venv antenv
fi
source antenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=production_app.py
export FLASK_ENV=production
export PORT=8080

# Start Gunicorn
gunicorn --bind=0.0.0.0:8080 --timeout 600 production_app:app
