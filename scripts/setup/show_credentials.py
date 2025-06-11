"""
Display actual login credentials from the seed data
"""
import sqlite3

# These are the actual credentials from seed_sample_data.py
print("=== STUDENT DATABASE MANAGEMENT SYSTEM ===")
print("Available Login Credentials:")
print("-" * 40)

credentials = [
    ("admin", "admin123", "System Administrator"),
    ("john_doe", "password123", "Student"),
    ("jane_smith", "password123", "Student"),
    ("mike_wilson", "password123", "Student"),
    ("sarah_davis", "password123", "Student"),
    ("alex_brown", "password123", "Student"),
    ("teacher1", "teacher123", "Teacher"),
    ("teacher2", "teacher123", "Teacher")
]

for username, password, role in credentials:
    print(f"{role:20} | {username:12} | {password}")

print("-" * 40)
print("💡 Tip: Use any of these credentials to login to the system")
print("🚀 Run: python Main.py")
