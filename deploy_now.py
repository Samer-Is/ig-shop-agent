#!/usr/bin/env python3
"""
Azure Web App Deployment Script
Deploy IG-Shop-Agent Flask Backend to Azure
"""

import os
import subprocess
import sys

def run_command(cmd):
    """Run shell command and return result"""
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ Success: {result.stdout}")
    return True

def deploy_to_azure():
    """Deploy Flask app to Azure Web App"""
    
    print("🚀 Starting Azure Web App Deployment...")
    
    # 1. Ensure we're in the backend directory
    if not os.path.exists('app_simple.py'):
        print("❌ Error: app_simple.py not found. Run from backend directory.")
        return False
    
    # 2. Create requirements.txt for production
    print("📦 Creating production requirements...")
    
    # 3. Initialize git repository if needed
    if not os.path.exists('.git'):
        print("🔧 Initializing git repository...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit - IG Shop Agent Flask Backend"')
    
    # 4. Deploy to Azure Web App
    azure_commands = [
        # Set the deployment source to local git
        "az webapp deployment source config-local-git --name igshop-dev-yjhtoi-api --resource-group igshop-dev-rg-v2",
        
        # Get the git URL for deployment  
        "az webapp deployment list-publishing-credentials --name igshop-dev-yjhtoi-api --resource-group igshop-dev-rg-v2"
    ]
    
    print("🌐 Configuring Azure Web App deployment...")
    for cmd in azure_commands:
        if not run_command(cmd):
            print(f"❌ Failed to execute: {cmd}")
            return False
    
    print("✅ Deployment configuration complete!")
    print("\n📋 MANUAL STEPS NEEDED:")
    print("1. Get the Git deployment URL from Azure Portal")  
    print("2. Push code: git remote add azure <DEPLOYMENT_URL>")
    print("3. Deploy: git push azure main")
    print("4. Set environment variables in Azure Portal")
    
    return True

if __name__ == "__main__":
    deploy_to_azure() 