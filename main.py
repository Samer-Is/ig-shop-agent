#!/usr/bin/env python3
"""
IG-Shop-Agent - Main Entry Point for Azure Web Apps
This is the main entry point that Azure Web Apps will execute.
Imports the FastAPI application from the root directory.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_paths():
    """Setup the Python path to include necessary directories"""
    current_dir = Path(__file__).parent
    
    # Add current directory to Python path for imports
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Add backend directory to Python path for middleware imports
    backend_dir = current_dir / "backend"
    if backend_dir.exists() and str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
        logger.info(f"✅ Added backend directory to Python path: {backend_dir}")
    
    logger.info(f"✅ Added root directory to Python path: {current_dir}")
    return current_dir

def create_app():
    """Create and configure the FastAPI application"""
    try:
        # Setup paths
        setup_paths()
        
        # Import the FastAPI app from root directory
        from app import app
        
        logger.info("✅ Successfully imported FastAPI application from app.py")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to import FastAPI application: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise

# Create the app instance for Azure Web Apps
app = create_app()

# For Azure Web Apps compatibility
application = app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting FastAPI server on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    ) 