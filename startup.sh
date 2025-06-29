#!/bin/bash

# Azure Web App startup script for IG-Shop-Agent Flask Backend
echo "🚀 Starting IG-Shop-Agent Flask Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export ENVIRONMENT=production
export DEBUG=false

# Start the Flask application
echo "🌐 Starting Flask server on port 8000..."
python app_simple.py 