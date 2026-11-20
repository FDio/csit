#!/bin/bash

# Setup script for the CLI application
# Creates virtual environment and runs the app

echo "Setting up virtual environment..."

# Create virtual environment if it doesn't exist or is broken
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
    rm -rf .venv
    if python3 -m venv .venv; then
        echo "Virtual environment created."
    else
        echo "Virtual environment creation failed. Running without virtual environment."
        USE_VENV=false
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment if available
if [ "$USE_VENV" != "false" ] && [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated."
else
    echo "Running without virtual environment."
fi

pip install openpyxl

# Run the application
echo "Running the application..."
python compare_releases.py 2606.xlsx 2610.xlsx

echo "Application finished."