#!/usr/bin/env python3
"""
Student Database Management System - Entry Point
This script serves as the main entry point for the application.
"""

import sys
import os

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

def main():
    """Main entry point for the application"""
    try:
        # Import and run the main application
        from main import init_db, LoginWindow
        import tkinter as tk
        
        # Initialize database
        init_db()
        
        # Create and run the application
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Please ensure all required dependencies are installed.")
        print("Run: pip install -r config/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
