"""
Configuration settings for the Student Database Management System
"""

import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Directory paths
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ASSETS_DIR = os.path.join(SRC_DIR, "assets")
PROFILE_PICTURES_DIR = os.path.join(ASSETS_DIR, "profile_pictures")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")

# Database configuration
DATABASE_PATH = os.path.join(DATA_DIR, "student_management_system.db")

# Asset file paths
LOGO_PATH = os.path.join(IMAGES_DIR, "logo.png")
COLLEGE_BANNER_PATH = os.path.join(IMAGES_DIR, "college_banner.png")
ID_CARD_BG_PATH = os.path.join(IMAGES_DIR, "id_card_bg.png")

# Email configuration (placeholder)
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# Application settings
APP_NAME = "Student Database Management System"
APP_VERSION = "2.0"
APP_AUTHOR = "Rushikesh Atole and Team"

# UI settings
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_GEOMETRY = "1200x800"
THEME = "cosmo"  # ttkbootstrap theme

# Ensure critical directories exist
def ensure_directories():
    """Ensure all necessary directories exist"""
    dirs = [DATA_DIR, ASSETS_DIR, PROFILE_PICTURES_DIR, IMAGES_DIR]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

# Initialize directories when module is imported
ensure_directories()
