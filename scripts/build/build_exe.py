#!/usr/bin/env python3
"""
Build Script for Student Database Management System
This script automates the process of creating an executable file
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    project_root = get_project_root()
    requirements_file = project_root / "config" / "requirements.txt"
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False

def clean_build_directories():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    project_root = get_project_root()
    
    directories_to_clean = [
        project_root / "build",
        project_root / "dist",
        project_root / "__pycache__",
    ]
    
    for directory in directories_to_clean:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"✓ Cleaned {directory.name}")
    
    # Clean .pyc files
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def verify_files():
    """Verify that required files exist"""
    print("Verifying required files...")
    project_root = get_project_root()
    
    required_files = [
        project_root / "run.py",
        project_root / "src" / "main.py",
        project_root / "config" / "main.spec",
        project_root / "Student Database.ico",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
        else:
            print(f"✓ Found {file_path.name}")
    
    if missing_files:
        print("✗ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    project_root = get_project_root()
    spec_file = project_root / "config" / "main.spec"
    
    try:
        # Change to project root directory
        os.chdir(project_root)
        
        # Run PyInstaller
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            str(spec_file)
        ], check=True)
        
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error building executable: {e}")
        return False

def verify_executable():
    """Verify that the executable was created and works"""
    print("Verifying executable...")
    project_root = get_project_root()
    exe_path = project_root / "dist" / "Student Database Management System.exe"
    
    if not exe_path.exists():
        print(f"✗ Executable not found at {exe_path}")
        return False
    
    print(f"✓ Executable created at: {exe_path}")
    
    # Get file size
    file_size = exe_path.stat().st_size / (1024 * 1024)  # Convert to MB
    print(f"✓ Executable size: {file_size:.1f} MB")
    
    return True

def create_distribution():
    """Create a distribution folder with the executable and necessary files"""
    print("Creating distribution package...")
    project_root = get_project_root()
    dist_dir = project_root / "dist"
    exe_path = dist_dir / "Student Database Management System.exe"
    
    if not exe_path.exists():
        print("✗ Executable not found. Cannot create distribution.")
        return False
    
    # Create distribution info file
    info_file = dist_dir / "README.txt"
    with open(info_file, 'w') as f:
        f.write("Student Database Management System\n")
        f.write("===================================\n\n")
        f.write("Installation Instructions:\n")
        f.write("1. Double-click 'Student Database Management System.exe' to run\n")
        f.write("2. The application will create a database automatically on first run\n")
        f.write("3. Use the default login credentials:\n")
        f.write("   Username: admin\n")
        f.write("   Password: admin\n\n")
        f.write("Features:\n")
        f.write("- Student record management\n")
        f.write("- ID card generation with photos\n")
        f.write("- Data export functionality\n")
        f.write("- Search and filter capabilities\n\n")
        f.write("For support or issues, please refer to the documentation.\n")
    
    print(f"✓ Distribution package created in: {dist_dir}")
    return True

def main():
    """Main build process"""
    print("=" * 60)
    print("Student Database Management System - Build Script")
    print("=" * 60)
    
    project_root = get_project_root()
    print(f"Project root: {project_root}")
    
    # Step 1: Verify files
    if not verify_files():
        print("\n✗ Build failed: Missing required files")
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n✗ Build failed: Could not install dependencies")
        return False
    
    # Step 3: Clean build directories
    clean_build_directories()
    
    # Step 4: Build executable
    if not build_executable():
        print("\n✗ Build failed: Could not create executable")
        return False
    
    # Step 5: Verify executable
    if not verify_executable():
        print("\n✗ Build failed: Executable verification failed")
        return False
    
    # Step 6: Create distribution
    if not create_distribution():
        print("\n✗ Build failed: Could not create distribution")
        return False
    
    print("\n" + "=" * 60)
    print("BUILD SUCCESSFUL!")
    print("=" * 60)
    print(f"Executable location: {project_root / 'dist' / 'Student Database Management System.exe'}")
    print("The application is ready for distribution.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
