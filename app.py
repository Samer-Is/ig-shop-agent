#!/usr/bin/env python3
"""
IG-Shop-Agent - Main Application Entry Point
This file serves as the entry point for the FastAPI application.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set required environment variables if not set
if not os.getenv('META_APP_ID'):
    os.environ['META_APP_ID'] = 'placeholder'
if not os.getenv('META_APP_SECRET'):
    os.environ['META_APP_SECRET'] = 'placeholder'
if not os.getenv('OPENAI_API_KEY'):
    os.environ['OPENAI_API_KEY'] = 'placeholder'
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'

try:
    # Import the complete FastAPI application from backend directory
    from backend.app import app
    logger.info("✅ Successfully imported FastAPI application from backend")
    
    # Verify app is properly configured
    logger.info(f"✅ App title: {app.title}")
    logger.info(f"✅ Routes configured: {len(app.routes)}")
    
except Exception as e:
    logger.error(f"❌ Failed to import FastAPI application: {e}")
    raise

# If running directly, start the server
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"🚀 Starting FastAPI server on port {port}")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 