#!/usr/bin/env python3
"""
IG-Shop-Agent - Main Entry Point for Azure Web Apps
This is the main entry point that Azure Web Apps will execute.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the FastAPI application."""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent
        logger.info(f"🔍 Current directory: {current_dir}")
        
        # Try to import from root-level app.py first
        try:
            from app import app
            logger.info("✅ Successfully imported FastAPI application from root app.py")
            return app
        except ImportError as e:
            logger.warning(f"Could not import from root app.py: {e}")
            
            # Fallback: try backend directory
            backend_dir = current_dir / "backend"
            if backend_dir.exists():
                logger.info(f"🔍 Trying backend directory: {backend_dir}")
                sys.path.insert(0, str(backend_dir))
                os.chdir(backend_dir)
                
                from app import app
                logger.info("✅ Successfully imported FastAPI application from backend/app.py")
                return app
            else:
                raise ImportError("Could not find app.py in root or backend directory")
        
    except Exception as e:
        logger.error(f"❌ Failed to import FastAPI application: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise

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