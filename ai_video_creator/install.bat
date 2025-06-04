@echo off
setlocal enabledelayedexpansion

:: Installation script for AI Video Creator
:: This script installs the AI Video Creator and its dependencies on Windows

:: Function to print colored messages
call :print_message blue "=================================================="
call :print_message blue "AI Video Creator - Installation Script (Windows)"
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

:: Check for FFmpeg (required by moviepy)
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_message yellow "FFmpeg is required but not installed."
    call :print_message yellow "Please download and install FFmpeg from https://ffmpeg.org/download.html"
    call :print_message yellow "Make sure to add FFmpeg to your PATH environment variable."
    
    set /p answer="Continue without FFmpeg? (y/n): "
    if /i not "!answer!"=="y" (
        call :print_message red "Exiting. Please install FFmpeg and try again."
        exit /b 1
    )
    
    call :print_message yellow "Continuing without FFmpeg. Some features may not work properly."
) else (
    call :print_message green "✓ FFmpeg detected"
)

:: Create installation directory
set "install_dir=%USERPROFILE%\.ai_video_creator"
if exist "!install_dir!" (
    call :print_message yellow "Installation directory already exists: !install_dir!"
    set /p answer="Would you like to remove it and reinstall? (y/n): "
    if /i "!answer!"=="y" (
        call :print_message yellow "Removing existing installation..."
        rmdir /s /q "!install_dir!"
    ) else (
        call :print_message yellow "Updating existing installation..."
    )
)

:: Create installation directory if it doesn't exist
if not exist "!install_dir!" mkdir "!install_dir!"
call :print_message green "✓ Installation directory created: !install_dir!"

:: Copy files to installation directory
call :print_message yellow "Copying files to installation directory..."
xcopy /s /e /y "." "!install_dir!\" >nul
call :print_message green "✓ Files copied to installation directory"

:: Create virtual environment
call :print_message yellow "Creating virtual environment..."
cd "!install_dir!"
python -m venv venv
call venv\Scripts\activate.bat
call :print_message green "✓ Virtual environment created and activated"

:: Install dependencies
call :print_message yellow "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
call :print_message green "✓ Dependencies installed"

:: Create bin directory for executable
set "bin_dir=%USERPROFILE%\AppData\Local\Programs\AI-Video-Creator"
if not exist "!bin_dir!" mkdir "!bin_dir!"

:: Create wrapper batch file
set "wrapper_script=!bin_dir!\ai-video-creator.bat"
(
    echo @echo off
    echo :: Wrapper script for AI Video Creator
    echo.
    echo :: Change to installation directory and run the script
    echo cd /d "%install_dir%"
    echo call venv\Scripts\activate.bat
    echo python ai_video_creator.py %%*
    echo.
    echo :: Don't close the window immediately if there's an error
    echo if %%ERRORLEVEL%% neq 0 pause
) > "!wrapper_script!"

call :print_message green "✓ Executable wrapper created: !wrapper_script!"

:: Add bin_dir to PATH if not already there
call :check_path "!bin_dir!"
if %ERRORLEVEL% neq 0 (
    call :print_message yellow "Adding !bin_dir! to PATH..."
    
    :: Add to PATH using setx (permanent)
    setx PATH "%%PATH%%;!bin_dir!"
    
    call :print_message green "✓ Added !bin_dir! to PATH"
    call :print_message yellow "Please restart your command prompt to use the 'ai-video-creator' command."
)

:: Create .env file if it doesn't exist
if not exist "!install_dir!\.env" (
    if exist "!install_dir!\.env.example" (
        call :print_message yellow "Creating .env file from example..."
        copy "!install_dir!\.env.example" "!install_dir!\.env" >nul
        call :print_message yellow "Please edit !install_dir!\.env to add your API keys."
    )
)

:: Create videos directory if it doesn't exist
if not exist "!install_dir!\videos" mkdir "!install_dir!\videos"
call :print_message green "✓ Videos directory created: !install_dir!\videos"

:: Create output directory if it doesn't exist
if not exist "!install_dir!\output" mkdir "!install_dir!\output"
call :print_message green "✓ Output directory created: !install_dir!\output"

:: Create desktop shortcut
call :print_message yellow "Creating desktop shortcut..."
set "desktop=%USERPROFILE%\Desktop"
set "shortcut=!desktop!\AI Video Creator.lnk"

:: Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!shortcut!'); $Shortcut.TargetPath = '!wrapper_script!'; $Shortcut.Save()"

call :print_message green "✓ Desktop shortcut created: !shortcut!"

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

call :print_message blue "=================================================="
call :print_message green "AI Video Creator has been installed successfully!"
call :print_message blue "=================================================="
call :print_message yellow "To use AI Video Creator, run: ai-video-creator"
call :print_message yellow "Or use the desktop shortcut: AI Video Creator"
call :print_message yellow "Add your API keys to: !install_dir!\.env"
call :print_message yellow "Add background videos to: !install_dir!\videos"
call :print_message yellow "Output videos will be saved to: !install_dir!\output"
call :print_message blue "=================================================="

exit /b 0

:: Function to check if a directory is in PATH
:check_path
setlocal
set "check_dir=%~1"
echo %PATH% | findstr /C:"%check_dir%" >nul
if %ERRORLEVEL% equ 0 (
    endlocal
    exit /b 0
) else (
    endlocal
    exit /b 1
)

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