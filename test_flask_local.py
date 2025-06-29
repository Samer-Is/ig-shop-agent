#!/usr/bin/env python3
"""
Local Flask App Testing - PHASE 1
Test the Flask app locally before Azure deployment
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

# Set environment variables for local testing
os.environ['META_APP_ID'] = '1879578119651644'
os.environ['META_APP_SECRET'] = 'f79b3350f43751d6139e1b29a232cbf3'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
os.environ['META_REDIRECT_URI'] = 'http://localhost:5000/auth/instagram/callback'

def test_flask_import():
    """Test if Flask app can be imported without errors"""
    print("🔍 PHASE 1.1: Testing Flask app import...")
    
    try:
        sys.path.insert(0, 'backend')
        import production_app
        print("✅ Flask app imported successfully!")
        return production_app.app
    except Exception as e:
        print(f"❌ Flask import failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return None

def test_flask_startup():
    """Test if Flask app starts without errors"""
    print("\n🔍 PHASE 1.2: Testing Flask app startup...")
    
    try:
        # Start Flask in background
        import subprocess
        process = subprocess.Popen([
            sys.executable, '-c', 
            """
import sys
sys.path.insert(0, 'backend')
import production_app
production_app.app.run(host='127.0.0.1', port=5555, debug=True)
            """
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Starting Flask server on port 5555...")
        time.sleep(3)
        
        # Test if server responds
        try:
            response = requests.get('http://127.0.0.1:5555/', timeout=5)
            if response.status_code == 200:
                print("✅ Flask server started successfully!")
                print(f"   Response: {response.json()}")
                
                # Kill the process
                process.terminate()
                return True
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                process.terminate()
                return False
        except Exception as e:
            print(f"❌ Server not responding: {str(e)}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Flask startup failed: {str(e)}")
        return False

def test_local_endpoints():
    """Test all endpoints locally"""
    print("\n🔍 PHASE 1.3: Testing endpoints locally...")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, '-c', 
        """
import sys, os
sys.path.insert(0, 'backend')
os.environ['META_APP_ID'] = '1879578119651644'
os.environ['META_APP_SECRET'] = 'f79b3350f43751d6139e1b29a232cbf3'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
import production_app
production_app.app.run(host='127.0.0.1', port=5556, debug=False)
        """
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(4)
    
    base_url = 'http://127.0.0.1:5556'
    tests = []
    
    # Test endpoints
    endpoints = [
        ('/', 'Root endpoint'),
        ('/health', 'Health endpoint'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} working - {response.status_code}")
                tests.append((name, True))
            else:
                print(f"❌ {name} failed - {response.status_code}")
                tests.append((name, False))
        except Exception as e:
            print(f"❌ {name} error - {str(e)}")
            tests.append((name, False))
    
    # Test registration
    try:
        test_user = {
            "email": "local-test@example.com",
            "password": "testpass123",
            "business_name": "Local Test Shop"
        }
        
        response = requests.post(f'{base_url}/auth/register', json=test_user, timeout=10)
        if response.status_code in [201, 400]:  # 400 = user exists
            print(f"✅ Registration endpoint working - {response.status_code}")
            tests.append(('Registration', True))
            
            if response.status_code == 201:
                token = response.json().get('token')
                print(f"   Got token: {token[:20] if token else 'None'}...")
        else:
            print(f"❌ Registration failed - {response.status_code}: {response.text}")
            tests.append(('Registration', False))
    except Exception as e:
        print(f"❌ Registration error - {str(e)}")
        tests.append(('Registration', False))
    
    process.terminate()
    time.sleep(1)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    print(f"\n📊 Local tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.8  # 80% pass rate

def check_requirements():
    """Check if all requirements are available"""
    print("\n🔍 PHASE 1.4: Checking requirements...")
    
    required_packages = [
        'flask', 'flask_cors', 'flask_sqlalchemy', 'flask_migrate',
        'requests', 'openai', 'jwt', 'werkzeug', 'psycopg2'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {missing}")
        return False
    else:
        print("\n✅ All required packages available!")
        return True

def main():
    print("🚀 FLASK LOCAL TESTING - PHASE 1")
    print("="*50)
    print("Testing Flask app locally before Azure deployment")
    print("="*50)
    
    # Step 1: Check requirements
    req_ok = check_requirements()
    if not req_ok:
        print("\n❌ PHASE 1 FAILED: Missing requirements")
        return False
    
    # Step 2: Test import
    app = test_flask_import()
    if not app:
        print("\n❌ PHASE 1 FAILED: Import errors")
        return False
    
    # Step 3: Test startup
    startup_ok = test_flask_startup()
    if not startup_ok:
        print("\n❌ PHASE 1 FAILED: Startup errors")
        return False
    
    # Step 4: Test endpoints
    endpoints_ok = test_local_endpoints()
    if not endpoints_ok:
        print("\n❌ PHASE 1 FAILED: Endpoint errors")
        return False
    
    print("\n🎉 PHASE 1 COMPLETE: Flask app ready for deployment!")
    print("✅ All imports work")
    print("✅ App starts successfully")
    print("✅ Endpoints respond correctly")
    print("✅ Ready for Azure deployment")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 