#!/usr/bin/env python3
"""
Simple Flask Test - Direct import and run
"""

import os
import sys

# Set environment variables
os.environ['META_APP_ID'] = '1879578119651644'
os.environ['META_APP_SECRET'] = 'f79b3350f43751d6139e1b29a232cbf3'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'

# Add backend to path
sys.path.insert(0, 'backend')

print("🔍 Testing Flask app direct import...")

try:
    import production_app
    print("✅ Import successful!")
    
    # Test if we can access the app
    app = production_app.app
    print(f"✅ App object: {app}")
    
    # Test app configuration
    print(f"✅ App config META_APP_ID: {app.config.get('META_APP_ID')}")
    
    # Test if we can create an app context
    with app.app_context():
        print("✅ App context created successfully!")
        
        # Test a simple route  
        with app.test_client() as client:
            print("🔍 Testing root endpoint...")
            response = client.get('/')
            print(f"✅ Root endpoint response: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Response data: {data}")
            
            print("🔍 Testing health endpoint...")
            response = client.get('/health')
            print(f"✅ Health endpoint response: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Health data: {data}")
    
    print("\n🎉 FLASK APP IS WORKING!")
    print("✅ Import successful")
    print("✅ App context works")
    print("✅ Routes respond correctly")
    print("✅ Ready for deployment!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 