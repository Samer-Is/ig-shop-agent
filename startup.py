#!/usr/bin/env python3
"""
Startup file for Azure Web Apps
This file is automatically detected by Azure Oryx
"""

import os
import sys
from pathlib import Path

# Add the current directory and backend directory to Python path
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"

# Add both paths to ensure proper imports
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(backend_dir))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = f"{current_dir}:{backend_dir}:{os.environ.get('PYTHONPATH', '')}"

# Change to backend directory for imports
os.chdir(backend_dir)

from app import app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 