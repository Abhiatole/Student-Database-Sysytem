#!/usr/bin/env python3
"""
Database Seeding Script for Student Management System
This script populates the database with sample data for testing and demonstration.
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
import random

DATABASE_NAME = "student_management_system.db"

def hash_password(password):
    """Hashes the password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    """Populate the database with sample data."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
      # Clear existing data (optional - remove if you want to keep existing data)
    print("Clearing existing data...")
    tables_to_clear = [
        'delivery_logs', 'marks', 'payments', 'communications',
        'students', 'courses', 'academic_years', 'faculties', 'users'
    ]
    
    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except sqlite3.Error:
            pass  # Table might not exist yet
    
    # Seed Users
    print("Seeding users...")
    users_data = [
        ('admin', hash_password('admin123'), 'System Administrator', 'admin'),
        ('teacher1', hash_password('teacher123'), 'Dr. Sarah Johnson', 'admin'),
        ('student1', hash_password('student123'), 'John Doe', 'student'),
        ('student2', hash_password('student123'), 'Jane Smith', 'student'),
        ('demo', hash_password('demo'), 'Demo User', 'admin'),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO users (user_id, password_hash, name, role) VALUES (?, ?, ?, ?)",
        users_data
    )
    
    # Seed Faculties
    print("Seeding faculties...")
    faculties_data = [
        ('Computer Science & Engineering',),
        ('Electrical Engineering',),
        ('Mechanical Engineering',),
        ('Civil Engineering',),
        ('Business Administration',),
        ('Arts & Literature',),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO faculties (faculty_name) VALUES (?)",
        faculties_data
    )
    
    # Seed Academic Years
    print("Seeding academic years...")
    academic_years_data = [
        ('2023-24',),
        ('2024-25',),
        ('2025-26',),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO academic_years (year_name) VALUES (?)",
        academic_years_data
    )
    
    # Get IDs for foreign keys
    cursor.execute("SELECT faculty_id, faculty_name FROM faculties")
    faculties = dict(cursor.fetchall())
    
    cursor.execute("SELECT year_id, year_name FROM academic_years")
    years = dict(cursor.fetchall())
    
    # Seed Courses
    print("Seeding courses...")
    courses_data = [
        ('Bachelor of Computer Science', list(faculties.keys())[0]),
        ('Bachelor of Electrical Engineering', list(faculties.keys())[1]),
        ('Bachelor of Mechanical Engineering', list(faculties.keys())[2]),
        ('Bachelor of Civil Engineering', list(faculties.keys())[3]),
        ('Bachelor of Business Administration', list(faculties.keys())[4]),
        ('Bachelor of Arts', list(faculties.keys())[5]),
        ('Master of Computer Science', list(faculties.keys())[0]),
        ('Master of Business Administration', list(faculties.keys())[4]),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO courses (course_name, faculty_id) VALUES (?, ?)",
        courses_data
    )
    
    # Get course IDs
    cursor.execute("SELECT course_id, course_name FROM courses")
    courses = dict(cursor.fetchall())
      # Seed Students
    print("Seeding students...")
    students_data = [
        ('STU001', 'student1', 'John Doe', '555-0101', 'john.doe@email.com', '123 Main St', 'AAAA1111BBBB', '1995-05-15', 'Male', 85.5, 88.2, 'O+', 'Mary Doe', 1, '2023-09-01', list(courses.keys())[0], list(years.keys())[0], None),
        ('STU002', 'student2', 'Jane Smith', '555-0102', 'jane.smith@email.com', '456 Oak Ave', 'BBBB2222CCCC', '1996-08-22', 'Female', 92.1, 89.7, 'A+', 'Linda Smith', 1, '2023-09-01', list(courses.keys())[0], list(years.keys())[0], None),
        ('STU003', None, 'Michael Brown', '555-0103', 'michael.brown@email.com', '789 Pine Rd', 'CCCC3333DDDD', '1995-12-10', 'Male', 78.9, 82.4, 'B+', 'Patricia Brown', 1, '2023-09-01', list(courses.keys())[1], list(years.keys())[0], None),
        ('STU004', None, 'Emily Davis', '555-0104', 'emily.davis@email.com', '321 Elm St', 'DDDD4444EEEE', '1997-03-18', 'Female', 91.3, 93.6, 'AB+', 'Margaret Davis', 1, '2023-09-01', list(courses.keys())[1], list(years.keys())[0], None),
        ('STU005', None, 'Robert Wilson', '555-0105', 'robert.wilson@email.com', '654 Maple Dr', 'EEEE5555FFFF', '1996-11-25', 'Male', 84.7, 86.1, 'O-', 'Susan Wilson', 1, '2023-09-01', list(courses.keys())[2], list(years.keys())[0], None),
        ('STU006', None, 'Sarah Anderson', '555-0106', 'sarah.anderson@email.com', '987 Cedar Ln', 'FFFF6666GGGG', '1995-07-08', 'Female', 89.4, 91.8, 'A-', 'Barbara Anderson', 1, '2023-09-01', list(courses.keys())[2], list(years.keys())[0], None),
        ('STU007', None, 'David Taylor', '555-0107', 'david.taylor@email.com', '147 Birch St', 'GGGG7777HHHH', '1996-04-14', 'Male', 87.2, 85.9, 'B-', 'Helen Taylor', 1, '2023-09-01', list(courses.keys())[3], list(years.keys())[0], None),
        ('STU008', None, 'Lisa Thomas', '555-0108', 'lisa.thomas@email.com', '258 Spruce Ave', 'HHHH8888IIII', '1997-01-30', 'Female', 93.8, 94.2, 'AB-', 'Dorothy Thomas', 1, '2023-09-01', list(courses.keys())[4], list(years.keys())[0], None),
        ('STU009', None, 'James Garcia', '555-0109', 'james.garcia@email.com', '369 Fir Rd', 'IIII9999JJJJ', '1995-09-12', 'Male', 81.6, 83.7, 'O+', 'Maria Garcia', 1, '2023-09-01', list(courses.keys())[5], list(years.keys())[0], None),
        ('STU010', None, 'Amanda Martinez', '555-0110', 'amanda.martinez@email.com', '741 Ash Dr', 'JJJJ0000KKKK', '1996-06-28', 'Female', 88.9, 90.3, 'A+', 'Jennifer Martinez', 1, '2024-09-01', list(courses.keys())[0], list(years.keys())[1], None),
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO students 
           (roll_number, user_id, name, contact_number, email, address, aadhaar_no, date_of_birth, 
            gender, tenth_percent, twelfth_percent, blood_group, mother_name, enrollment_status, 
            enrollment_date, course_id, academic_year_id, profile_picture_path) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        students_data
    )
      # Seed Student Marks
    print("Seeding student marks...")
    subjects = ['Mathematics', 'Physics', 'Chemistry', 'English', 'Computer Science', 'Programming']
    
    cursor.execute("SELECT student_id, course_id FROM students")
    students_with_courses = cursor.fetchall()
    
    marks_data = []
    for student_id, course_id in students_with_courses:
        # Add 3-4 subjects per student with random marks
        student_subjects = random.sample(subjects, random.randint(3, 4))
        for i, subject in enumerate(student_subjects):
            marks_obtained = random.randint(60, 100)  # Generate marks between 60-100
            max_marks = 100
            grade = 'A+' if marks_obtained >= 95 else 'A' if marks_obtained >= 85 else 'B+' if marks_obtained >= 75 else 'B' if marks_obtained >= 65 else 'C'
            semester = random.randint(1, 2)  # Semester 1 or 2
            marks_data.append((student_id, course_id, subject, semester, marks_obtained, max_marks, grade))
    
    cursor.executemany(
        "INSERT OR IGNORE INTO marks (student_id, course_id, subject_name, semester, marks_obtained, max_marks, grade) VALUES (?, ?, ?, ?, ?, ?, ?)",
        marks_data
    )
      # Seed Payment Receipts
    print("Seeding payment receipts...")
    payment_types = ['Tuition Fee', 'Library Fee', 'Lab Fee', 'Sports Fee', 'Hostel Fee']
    payments_data = []
    
    cursor.execute("SELECT student_id FROM students")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    for i, student_id in enumerate(student_ids):
        # Add 2-4 payments per student
        for j in range(random.randint(2, 4)):
            payment_type = random.choice(payment_types)
            amount = random.randint(1000, 5000)
            receipt_number = f"REC{i+1:03d}{j+1:02d}"
            payment_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
            payments_data.append((student_id, amount, payment_date, payment_type, receipt_number, f"Payment for {payment_type}"))
    
    cursor.executemany(
        "INSERT OR IGNORE INTO payments (student_id, amount_paid, payment_date, payment_type, receipt_number, description) VALUES (?, ?, ?, ?, ?, ?)",
        payments_data
    )
      # Seed Communications
    print("Seeding communications...")
    communications_data = [
        (None, 'John Doe', 'john.doe@email.com', 'Registration Issue', 'I am having trouble with my course registration. Can you help?', '', 'query', 'Pending', '2024-01-15 10:30:00', None),
        (None, 'Jane Smith', 'jane.smith@email.com', 'Fee Payment', 'I paid my fees but it is not reflected in my account.', 'Issue resolved - payment updated in system.', 'query', 'Answered', '2024-01-20 14:15:00', '2024-01-21 09:00:00'),
        (None, 'Michael Brown', 'michael.brown@email.com', 'Transcript Request', 'I need an official transcript for job application.', '', 'query', 'Pending', '2024-01-25 09:45:00', None),
        (None, 'Emily Davis', 'emily.davis@email.com', 'Library Access', 'My library card is not working. Please help.', 'New library card issued.', 'query', 'Answered', '2024-02-01 16:20:00', '2024-02-02 10:15:00'),
        ('admin', 'System Admin', 'admin@college.edu', 'System Feedback', 'The new online system is working great! Thanks for the improvement.', 'Thank you for your feedback!', 'feedback', 'Read', '2024-02-05 11:00:00', '2024-02-05 11:30:00'),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO communications (sender_id, sender_name, sender_email, subject, message_text, response_text, type, status, timestamp, response_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        communications_data    )
    
    # Seed Delivery Logs
    print("Seeding delivery logs...")
    delivery_logs_data = [
        ('report', 'Student Marks Report', 'john.doe@email.com', 'email', 'Sent', '2024-05-01 10:15:00', None),
        ('id_card', 'STU001', 'john.doe@email.com', 'email', 'Sent', '2024-04-15 14:30:00', None),
        ('receipt', 'REC00101', 'jane.smith@email.com', 'email', 'Failed', '2024-04-20 09:45:00', 'SMTP connection failed'),
        ('report', 'Fee Collection Report', 'admin@college.edu', 'email', 'Sent', '2024-05-10 16:20:00', None),
        ('report', 'Student List Export', 'download', 'download', 'Completed', '2024-04-25 10:05:00', None),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO delivery_logs (artefact_type, artefact_identifier, recipient_address, channel, delivery_status, timestamp, error_message) VALUES (?, ?, ?, ?, ?, ?, ?)",
        delivery_logs_data
    )
    
    conn.commit()
    conn.close()
    
    print("✅ Database seeded successfully!")
    print("\n📊 Sample Data Summary:")
    print("- 5 Users (admin/admin, demo/demo, student1/student123, student2/student123)")
    print("- 3 Faculties (Computer Science, Management, Science)")
    print("- 5 Academic Years (First Year to Fifth Year)")
    print("- 6 Courses across different faculties")
    print("- 10 Students with complete profiles and academic info")
    print("- Student marks across multiple subjects and semesters")
    print("- Payment records for various fees")
    print("- Communication queries and feedback messages")
    print("- Delivery logs for emails and reports")
    print("\n🔑 Login Credentials:")
    print("- Admin: admin / admin")
    print("- Demo: demo / demo")  
    print("- Student: student1 / student123")
    print("- Student: student2 / student123")

if __name__ == "__main__":
    print("🌱 Seeding Student Management System Database...")
    print("=" * 50)
    seed_database()
