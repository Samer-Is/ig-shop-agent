#!/usr/bin/env python3
"""Test script to check if FastAPI app imports correctly"""

import sys
import os
sys.path.append('.')

try:
    from app import app
    print('✅ FastAPI app imported successfully')
    print(f'App type: {type(app)}')
    print(f'App routes: {len(app.routes)} routes')
    
    # List all routes
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f'  {route.methods} {route.path}')
    
    print('\n✅ All imports successful!')
    
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1) 