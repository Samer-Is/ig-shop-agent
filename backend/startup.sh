#!/bin/bash
echo "Starting IG-Shop-Agent Flask Application..."
python -m gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 production_app:app
