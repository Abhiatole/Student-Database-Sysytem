import sqlite3

conn = sqlite3.connect('student_management_system.db')
cursor = conn.cursor()

print("=== Users table schema ===")
cursor.execute("PRAGMA table_info(users)")
for row in cursor.fetchall():
    print(row)

print("\n=== Sample users ===")
cursor.execute("SELECT * FROM users LIMIT 3")
for row in cursor.fetchall():
    print(row)

conn.close()
