import sqlite3
from app.config import DATABASE_NAME

SCHEMA = '''
-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'student'))
);
-- Faculties Table
CREATE TABLE IF NOT EXISTS faculties (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_name TEXT NOT NULL UNIQUE
);
-- Academic Years Table
CREATE TABLE IF NOT EXISTS academic_years (
    year_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_name TEXT NOT NULL UNIQUE
);
-- Courses Table
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL UNIQUE,
    faculty_id INTEGER,
    FOREIGN KEY (faculty_id) REFERENCES faculties(faculty_id)
);
-- Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT UNIQUE NOT NULL,
    user_id TEXT UNIQUE,
    name TEXT NOT NULL,
    contact_number TEXT,
    email TEXT,
    address TEXT,
    aadhaar_no TEXT UNIQUE,
    date_of_birth TEXT,
    gender TEXT,
    tenth_percent REAL,
    twelfth_percent REAL,
    blood_group TEXT,
    mother_name TEXT,
    enrollment_status INTEGER DEFAULT 1,
    enrollment_date TEXT NOT NULL,
    course_id INTEGER,
    academic_year_id INTEGER,
    profile_picture_path TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (academic_year_id) REFERENCES academic_years(year_id)
);
-- Marks Table
CREATE TABLE IF NOT EXISTS marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    subject_name TEXT NOT NULL,
    semester INTEGER NOT NULL,
    marks_obtained REAL,
    max_marks REAL,
    grade TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount_paid REAL NOT NULL,
    payment_date TEXT NOT NULL,
    payment_type TEXT,
    receipt_number TEXT UNIQUE NOT NULL,
    description TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
-- Communications Table
CREATE TABLE IF NOT EXISTS communications (
    comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id TEXT,
    sender_name TEXT,
    sender_email TEXT,
    subject TEXT NOT NULL,
    message_text TEXT NOT NULL,
    response_text TEXT,
    type TEXT NOT NULL CHECK(type IN ('query', 'feedback', 'announcement')),
    status TEXT DEFAULT 'Pending',
    timestamp TEXT NOT NULL,
    response_timestamp TEXT,
    FOREIGN KEY(sender_id) REFERENCES users(user_id) ON DELETE SET NULL
);
-- Delivery Log Table
CREATE TABLE IF NOT EXISTS delivery_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artefact_type TEXT NOT NULL,
    artefact_identifier TEXT NOT NULL,
    recipient_address TEXT NOT NULL,
    channel TEXT NOT NULL,
    delivery_status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    error_message TEXT
);
'''

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    with get_db_connection() as conn:
        conn.executescript(SCHEMA)
        # Insert default data if needed (see seed.py for details)
