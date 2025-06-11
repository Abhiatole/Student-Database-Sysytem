#!/usr/bin/env python3
"""
Sample Data Seeder for Student Database Management System
This script adds sample users, students, and marks data for testing purposes.
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
import random
import os

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect("student_management_system.db")
    conn.row_factory = sqlite3.Row
    return conn

def seed_sample_data():
    """Add comprehensive sample data to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🌱 Seeding sample data...")
        
        # 1. Add sample users (login credentials)
        sample_users = [
            ('admin', 'admin123', 'System Administrator', 'admin'),
            ('john_doe', 'password123', 'John Doe', 'student'),
            ('jane_smith', 'password123', 'Jane Smith', 'student'),
            ('mike_wilson', 'password123', 'Mike Wilson', 'student'),
            ('sarah_johnson', 'password123', 'Sarah Johnson', 'student'),
            ('david_brown', 'password123', 'David Brown', 'student'),
            ('teacher1', 'teacher123', 'Prof. Anderson', 'admin'),
            ('teacher2', 'teacher123', 'Dr. Martinez', 'admin')
        ]
        
        for user_id, password, name, role in sample_users:
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, password_hash, name, role) 
                VALUES (?, ?, ?, ?)
            """, (user_id, hash_password(password), name, role))
        
        print("✅ Added sample users")
        
        # 2. Get course and academic year IDs
        cursor.execute("SELECT course_id, course_name FROM courses")
        courses = {row['course_name']: row['course_id'] for row in cursor.fetchall()}
        
        cursor.execute("SELECT year_id, year_name FROM academic_years")
        years = {row['year_name']: row['year_id'] for row in cursor.fetchall()}
        
        # 3. Add sample students
        sample_students = [
            {
                'roll_number': 'BCA001',
                'user_id': 'john_doe',
                'name': 'John Doe',
                'contact_number': '+91-9876543210',
                'email': 'john.doe@example.com',
                'address': '123 Main Street, Mumbai, Maharashtra',
                'aadhaar_no': '123456789012',
                'date_of_birth': '2002-05-15',
                'gender': 'Male',
                'tenth_percent': 85.5,
                'twelfth_percent': 78.0,
                'blood_group': 'B+',
                'mother_name': 'Mary Doe',
                'course': 'BCA',
                'academic_year': 'Second Year'
            },
            {
                'roll_number': 'BCA002',
                'user_id': 'jane_smith',
                'name': 'Jane Smith',
                'contact_number': '+91-9876543211',
                'email': 'jane.smith@example.com',
                'address': '456 Oak Avenue, Delhi, Delhi',
                'aadhaar_no': '123456789013',
                'date_of_birth': '2001-08-22',
                'gender': 'Female',
                'tenth_percent': 92.0,
                'twelfth_percent': 89.5,
                'blood_group': 'A+',
                'mother_name': 'Lisa Smith',
                'course': 'BCA',
                'academic_year': 'Third Year'
            },
            {
                'roll_number': 'MCA001',
                'user_id': 'mike_wilson',
                'name': 'Mike Wilson',
                'contact_number': '+91-9876543212',
                'email': 'mike.wilson@example.com',
                'address': '789 Pine Road, Bangalore, Karnataka',
                'aadhaar_no': '123456789014',
                'date_of_birth': '2000-12-10',
                'gender': 'Male',
                'tenth_percent': 88.0,
                'twelfth_percent': 82.5,
                'blood_group': 'O+',
                'mother_name': 'Patricia Wilson',
                'course': 'MCA',
                'academic_year': 'First Year'
            },
            {
                'roll_number': 'BBA001',
                'user_id': 'sarah_johnson',
                'name': 'Sarah Johnson',
                'contact_number': '+91-9876543213',
                'email': 'sarah.johnson@example.com',
                'address': '321 Cedar Lane, Chennai, Tamil Nadu',
                'aadhaar_no': '123456789015',
                'date_of_birth': '2001-03-18',
                'gender': 'Female',
                'tenth_percent': 90.5,
                'twelfth_percent': 87.0,
                'blood_group': 'AB+',
                'mother_name': 'Rebecca Johnson',
                'course': 'BBA',
                'academic_year': 'Second Year'
            },
            {
                'roll_number': 'BSC001',
                'user_id': 'david_brown',
                'name': 'David Brown',
                'contact_number': '+91-9876543214',
                'email': 'david.brown@example.com',
                'address': '654 Maple Street, Pune, Maharashtra',
                'aadhaar_no': '123456789016',
                'date_of_birth': '2002-07-25',
                'gender': 'Male',
                'tenth_percent': 87.5,
                'twelfth_percent': 84.0,
                'blood_group': 'A-',
                'mother_name': 'Helen Brown',
                'course': 'B.Sc. (Physics)',
                'academic_year': 'First Year'
            }
        ]
        
        for student in sample_students:
            course_id = courses.get(student['course'])
            year_id = years.get(student['academic_year'])
            
            cursor.execute("""
                INSERT OR IGNORE INTO students 
                (roll_number, user_id, name, contact_number, email, address, aadhaar_no, 
                 date_of_birth, gender, tenth_percent, twelfth_percent, blood_group, 
                 mother_name, enrollment_status, enrollment_date, course_id, academic_year_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student['roll_number'], student['user_id'], student['name'],
                student['contact_number'], student['email'], student['address'],
                student['aadhaar_no'], student['date_of_birth'], student['gender'],
                student['tenth_percent'], student['twelfth_percent'], student['blood_group'],
                student['mother_name'], 1, datetime.now().strftime("%Y-%m-%d"),
                course_id, year_id
            ))
        
        print("✅ Added sample students")
        
        # 4. Add sample marks
        cursor.execute("SELECT student_id, course_id FROM students WHERE roll_number IN ('BCA001', 'BCA002', 'MCA001', 'BBA001', 'BSC001')")
        students_courses = cursor.fetchall()
        
        # Define subjects for each course
        subjects_by_course = {
            courses['BCA']: [
                ('Programming in C', 1), ('Database Management', 1), ('Web Technology', 2),
                ('Data Structures', 2), ('Computer Networks', 3), ('Software Engineering', 3)
            ],
            courses['MCA']: [
                ('Advanced Programming', 1), ('System Analysis', 1), ('Database Systems', 2),
                ('Computer Graphics', 2), ('Artificial Intelligence', 3), ('Project Management', 3)
            ],
            courses['BBA']: [
                ('Business Mathematics', 1), ('Principles of Management', 1), ('Marketing Management', 2),
                ('Financial Management', 2), ('Human Resource Management', 3), ('Strategic Management', 3)
            ],
            courses['B.Sc. (Physics)']: [
                ('Mechanics', 1), ('Thermodynamics', 1), ('Electromagnetism', 2),
                ('Optics', 2), ('Quantum Physics', 3), ('Nuclear Physics', 3)
            ]
        }
        
        # Add marks for each student
        for student_course in students_courses:
            student_id = student_course['student_id']
            course_id = student_course['course_id']
            
            if course_id in subjects_by_course:
                for subject_name, semester in subjects_by_course[course_id]:
                    # Generate random marks (70-95 range for good students)
                    marks_obtained = round(random.uniform(70, 95), 1)
                    max_marks = 100
                    
                    # Calculate grade
                    percentage = (marks_obtained / max_marks) * 100
                    if percentage >= 90:
                        grade = 'A+'
                    elif percentage >= 80:
                        grade = 'A'
                    elif percentage >= 70:
                        grade = 'B+'
                    elif percentage >= 60:
                        grade = 'B'
                    else:
                        grade = 'C'
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO marks 
                        (student_id, course_id, subject_name, semester, marks_obtained, max_marks, grade)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (student_id, course_id, subject_name, semester, marks_obtained, max_marks, grade))
        
        print("✅ Added sample marks")
        
        # 5. Add sample payment records
        cursor.execute("SELECT student_id, name, roll_number FROM students")
        all_students = cursor.fetchall()
        
        payment_types = ['Tuition Fee', 'Exam Fee', 'Library Fee', 'Lab Fee', 'Hostel Fee']
        
        for student in all_students:
            # Add 2-3 payments per student
            for i in range(random.randint(2, 3)):
                payment_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
                payment_type = random.choice(payment_types)
                amount = random.choice([5000, 7500, 10000, 15000, 20000])  # Common fee amounts
                receipt_number = f"RCP{datetime.now().strftime('%Y%m%d')}{student['student_id']:03d}{i:02d}"
                description = f"{payment_type} payment for {student['name']}"
                
                cursor.execute("""
                    INSERT OR IGNORE INTO payments 
                    (student_id, amount_paid, payment_date, payment_type, receipt_number, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (student['student_id'], amount, payment_date, payment_type, receipt_number, description))
        
        print("✅ Added sample payments")
        
        # 6. Add sample communications
        sample_communications = [
            {
                'sender_id': 'john_doe',
                'sender_name': 'John Doe',
                'sender_email': 'john.doe@example.com',
                'subject': 'Query about exam schedule',
                'message_text': 'Hello, I wanted to know when the final exams will be conducted. Please provide the schedule.',
                'type': 'query',
                'timestamp': (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'sender_id': None,
                'sender_name': 'Anonymous Student',
                'sender_email': 'student@example.com',
                'subject': 'Feedback on teaching quality',
                'message_text': 'The teaching quality has improved significantly this semester. Keep up the good work!',
                'type': 'feedback',
                'timestamp': (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'sender_id': 'teacher1',
                'sender_name': 'Prof. Anderson',
                'sender_email': 'anderson@college.edu',
                'subject': 'Holiday Announcement',
                'message_text': 'The college will remain closed on Monday due to a public holiday.',
                'type': 'announcement',
                'timestamp': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        for comm in sample_communications:
            cursor.execute("""
                INSERT OR IGNORE INTO communications 
                (sender_id, sender_name, sender_email, subject, message_text, type, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (comm['sender_id'], comm['sender_name'], comm['sender_email'], 
                  comm['subject'], comm['message_text'], comm['type'], 'Pending', comm['timestamp']))
        
        print("✅ Added sample communications")
        
        # Commit all changes
        conn.commit()
        print("\n🎉 Sample data seeding completed successfully!")
        print("\n📋 Sample Login Credentials:")
        print("Admin: admin / admin123")
        print("Students:")
        for user_id, password, name, role in sample_users:
            if role == 'student':
                print(f"  {name}: {user_id} / {password}")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_sample_data()
