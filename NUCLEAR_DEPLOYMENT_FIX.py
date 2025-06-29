#!/usr/bin/env python3
"""
NUCLEAR OPTION: COMPLETE AZURE DEPLOYMENT FIX
Fix EVERY possible Azure deployment issue in one comprehensive script
"""

import subprocess
import requests
import time
import json
import os
from pathlib import Path

BACKEND_URL = "https://igshop-dev-yjhtoi-api.azurewebsites.net"
RESOURCE_GROUP = "igshop-dev-rg-v2"
APP_NAME = "igshop-dev-yjhtoi-api"

def run_cmd(cmd, description, critical=True):
    """Run command with detailed logging"""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("   ✅ Success")
            if result.stdout.strip():
                output = result.stdout.strip()
                print(f"   Output: {output[:500]}...")
            return True, result.stdout
        else:
            print("   ❌ Failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:500]}...")
            if critical:
                print(f"   🚨 CRITICAL FAILURE: {description}")
            return False, result.stderr
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False, str(e)

def check_url(url, expected_text="", description=""):
    """Check if URL returns expected content"""
    try:
        response = requests.get(url, timeout=30)
        content = response.text
        
        if response.status_code == 200:
            if expected_text and expected_text in content:
                print(f"✅ {description}: Found expected content")
                return True
            elif not expected_text:
                print(f"✅ {description}: URL accessible (Status 200)")
                return True
            else:
                print(f"❌ {description}: URL accessible but missing expected content")
                print(f"   Expected: '{expected_text}'")
                print(f"   Got: {content[:200]}...")
                return False
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Exception - {str(e)}")
        return False

def main():
    print("🚀 NUCLEAR DEPLOYMENT FIX - ADDRESSING ALL POSSIBLE ISSUES")
    print("=" * 60)
    
    # STEP 1: Create a proper requirements.txt
    print("\n📦 STEP 1: CREATING COMPREHENSIVE REQUIREMENTS.TXT")
    requirements = """
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
requests==2.31.0
openai==1.3.8
PyJWT==2.8.0
Werkzeug==2.3.7
psycopg2-binary==2.9.7
gunicorn==21.2.0
python-dotenv==1.0.0
""".strip()
    
    os.chdir('backend')
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✅ Created comprehensive requirements.txt")
    
    # STEP 2: Create a proper startup script
    print("\n🚀 STEP 2: CREATING STARTUP SCRIPT")
    startup_script = '''#!/bin/bash
echo "Starting IG-Shop-Agent Flask Application..."
python -m gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 production_app:app
'''
    with open('startup.sh', 'w') as f:
        f.write(startup_script)
    print("✅ Created startup.sh")
    
    # STEP 3: Create web.config for Azure
    print("\n⚙️ STEP 3: CREATING WEB.CONFIG")
    web_config = '''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" 
                  arguments="-m gunicorn --bind=0.0.0.0:%HTTP_PLATFORM_PORT% --timeout 600 production_app:app"
                  stdoutLogEnabled="true"
                  stdoutLogFile="\\home\\LogFiles\\python.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="D:\\home\\site\\wwwroot" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>'''
    with open('web.config', 'w') as f:
        f.write(web_config)
    print("✅ Created web.config")
    
    os.chdir('..')
    
    # STEP 4: Azure CLI Login Check
    print("\n🔐 STEP 4: CHECKING AZURE CLI LOGIN")
    success, _ = run_cmd("az account show", "Checking Azure CLI login")
    if not success:
        print("❌ Not logged into Azure CLI!")
        print("Please run: az login")
        return False
    
    # STEP 5: Stop the web app
    print("\n⏹️ STEP 5: STOPPING WEB APP")
    run_cmd(f"az webapp stop --name {APP_NAME} --resource-group {RESOURCE_GROUP}", 
            "Stopping web app", critical=False)
    
    # STEP 6: Configure Python runtime
    print("\n🐍 STEP 6: CONFIGURING PYTHON RUNTIME")
    run_cmd(f"az webapp config set --name {APP_NAME} --resource-group {RESOURCE_GROUP} --linux-fx-version 'PYTHON|3.11'", 
            "Setting Python 3.11 runtime")
    
    # STEP 7: Set startup command
    print("\n🚀 STEP 7: SETTING STARTUP COMMAND")
    startup_cmd = "gunicorn --bind=0.0.0.0 --timeout 600 production_app:app"
    run_cmd(f'az webapp config set --name {APP_NAME} --resource-group {RESOURCE_GROUP} --startup-file "{startup_cmd}"', 
            "Setting startup command")
    
    # STEP 8: Configure environment variables
    print("\n🔧 STEP 8: SETTING ENVIRONMENT VARIABLES")
    env_vars = {
        'META_APP_ID': '1879578119651644',
        'META_APP_SECRET': 'f79b3350f43751d6139e1b29a232cbf3',
        'OPENAI_API_KEY': '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',
        'JWT_SECRET_KEY': 'super-secret-jwt-key-for-production',
        'META_REDIRECT_URI': f'{BACKEND_URL}/auth/instagram/callback',
        'FLASK_ENV': 'production'
    }
    
    env_string = ' '.join([f'{k}="{v}"' for k, v in env_vars.items()])
    run_cmd(f'az webapp config appsettings set --name {APP_NAME} --resource-group {RESOURCE_GROUP} --settings {env_string}', 
            "Setting environment variables")
    
    # STEP 9: Deploy from GitHub (force sync)
    print("\n📥 STEP 9: FORCING GITHUB DEPLOYMENT")
    run_cmd(f"az webapp deployment source sync --name {APP_NAME} --resource-group {RESOURCE_GROUP}", 
            "Syncing from GitHub repository")
    
    # STEP 10: Start the web app
    print("\n▶️ STEP 10: STARTING WEB APP")
    run_cmd(f"az webapp start --name {APP_NAME} --resource-group {RESOURCE_GROUP}", 
            "Starting web app")
    
    # STEP 11: Wait for deployment
    print("\n⏳ STEP 11: WAITING FOR DEPLOYMENT")
    for i in range(12):  # 2 minutes total
        print(f"   Waiting... {i+1}/12 (10 seconds each)")
        time.sleep(10)
        
        if check_url(BACKEND_URL, "IG-Shop-Agent", f"Check #{i+1}"):
            print("✅ DEPLOYMENT SUCCESSFUL!")
            break
    else:
        print("❌ Deployment timeout - checking logs...")
        
        # Get deployment logs
        print("\n📋 CHECKING DEPLOYMENT LOGS")
        run_cmd(f"az webapp log tail --name {APP_NAME} --resource-group {RESOURCE_GROUP}", 
                "Getting application logs", critical=False)
    
    # STEP 12: Final comprehensive test
    print("\n🧪 STEP 12: COMPREHENSIVE TESTING")
    
    endpoints_to_test = [
        ("/", "health check"),
        ("/api/status", "API status"),
        ("/api/health", "health endpoint"),
        ("/auth/instagram", "Instagram auth")
    ]
    
    for endpoint, description in endpoints_to_test:
        url = f"{BACKEND_URL}{endpoint}"
        check_url(url, "", f"{description} - {endpoint}")
    
    print("\n" + "=" * 60)
    print("🏁 NUCLEAR DEPLOYMENT FIX COMPLETE")
    print("If the Flask app is still not working, the issue is likely:")
    print("1. GitHub repository sync issues")
    print("2. Azure platform-level problems")
    print("3. Network/DNS issues")
    print("=" * 60)

if __name__ == "__main__":
    main() 