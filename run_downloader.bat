@echo off
echo Starting Simple YouTube Downloader...
python simple_yt_downloader.py
if %ERRORLEVEL% neq 0 (
    echo An error occurred while running the application.
    echo Please ensure you have Python installed (version 3.6 or higher).
    echo You can download Python from https://www.python.org/downloads/
    pause
) 