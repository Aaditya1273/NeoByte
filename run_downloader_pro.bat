@echo off
echo.
echo  ===============================================
echo   ^|                                             ^|
echo   ^|       YouTube Downloader Pro Launcher       ^|
echo   ^|       ============================         ^|
echo   ^|                                             ^|
echo   ^|       A modern, futuristic UI design        ^|
echo   ^|       with enhanced visuals                 ^|
echo   ^|                                             ^|
echo  ===============================================
echo.
echo  Starting application...
echo.

python youtube_downloader_qt.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo  ERROR: An issue occurred while running the application.
    echo.
    echo  This application requires:
    echo   - Python 3.6 or higher
    echo   - PyQt5 and pytube libraries (auto-installed if missing)
    echo.
    echo  If this is your first time running the application,
    echo  please make sure you have an internet connection.
    echo.
    pause
) 