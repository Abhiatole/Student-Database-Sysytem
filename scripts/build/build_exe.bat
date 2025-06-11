
@echo off
echo ============================================================
echo Student Database Management System - Build Script
echo ============================================================

:: Set the project root directory
set PROJECT_ROOT=%~dp0..\..
cd /d "%PROJECT_ROOT%"

echo Current directory: %CD%

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Install dependencies
echo.
echo Installing dependencies...
python -m pip install -r config\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

:: Clean previous builds
echo.
echo Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build the executable
echo.
echo Building executable...
python -m PyInstaller --clean config\main.spec
if errorlevel 1 (
    echo Error: Failed to build executable
    pause
    exit /b 1
)

:: Check if executable was created
if not exist "dist\Student Database Management System.exe" (
    echo Error: Executable was not created
    pause
    exit /b 1
)

:: Create README for distribution
echo.
echo Creating distribution package...
echo Student Database Management System > "dist\README.txt"
echo =================================== >> "dist\README.txt"
echo. >> "dist\README.txt"
echo Installation Instructions: >> "dist\README.txt"
echo 1. Double-click 'Student Database Management System.exe' to run >> "dist\README.txt"
echo 2. The application will create a database automatically on first run >> "dist\README.txt"  
echo 3. Use the default login credentials: >> "dist\README.txt"
echo    Username: admin >> "dist\README.txt"
echo    Password: admin >> "dist\README.txt"
echo. >> "dist\README.txt"
echo Features: >> "dist\README.txt"
echo - Student record management >> "dist\README.txt"
echo - ID card generation with photos >> "dist\README.txt"
echo - Data export functionality >> "dist\README.txt"
echo - Search and filter capabilities >> "dist\README.txt"

echo.
echo ============================================================
echo BUILD SUCCESSFUL!
echo ============================================================
echo Executable location: %CD%\dist\Student Database Management System.exe
echo The application is ready for distribution.
echo ============================================================

pause
