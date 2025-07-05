#!/bin/bash

# Azure Web App Deployment Script for IG-Shop-Agent

echo "Starting deployment..."

# Exit on any error
set -e

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Deployment completed successfully!" 