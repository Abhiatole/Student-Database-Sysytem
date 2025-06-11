@echo off
echo Starting Student Database Management System...
echo.
echo Please wait while the application loads...
echo.

:: Change to the directory containing the executable
cd /d "%~dp0"

:: Run the executable
"Student Database Management System.exe"

:: Check if the application exited with an error
if errorlevel 1 (
    echo.
    echo An error occurred while running the application.
    echo Please check that all required files are present.
    echo.
    pause
)
