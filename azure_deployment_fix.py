#!/usr/bin/env python3
"""
PHASE 2: Azure Deployment Debugging and Fix
The Flask app works locally, now we need to fix Azure deployment
"""

import subprocess
import requests
import time
import json
import os

BACKEND_URL = "https://igshop-dev-yjhtoi-api.azurewebsites.net"
RESOURCE_GROUP = "igshop-dev-rg-v2"
APP_NAME = "igshop-dev-yjhtoi-api"

def run_cmd(cmd, description):
    """Run Azure CLI command with detailed output"""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            print("   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return True, result.stdout
        else:
            print(f"   ❌ Failed: {result.stderr.strip()}")
            return False, result.stderr
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, str(e)

def check_azure_logs():
    """Get Azure Web App logs to see what's happening"""
    print("\n🔍 CHECKING AZURE DEPLOYMENT LOGS")
    print("="*50)
    
    # Get recent logs
    success, output = run_cmd(
        f'az webapp log tail --resource-group {RESOURCE_GROUP} --name {APP_NAME} --provider application',
        "Getting application logs"
    )
    
    if success:
        print("📋 Recent logs:")
        print(output[-1000:])  # Last 1000 chars
    
    # Get deployment status
    success, output = run_cmd(
        f'az webapp deployment list --resource-group {RESOURCE_GROUP} --name {APP_NAME}',
        "Getting deployment history"
    )
    
    return success

def force_flask_deployment():
    """Force correct Flask configuration"""
    print("\n🚀 FORCING FLASK DEPLOYMENT")
    print("="*50)
    
    commands = [
        # 1. Set correct runtime
        (
            f'az webapp config set --resource-group {RESOURCE_GROUP} --name {APP_NAME} --linux-fx-version "PYTHON|3.11"',
            "Setting Python 3.11 runtime"
        ),
        
        # 2. Set startup command
        (
            f'az webapp config set --resource-group {RESOURCE_GROUP} --name {APP_NAME} --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 production_app:app"',
            "Setting gunicorn startup command"
        ),
        
        # 3. Set app settings
        (
            f'az webapp config appsettings set --resource-group {RESOURCE_GROUP} --name {APP_NAME} --settings ' +
            'WEBSITES_PORT=8000 ' +
            'SCM_DO_BUILD_DURING_DEPLOYMENT=true ' +
            'ENABLE_ORYX_BUILD=true ' +
            'WEBSITES_ENABLE_APP_SERVICE_STORAGE=false ' +
            f'META_APP_ID=1879578119651644 ' +
            f'META_APP_SECRET=f79b3350f43751d6139e1b29a232cbf3 ' +
            f'OPENAI_API_KEY="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" ' +
            f'JWT_SECRET_KEY=production-jwt-secret-2024 ' +
            f'META_REDIRECT_URI=https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback',
            "Setting environment variables and build settings"
        ),
        
        # 4. Restart app
        (
            f'az webapp restart --resource-group {RESOURCE_GROUP} --name {APP_NAME}',
            "Restarting web app"
        )
    ]
    
    success_count = 0
    for cmd, desc in commands:
        success, output = run_cmd(cmd, desc)
        if success:
            success_count += 1
        time.sleep(3)
    
    return success_count == len(commands)

def trigger_github_deployment():
    """Trigger a fresh GitHub deployment"""
    print("\n🚀 TRIGGERING FRESH GITHUB DEPLOYMENT")
    print("="*50)
    
    # Get current deployment source
    success, output = run_cmd(
        f'az webapp deployment source show --resource-group {RESOURCE_GROUP} --name {APP_NAME}',
        "Checking deployment source"
    )
    
    if success:
        print("✅ GitHub deployment configured")
        
        # Sync with GitHub
        success, output = run_cmd(
            f'az webapp deployment source sync --resource-group {RESOURCE_GROUP} --name {APP_NAME}',
            "Syncing with GitHub repository"
        )
        
        return success
    else:
        print("❌ GitHub deployment not configured")
        return False

def wait_and_test_deployment():
    """Wait for deployment and test"""
    print("\n⏳ WAITING FOR DEPLOYMENT TO COMPLETE")
    print("="*50)
    
    max_attempts = 15  # 5 minutes
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n📡 Check {attempt}/{max_attempts}")
        
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if "IG-Shop-Agent Production API" in content:
                    print("🎉 FLASK APP IS LIVE!")
                    data = response.json()
                    print(f"   API Response: {data}")
                    
                    # Test health endpoint
                    health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
                    if health_response.status_code == 200:
                        health_data = health_response.json()
                        print(f"   Health Check: {health_data}")
                    
                    return True
                else:
                    print(f"   Still Azure default page: {content[:100]}...")
            else:
                print(f"   HTTP {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   Connection error: {str(e)}")
        
        if attempt < max_attempts:
            print("   ⏳ Waiting 20 seconds...")
            time.sleep(20)
    
    print("❌ Deployment timeout - Flask app not responding")
    return False

def main():
    print("🚀 PHASE 2: AZURE DEPLOYMENT DEBUGGING")
    print("="*60)
    print("Flask app works locally - fixing Azure deployment")
    print("="*60)
    
    # Step 1: Check current status
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if "IG-Shop-Agent Production API" in response.text:
            print("✅ Flask app is already working on Azure!")
            return True
    except:
        pass
    
    print("❌ Flask app not responding on Azure - starting fix...")
    
    # Step 2: Check logs
    check_azure_logs()
    
    # Step 3: Force configuration
    config_success = force_flask_deployment()
    if not config_success:
        print("❌ Azure configuration failed")
        return False
    
    # Step 4: Trigger deployment
    deploy_success = trigger_github_deployment()
    if deploy_success:
        print("✅ GitHub deployment triggered")
    else:
        print("⚠️  GitHub deployment issue - continuing...")
    
    # Step 5: Wait and test
    final_success = wait_and_test_deployment()
    
    if final_success:
        print("\n🎉 PHASE 2 COMPLETE!")
        print("✅ Azure deployment fixed")
        print("✅ Flask app responding")
        print("✅ Ready for comprehensive testing")
        print(f"\n🔗 Backend URL: {BACKEND_URL}")
        return True
    else:
        print("\n❌ PHASE 2 FAILED!")
        print("🔧 Azure deployment still not working")
        print("📋 Check Azure portal for detailed logs")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 