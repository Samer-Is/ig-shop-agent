#!/usr/bin/env python3
"""
IG-Shop-Agent - Main Entry Point for Azure Web Apps
This is the main entry point that Azure Web Apps will execute.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory and backend directory to Python path
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"

# Add both paths to ensure proper imports
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(backend_dir))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = f"{current_dir}:{backend_dir}:{os.environ.get('PYTHONPATH', '')}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the FastAPI application."""
    try:
        # Change to backend directory to ensure relative imports work
        os.chdir(backend_dir)
        
        # Import the FastAPI application
        from app import app
        logger.info("✅ Successfully imported FastAPI application")
        logger.info(f"✅ App title: {app.title}")
        logger.info(f"✅ Routes configured: {len(app.routes)}")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to import FastAPI application: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        # Try alternative import method
        try:
            logger.info("🔄 Trying alternative import method...")
            import backend.app
            app = backend.app.app
            logger.info("✅ Successfully imported using alternative method")
            return app
        except Exception as e2:
            logger.error(f"❌ Alternative import also failed: {e2}")
            raise e

# Create the app instance
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