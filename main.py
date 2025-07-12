#!/usr/bin/env python3
"""
IG-Shop-Agent - Main Entry Point for Azure Web Apps
This is the main entry point that Azure Web Apps will execute.
Imports the FastAPI application from the backend directory.
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

def setup_backend_path():
    """Setup the Python path to include the backend directory"""
    current_dir = Path(__file__).parent
    backend_dir = current_dir / "backend"
    
    if not backend_dir.exists():
        raise ImportError(f"Backend directory not found at {backend_dir}")
    
    # Add backend directory to Python path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    logger.info(f"✅ Added backend directory to Python path: {backend_dir}")
    return backend_dir

def create_app():
    """Create and configure the FastAPI application from backend"""
    try:
        # Setup backend path
        backend_dir = setup_backend_path()
        
        # Change working directory to backend for proper imports
        original_cwd = os.getcwd()
        os.chdir(backend_dir)
        
        # Import the FastAPI app from backend
        from app import app
        
        # Restore original working directory
        os.chdir(original_cwd)
        
        logger.info("✅ Successfully imported FastAPI application from backend/app.py")
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