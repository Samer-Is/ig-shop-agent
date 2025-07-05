#!/usr/bin/env python3
"""
IG-Shop-Agent - Main Entry Point for Azure Web Apps
This is the main entry point that Azure Web Apps will execute.
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

def create_app():
    """Create and configure the FastAPI application."""
    try:
        # Import the complete FastAPI application from backend directory
        from backend.app import app
        logger.info("✅ Successfully imported FastAPI application from backend")
        
        # Verify app is properly configured
        logger.info(f"✅ App title: {app.title}")
        logger.info(f"✅ Routes configured: {len(app.routes)}")
        
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to import FastAPI application: {e}")
        raise

# Create the app instance
app = create_app()

# For Azure Web Apps
application = app

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