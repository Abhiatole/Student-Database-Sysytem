import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.getenv('DATABASE_NAME', 'student_management_system.db')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'your_email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_app_password')
