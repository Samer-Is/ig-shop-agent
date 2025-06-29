#!/bin/bash

# Activate Python environment
cd /home/site/wwwroot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=production_app.py
export FLASK_ENV=production
export PORT=8080

# Start Gunicorn
gunicorn --bind=0.0.0.0:8080 --timeout 600 production_app:app
