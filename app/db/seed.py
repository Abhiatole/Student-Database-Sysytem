from app.db.database import get_db_connection
from app.utils.security import hash_password

# Place initial data seeding logic here for faculties, courses, etc.
def seed_defaults():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Admin user
        cursor.execute("INSERT OR IGNORE INTO users (user_id, password_hash, name, role) VALUES (?, ?, ?, ?)",
                       ('admin', hash_password('admin'), 'Administrator', 'admin'))
        # Faculties
        faculties = [('School of Computer Science',), ('School of Management',), ('School of Science',)]
        cursor.executemany("INSERT OR IGNORE INTO faculties (faculty_name) VALUES (?)", faculties)
        # Academic Years
        academic_years = [('First Year',), ('Second Year',), ('Third Year',), ('Fourth Year',), ('Fifth Year',)]
        cursor.executemany("INSERT OR IGNORE INTO academic_years (year_name) VALUES (?)", academic_years)
        # Courses
        faculty_ids = {name: i+1 for i, (name,) in enumerate(faculties)}
        courses = [
            ('BCA', faculty_ids['School of Computer Science']),
            ('MCA', faculty_ids['School of Computer Science']),
            ('BBA', faculty_ids['School of Management']),
            ('B.Sc. (Physics)', faculty_ids['School of Science']),
            ('Integrated MCA', faculty_ids['School of Computer Science'])
        ]
        cursor.executemany("INSERT OR IGNORE INTO courses (course_name, faculty_id) VALUES (?, ?)", courses)
        conn.commit()
