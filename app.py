#!/usr/bin/env python3
"""
Main application entry point for Azure Web App deployment.
This file imports the FastAPI app from the backend directory.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app from the backend
from production_app import app

# This is what uvicorn will look for
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 