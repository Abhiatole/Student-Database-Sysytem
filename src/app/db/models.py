from app.db.database import get_db_connection
from typing import List, Optional, Dict

# Define ORM-like models or data access classes here for each table
class Student:
    @staticmethod
    def create(data: Dict) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (
                    roll_number, user_id, name, contact_number, email, address, aadhaar_no, date_of_birth, gender,
                    tenth_percent, twelfth_percent, blood_group, mother_name, enrollment_status, enrollment_date,
                    course_id, academic_year_id, profile_picture_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['roll_number'], data.get('user_id'), data['name'], data.get('contact_number'), data.get('email'),
                data.get('address'), data.get('aadhaar_no'), data.get('date_of_birth'), data.get('gender'),
                data.get('tenth_percent'), data.get('twelfth_percent'), data.get('blood_group'), data.get('mother_name'),
                data.get('enrollment_status', 1), data['enrollment_date'], data['course_id'], data['academic_year_id'],
                data.get('profile_picture_path')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_id(student_id: int) -> Optional[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_all() -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def update(student_id: int, data: Dict) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            fields = ', '.join([f"{k}=?" for k in data.keys()])
            values = list(data.values())
            values.append(student_id)
            cursor.execute(f'UPDATE students SET {fields} WHERE student_id=?', values)
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(student_id: int) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM students WHERE student_id=?', (student_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_bin():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE deleted=1')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def soft_delete(student_ids):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('UPDATE students SET deleted=1 WHERE student_id=?', [(sid,) for sid in student_ids])
            conn.commit()
            return cursor.rowcount
        
    @staticmethod
    def permanent_delete(student_ids):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('DELETE FROM students WHERE student_id=?', [(sid,) for sid in student_ids])
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def restore(student_ids):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('UPDATE students SET deleted=0 WHERE student_id=?', [(sid,) for sid in student_ids])
            conn.commit()
            return cursor.rowcount
