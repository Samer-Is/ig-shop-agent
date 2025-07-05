#!/bin/bash

# Azure Web App startup script for IG-Shop-Agent Flask Backend
echo "🚀 Starting IG-Shop-Agent Flask Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
cd /home/site/wwwroot
python -m pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export ENVIRONMENT=production
export DEBUG=false

# Start the Flask application
echo "🌐 Starting Flask server on port 8000..."
uvicorn app:app --host 0.0.0.0 --port 8000 