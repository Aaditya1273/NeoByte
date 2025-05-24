@echo off
echo ========================================
echo      NeoByte Downloader Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Press any key to exit...
    pause > nul
    exit /b
)

REM Install dependencies if needed
echo [INFO] Checking dependencies...
pip install -r requirements.txt

REM Start the application
echo.
echo [INFO] Starting NeoByte Downloader...
echo [INFO] Web interface will open in your browser.
echo [INFO] Press Ctrl+C to stop the server when finished.
echo.
start http://localhost:5000
python app.py

pause 