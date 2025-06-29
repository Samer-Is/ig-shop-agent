#!/usr/bin/env python3
"""
Simple startup script for IG-Shop-Agent Local Backend
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False
    return True

def run_app():
    """Run the Flask application"""
    print("🚀 Starting IG-Shop-Agent Local Server...")
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")

if __name__ == "__main__":
    print("=" * 50)
    print("🛍️  IG-Shop-Agent Local Development Server")
    print("=" * 50)
    
    if install_requirements():
        run_app()
    else:
        print("Please install requirements manually: pip install -r requirements.txt")
        sys.exit(1) 