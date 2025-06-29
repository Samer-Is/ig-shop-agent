#!/usr/bin/env python3
"""
COMPREHENSIVE AZURE FIX - Convert Function App to Web App
The root issue: Azure resource is a Function App, not a Web App!
"""

import subprocess
import requests
import time
import json

RESOURCE_GROUP = "igshop-dev-rg-v2"
CURRENT_APP_NAME = "igshop-dev-yjhtoi-api"
NEW_WEBAPP_NAME = "igshop-webapp-api"
BACKEND_URL_NEW = f"https://{NEW_WEBAPP_NAME}.azurewebsites.net"

def run_cmd(cmd, description, critical=True):
    """Run command with detailed logging"""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("   ✅ Success")
            return True, result.stdout
        else:
            print("   ❌ Failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:300]}...")
            return False, result.stderr
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False, str(e)

def check_url(url, description=""):
    """Check if URL is accessible"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            content = response.text
            if "IG-Shop-Agent" in content:
                print(f"✅ {description}: Flask app is working!")
                return True
            elif "Azure Function" in content:
                print(f"❌ {description}: Still showing Function App page")
                return False
            else:
                print(f"⚠️ {description}: Unknown response (Status 200)")
                return False
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Exception - {str(e)}")
        return False

def main():
    print("🚀 COMPREHENSIVE AZURE FIX - FUNCTION APP TO WEB APP")
    print("=" * 70)
    
    # OPTION 1: Try to convert existing Function App to Web App
    print("\n🔄 OPTION 1: ATTEMPTING TO CONVERT FUNCTION APP TO WEB APP")
    
    # Remove Function App specific settings
    print("\n🧹 STEP 1: REMOVING FUNCTION APP SETTINGS")
    function_settings_to_remove = [
        "FUNCTIONS_WORKER_RUNTIME",
        "FUNCTIONS_EXTENSION_VERSION", 
        "AzureWebJobsStorage",
        "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING",
        "WEBSITE_CONTENTSHARE"
    ]
    
    for setting in function_settings_to_remove:
        run_cmd(f'az webapp config appsettings delete --name {CURRENT_APP_NAME} --resource-group {RESOURCE_GROUP} --setting-names {setting}', 
                f"Removing {setting}", critical=False)
    
    # Set Web App configuration
    print("\n⚙️ STEP 2: CONFIGURING AS WEB APP")
    
    # Fix the Python runtime command (escape quotes properly for PowerShell)
    run_cmd(f'az webapp config set --name {CURRENT_APP_NAME} --resource-group {RESOURCE_GROUP} --linux-fx-version "PYTHON|3.11"', 
            "Setting Python 3.11 runtime")
    
    # Set startup command  
    run_cmd(f'az webapp config set --name {CURRENT_APP_NAME} --resource-group {RESOURCE_GROUP} --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 production_app:app"', 
            "Setting Flask startup command")
    
    # Set environment variables for Flask
    print("\n🔧 STEP 3: SETTING FLASK ENVIRONMENT VARIABLES")
    env_vars = {
        'META_APP_ID': '1879578119651644',
        'META_APP_SECRET': 'f79b3350f43751d6139e1b29a232cbf3',
        'OPENAI_API_KEY': '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',
        'JWT_SECRET_KEY': 'super-secret-jwt-key-for-production',
        'META_REDIRECT_URI': f'https://{CURRENT_APP_NAME}.azurewebsites.net/auth/instagram/callback',
        'FLASK_ENV': 'production',
        'SCM_DO_BUILD_DURING_DEPLOYMENT': 'true'
    }
    
    for key, value in env_vars.items():
        run_cmd(f'az webapp config appsettings set --name {CURRENT_APP_NAME} --resource-group {RESOURCE_GROUP} --settings {key}="{value}"', 
                f"Setting {key}")
    
    # Setup GitHub deployment
    print("\n📥 STEP 4: CONFIGURING GITHUB DEPLOYMENT")
    
    # First, let's see what GitHub repo is configured
    success, output = run_cmd(f'az webapp deployment source show --name {CURRENT_APP_NAME} --resource-group {RESOURCE_GROUP}', 
                             "Checking current deployment source", critical=False)
    
    if success and output:
        print("   Current deployment configuration:")
        try:
            config = json.loads(output)
            if config and config.get('repoUrl'):
                print(f"   Repository: {config.get('repoUrl')}")
                print(f"   Branch: {config.get('branch', 'N/A')}")
            else:
                print("   No GitHub repository configured")
        except:
            print("   Could not parse deployment configuration")
    
    # Configure GitHub deployment (you'll need to replace with your actual repo)
    github_repo = "https://github.com/yourusername/ig-shop-agent"  # UPDATE THIS!
    print(f"\n⚠️  IMPORTANT: Update GitHub repository URL to your actual repo!")
    print(f"   Current placeholder: {github_repo}")
    
    # Restart the app
    print("\n🔄 STEP 5: RESTARTING APPLICATION")
    run_cmd(f"az webapp restart --name {CURRENT_APP_NAME} --resource-group {RESOURCE_GROUP}", 
            "Restarting web app")
    
    # Test the conversion
    print("\n🧪 STEP 6: TESTING CONVERSION")
    time.sleep(30)  # Wait for restart
    
    backend_url = f"https://{CURRENT_APP_NAME}.azurewebsites.net"
    if check_url(backend_url, "Testing converted Function App"):
        print("✅ SUCCESS: Function App successfully converted to Web App!")
        return True
    
    # OPTION 2: Create a new Web App
    print("\n🔄 OPTION 2: CREATING NEW WEB APP (Conversion failed)")
    
    print(f"\n🆕 STEP 7: CREATING NEW WEB APP: {NEW_WEBAPP_NAME}")
    
    # Create App Service Plan
    run_cmd(f'az appservice plan create --name {NEW_WEBAPP_NAME}-plan --resource-group {RESOURCE_GROUP} --sku B1 --is-linux', 
            "Creating App Service Plan")
    
    # Create Web App
    run_cmd(f'az webapp create --name {NEW_WEBAPP_NAME} --resource-group {RESOURCE_GROUP} --plan {NEW_WEBAPP_NAME}-plan --runtime "PYTHON|3.11"', 
            "Creating Web App")
    
    # Configure the new Web App
    run_cmd(f'az webapp config set --name {NEW_WEBAPP_NAME} --resource-group {RESOURCE_GROUP} --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 production_app:app"', 
            "Setting startup command for new Web App")
    
    # Set environment variables for new Web App
    print("\n🔧 STEP 8: CONFIGURING NEW WEB APP")
    env_vars['META_REDIRECT_URI'] = f'{BACKEND_URL_NEW}/auth/instagram/callback'
    
    for key, value in env_vars.items():
        run_cmd(f'az webapp config appsettings set --name {NEW_WEBAPP_NAME} --resource-group {RESOURCE_GROUP} --settings {key}="{value}"', 
                f"Setting {key} for new Web App")
    
    # Test new Web App
    print("\n🧪 STEP 9: TESTING NEW WEB APP")
    time.sleep(30)  # Wait for startup
    
    if check_url(BACKEND_URL_NEW, "Testing new Web App"):
        print("✅ SUCCESS: New Web App created and working!")
        print(f"\n🎉 NEW BACKEND URL: {BACKEND_URL_NEW}")
        print("   Update your frontend to use this new URL!")
        return True
    
    print("\n❌ Both options failed. Manual intervention required.")
    print("\nDEBUGGING STEPS:")
    print("1. Check Azure Portal for deployment logs")
    print("2. Verify GitHub repository integration")
    print("3. Check application logs for Python errors")
    print("4. Ensure all files are committed to GitHub")
    
    return False

if __name__ == "__main__":
    main() 