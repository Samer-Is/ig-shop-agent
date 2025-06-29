#!/bin/bash
cd /home/site/wwwroot

# Install dependencies
pip install -r requirements.txt

# Start Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 production_app:application
