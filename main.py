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
        logger.info(f"🔍 Directory contents: {list(current_dir.iterdir())}")
        
        # Check if backend directory exists
        backend_dir = current_dir / "backend"
        logger.info(f"🔍 Backend directory path: {backend_dir}")
        logger.info(f"🔍 Backend directory exists: {backend_dir.exists()}")
        
        if backend_dir.exists():
            logger.info(f"🔍 Backend directory contents: {list(backend_dir.iterdir())}")
            
            # Add backend directory to Python path
            sys.path.insert(0, str(backend_dir))
            os.environ['PYTHONPATH'] = f"{current_dir}:{backend_dir}:{os.environ.get('PYTHONPATH', '')}"
            
            # Change to backend directory for imports
            os.chdir(backend_dir)
            logger.info(f"✅ Changed to backend directory: {os.getcwd()}")
            
            # Import the FastAPI application
            from app import app
            logger.info("✅ Successfully imported FastAPI application from backend/app.py")
            
        else:
            # Backend directory doesn't exist, try direct import
            logger.warning("⚠️ Backend directory not found, trying direct import...")
            
            # Check if app.py exists in current directory
            app_py = current_dir / "app.py"
            if app_py.exists():
                logger.info("✅ Found app.py in current directory")
                from app import app
            else:
                # Try to find app.py in subdirectories
                logger.info("🔍 Searching for app.py in subdirectories...")
                for item in current_dir.rglob("app.py"):
                    if "backend" in str(item) or item.name == "app.py":
                        logger.info(f"✅ Found app.py at: {item}")
                        app_dir = item.parent
                        sys.path.insert(0, str(app_dir))
                        os.chdir(app_dir)
                        from app import app
                        break
                else:
                    raise FileNotFoundError("Could not find app.py in any location")
        
        logger.info("✅ Successfully imported FastAPI application")
        logger.info(f"✅ App title: {app.title}")
        logger.info(f"✅ Routes configured: {len(app.routes)}")
        return app
        
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