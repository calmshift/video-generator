#!/bin/bash

# Packaging script for AI Video Creator
# This script creates distribution packages for the AI Video Creator

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
print_message "blue" "AI Video Creator - Packaging Script"
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

# Check if build and twine are installed
if ! python3 -c "import build, twine" &> /dev/null; then
    print_message "yellow" "Installing build and twine..."
    pip install build twine
    print_message "green" "✓ Build and twine installed"
fi

# Clean up previous builds
print_message "yellow" "Cleaning up previous builds..."
rm -rf dist/ build/ *.egg-info/
print_message "green" "✓ Previous builds cleaned up"

# Create source distribution and wheel
print_message "yellow" "Creating distribution packages..."
python -m build
print_message "green" "✓ Distribution packages created"

# Check the packages
print_message "yellow" "Checking packages..."
twine check dist/*
print_message "green" "✓ Packages checked"

# List created packages
print_message "blue" "Created packages:"
ls -l dist/

# Instructions for publishing
print_message "yellow" "To publish to PyPI, run:"
print_message "yellow" "twine upload dist/*"

print_message "blue" "=================================================="
print_message "blue" "Packaging completed successfully!"
print_message "blue" "=================================================="