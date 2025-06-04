#!/bin/bash

# Run script for AI Video Creator
# This script helps set up and run the AI Video Creator

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, create from example if not
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit the .env file to add your API keys."
    echo "You can do this by running: nano .env"
fi

# Check if videos directory has files
if [ ! "$(ls -A videos)" ]; then
    echo "Warning: No video files found in the videos directory."
    echo "Please add some .mp4 video files to the videos directory."
fi

# Run the main script
echo "Running AI Video Creator..."
python ai_video_creator.py

# Deactivate virtual environment
deactivate

echo "Done!"