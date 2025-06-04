@echo off
setlocal enabledelayedexpansion

:: Run script for AI Video Creator
:: This script helps set up and run the AI Video Creator on Windows

:: Function to print colored messages
call :print_message blue "=================================================="
call :print_message blue "AI Video Creator - Setup and Run Script (Windows)"
call :print_message blue "=================================================="

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_message red "Python is required but not installed. Please install Python and try again."
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set "python_version=%%I"
set "required_version=3.8"

:: Simple version check (not perfect but works for most cases)
set "python_major_minor=!python_version:~0,3!"
if "!python_major_minor!" LSS "!required_version!" (
    call :print_message red "Python !required_version! or higher is required. You have Python !python_version!."
    exit /b 1
)

call :print_message green "✓ Python !python_version! detected"

:: Check if virtual environment exists, create if not
if not exist "venv\" (
    call :print_message yellow "Creating virtual environment..."
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        call :print_message red "Failed to create virtual environment. Please install venv package and try again."
        exit /b 1
    )
    call :print_message green "✓ Virtual environment created"
) else (
    call :print_message green "✓ Virtual environment exists"
)

:: Activate virtual environment
call :print_message yellow "Activating virtual environment..."
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    call :print_message red "Failed to activate virtual environment."
    exit /b 1
)
call :print_message green "✓ Virtual environment activated"

:: Install dependencies
call :print_message yellow "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    call :print_message red "Failed to install dependencies."
    exit /b 1
)
call :print_message green "✓ Dependencies installed"

:: Check if .env file exists, create from example if not
if not exist ".env" (
    if exist ".env.example" (
        call :print_message yellow "Creating .env file from example..."
        copy .env.example .env
        call :print_message yellow "Please edit the .env file to add your API keys."
        call :print_message yellow "You can do this by opening .env in a text editor."
        
        :: Ask if user wants to edit the file now
        set /p answer="Would you like to edit the .env file now? (y/n): "
        if /i "!answer!"=="y" (
            notepad .env
        )
    ) else (
        call :print_message yellow "No .env.example file found. You may need to set environment variables manually."
    )
) else (
    call :print_message green "✓ .env file exists"
)

:: Create necessary directories
if not exist "videos\" mkdir videos
if not exist "output\" mkdir output
call :print_message green "✓ Directories created/verified"

:: Check if videos directory has files
dir /b "videos\*.mp4" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_message yellow "Warning: No video files found in the videos directory."
    call :print_message yellow "Please add some .mp4 video files to the videos directory."
    
    :: Ask if user wants to continue
    set /p answer="Continue anyway? (y/n): "
    if /i not "!answer!"=="y" (
        call :print_message red "Exiting. Please add video files and run again."
        exit /b 1
    )
) else (
    call :print_message green "✓ Video files found"
)

:: Parse command line arguments
set "ARGS="
if not "%~1"=="" (
    set "ARGS=%*"
    call :print_message yellow "Running with arguments: !ARGS!"
)

:: Run the main script
call :print_message blue "Running AI Video Creator..."
python ai_video_creator.py %ARGS%

:: Check exit status
if %ERRORLEVEL% equ 0 (
    call :print_message green "✓ AI Video Creator completed successfully"
) else (
    call :print_message red "AI Video Creator exited with an error"
    call :print_message yellow "Check the log file for details: ai_video_creator.log"
)

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat
call :print_message green "✓ Virtual environment deactivated"

call :print_message blue "=================================================="
call :print_message blue "Done!"
call :print_message blue "=================================================="

exit /b 0

:: Function to print colored messages
:print_message
setlocal
set "color=%~1"
set "message=%~2"

if "%color%"=="green" (
    echo [92m%message%[0m
) else if "%color%"=="yellow" (
    echo [93m%message%[0m
) else if "%color%"=="red" (
    echo [91m%message%[0m
) else if "%color%"=="blue" (
    echo [94m%message%[0m
) else (
    echo %message%
)

endlocal
exit /b 0