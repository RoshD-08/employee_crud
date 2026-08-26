#!/bin/bash
echo "Starting Employee CRUD System..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
echo "Starting server on port 5001..."
export FLASK_RUN_PORT=5001
python3 app.py
