#!/usr/bin/env python3
"""
IG-Shop-Agent - Root App Launcher
Imports and runs the production Flask backend from backend/production_app.py
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Flask app from backend
from production_app import app

if __name__ == '__main__':
    # For development
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # For production (gunicorn)
    # gunicorn will import this file and use the 'app' object
    pass 