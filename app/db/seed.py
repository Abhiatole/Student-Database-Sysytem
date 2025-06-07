from app.db.database import get_db_connection
from app.utils.security import hash_password

# Place initial data seeding logic here for faculties, courses, etc.
def seed_defaults():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Admin user
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, password_hash, name, role) VALUES (?, ?, ?, ?)",
            ('admin', hash_password('admin'), 'Administrator', 'admin')
        )
        # Faculties
        faculties = [
            ('School of Computer Science',),
            ('School of Management',),
            ('School of Science',)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO faculties (faculty_name) VALUES (?)",
            faculties
        )
        # Academic Years
        academic_years = [
            ('First Year',),
            ('Second Year',),
            ('Third Year',),
            ('Fourth Year',),
            ('Fifth Year',)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO academic_years (year_name) VALUES (?)",
            academic_years
        )
        # Fetch faculty IDs for course mapping
        cursor.execute("SELECT faculty_id, faculty_name FROM faculties")
        faculty_map = {name: fid for fid, name in cursor.fetchall()}
        # Courses
        courses = [
            ('BCA', faculty_map.get('School of Computer Science')),
            ('MCA', faculty_map.get('School of Computer Science')),
            ('BBA', faculty_map.get('School of Management')),
            ('B.Sc. (Physics)', faculty_map.get('School of Science')),
            ('Integrated MCA', faculty_map.get('School of Computer Science'))
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO courses (course_name, faculty_id) VALUES (?, ?)",
            courses
        )
        # Example Students
        students = [
            ('stu001', hash_password('password1'), 'Alice', 'student', 1, 1, 1),
            ('stu002', hash_password('password2'), 'Bob', 'student', 2, 2, 2),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO users (user_id, password_hash, name, role, faculty_id, course_id, year_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            students
        )
        conn.commit()

# Add to seed.py after seeding
def print_seed_summary():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM faculties")
        faculties = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM courses")
        courses = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='student'")
        students = cursor.fetchone()[0]
        print(f"Seeded {faculties} faculties, {courses} courses, {students} students.")
