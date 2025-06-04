#!/bin/bash

# Run script for AI Video Creator
# This script helps set up and run the AI Video Creator

# Set up error handling
set -e
trap 'echo "Error occurred. Exiting..."; exit 1' ERR

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    
    case $color in
        "green") echo -e "\033[0;32m$message\033[0m" ;;
        "yellow") echo -e "\033[0;33m$message\033[0m" ;;
        "red") echo -e "\033[0;31m$message\033[0m" ;;
        "blue") echo -e "\033[0;34m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# Print banner
print_message "blue" "=================================================="
print_message "blue" "AI Video Creator - Setup and Run Script"
print_message "blue" "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_message "red" "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_message "red" "Python $required_version or higher is required. You have Python $python_version."
    exit 1
fi

print_message "green" "✓ Python $python_version detected"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_message "yellow" "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_message "red" "Failed to create virtual environment. Please install venv package and try again."
        exit 1
    fi
    print_message "green" "✓ Virtual environment created"
else
    print_message "green" "✓ Virtual environment exists"
fi

# Activate virtual environment
print_message "yellow" "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_message "red" "Failed to activate virtual environment."
    exit 1
fi
print_message "green" "✓ Virtual environment activated"

# Install dependencies
print_message "yellow" "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_message "red" "Failed to install dependencies."
    exit 1
fi
print_message "green" "✓ Dependencies installed"

# Check if .env file exists, create from example if not
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    print_message "yellow" "Creating .env file from example..."
    cp .env.example .env
    print_message "yellow" "Please edit the .env file to add your API keys."
    print_message "yellow" "You can do this by running: nano .env"
    
    # Check if any editor is available
    if command -v nano &> /dev/null; then
        print_message "yellow" "Would you like to edit the .env file now? (y/n)"
        read -r answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            nano .env
        fi
    fi
elif [ -f ".env" ]; then
    print_message "green" "✓ .env file exists"
else
    print_message "yellow" "No .env.example file found. You may need to set environment variables manually."
fi

# Create necessary directories
mkdir -p videos output
print_message "green" "✓ Directories created/verified"

# Check if videos directory has files
if [ ! "$(ls -A videos)" ]; then
    print_message "yellow" "Warning: No video files found in the videos directory."
    print_message "yellow" "Please add some .mp4 video files to the videos directory."
    
    # Ask if user wants to continue
    print_message "yellow" "Continue anyway? (y/n)"
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        print_message "red" "Exiting. Please add video files and run again."
        exit 1
    fi
else
    print_message "green" "✓ Video files found"
fi

# Parse command line arguments
ARGS=""
if [ $# -gt 0 ]; then
    ARGS="$@"
    print_message "yellow" "Running with arguments: $ARGS"
fi

# Run the main script
print_message "blue" "Running AI Video Creator..."
python ai_video_creator.py $ARGS

# Check exit status
if [ $? -eq 0 ]; then
    print_message "green" "✓ AI Video Creator completed successfully"
else
    print_message "red" "AI Video Creator exited with an error"
    print_message "yellow" "Check the log file for details: ai_video_creator.log"
fi

# Deactivate virtual environment
deactivate
print_message "green" "✓ Virtual environment deactivated"

print_message "blue" "=================================================="
print_message "blue" "Done!"
print_message "blue" "=================================================="