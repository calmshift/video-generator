#!/bin/bash

# Installation script for AI Video Creator
# This script installs the AI Video Creator and its dependencies

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
print_message "blue" "AI Video Creator - Installation Script"
print_message "blue" "=================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_message "yellow" "Running as root. This is not recommended."
    print_message "yellow" "Continue anyway? (y/n)"
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        print_message "red" "Exiting. Please run without sudo."
        exit 1
    fi
fi

# Check for system dependencies
print_message "yellow" "Checking system dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    print_message "red" "Python 3 is required but not installed."
    print_message "yellow" "Would you like to install Python 3? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            print_message "yellow" "Installing Python 3 using apt..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            print_message "yellow" "Installing Python 3 using yum..."
            sudo yum install -y python3 python3-pip
        elif command -v brew &> /dev/null; then
            print_message "yellow" "Installing Python 3 using Homebrew..."
            brew install python
        else
            print_message "red" "Could not determine package manager. Please install Python 3 manually."
            exit 1
        fi
    else
        print_message "red" "Python 3 is required. Exiting."
        exit 1
    fi
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_message "red" "Python $required_version or higher is required. You have Python $python_version."
    exit 1
fi

print_message "green" "✓ Python $python_version detected"

# Check for FFmpeg (required by moviepy)
if ! command -v ffmpeg &> /dev/null; then
    print_message "yellow" "FFmpeg is required but not installed."
    print_message "yellow" "Would you like to install FFmpeg? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            print_message "yellow" "Installing FFmpeg using apt..."
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            print_message "yellow" "Installing FFmpeg using yum..."
            sudo yum install -y ffmpeg
        elif command -v brew &> /dev/null; then
            print_message "yellow" "Installing FFmpeg using Homebrew..."
            brew install ffmpeg
        else
            print_message "red" "Could not determine package manager. Please install FFmpeg manually."
            exit 1
        fi
    else
        print_message "yellow" "FFmpeg is recommended for video processing. Some features may not work without it."
    fi
else
    print_message "green" "✓ FFmpeg detected"
fi

# Create installation directory
install_dir="$HOME/.ai_video_creator"
if [ -d "$install_dir" ]; then
    print_message "yellow" "Installation directory already exists: $install_dir"
    print_message "yellow" "Would you like to remove it and reinstall? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        print_message "yellow" "Removing existing installation..."
        rm -rf "$install_dir"
    else
        print_message "yellow" "Updating existing installation..."
    fi
fi

# Create installation directory if it doesn't exist
mkdir -p "$install_dir"
print_message "green" "✓ Installation directory created: $install_dir"

# Copy files to installation directory
print_message "yellow" "Copying files to installation directory..."
cp -r ./* "$install_dir/"
print_message "green" "✓ Files copied to installation directory"

# Create virtual environment
print_message "yellow" "Creating virtual environment..."
cd "$install_dir"
python3 -m venv venv
source venv/bin/activate
print_message "green" "✓ Virtual environment created and activated"

# Install dependencies
print_message "yellow" "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_message "green" "✓ Dependencies installed"

# Create symbolic link to executable
bin_dir="$HOME/.local/bin"
mkdir -p "$bin_dir"

# Create wrapper script
wrapper_script="$bin_dir/ai-video-creator"
cat > "$wrapper_script" << EOF
#!/bin/bash
# Wrapper script for AI Video Creator

# Activate virtual environment and run the script
cd "$install_dir"
source venv/bin/activate
python ai_video_creator.py "\$@"
EOF

# Make wrapper script executable
chmod +x "$wrapper_script"
print_message "green" "✓ Executable wrapper created: $wrapper_script"

# Check if bin_dir is in PATH
if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
    print_message "yellow" "Adding $bin_dir to PATH in your shell profile..."
    
    # Determine shell profile file
    shell_profile=""
    if [ -n "$BASH_VERSION" ]; then
        if [ -f "$HOME/.bashrc" ]; then
            shell_profile="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            shell_profile="$HOME/.bash_profile"
        fi
    elif [ -n "$ZSH_VERSION" ]; then
        shell_profile="$HOME/.zshrc"
    fi
    
    if [ -n "$shell_profile" ]; then
        echo "export PATH=\"\$PATH:$bin_dir\"" >> "$shell_profile"
        print_message "green" "✓ Added $bin_dir to PATH in $shell_profile"
        print_message "yellow" "Please restart your shell or run 'source $shell_profile' to update your PATH."
    else
        print_message "yellow" "Could not determine shell profile. Please add $bin_dir to your PATH manually."
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f "$install_dir/.env" ] && [ -f "$install_dir/.env.example" ]; then
    print_message "yellow" "Creating .env file from example..."
    cp "$install_dir/.env.example" "$install_dir/.env"
    print_message "yellow" "Please edit $install_dir/.env to add your API keys."
fi

# Create videos directory if it doesn't exist
mkdir -p "$install_dir/videos"
print_message "green" "✓ Videos directory created: $install_dir/videos"

# Create output directory if it doesn't exist
mkdir -p "$install_dir/output"
print_message "green" "✓ Output directory created: $install_dir/output"

# Deactivate virtual environment
deactivate

print_message "blue" "=================================================="
print_message "green" "AI Video Creator has been installed successfully!"
print_message "blue" "=================================================="
print_message "yellow" "To use AI Video Creator, run: ai-video-creator"
print_message "yellow" "If the command is not found, you may need to restart your shell or add $bin_dir to your PATH."
print_message "yellow" "Add your API keys to: $install_dir/.env"
print_message "yellow" "Add background videos to: $install_dir/videos"
print_message "yellow" "Output videos will be saved to: $install_dir/output"
print_message "blue" "=================================================="