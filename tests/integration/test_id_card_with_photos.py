#!/usr/bin/env python3
"""
Test script to verify ID card generation with profile pictures
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_profile_picture_paths():
    """Test if profile pictures exist and are accessible"""
    print("=== Testing Profile Picture Access ===\n")
      # Connect to database
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(project_root, 'data', 'student_management_system.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
      # Get students with profile pictures
    cursor.execute("""
        SELECT s.roll_number, s.name, s.profile_picture_path,
               c.course_name, ay.year_name
        FROM students s 
        LEFT JOIN courses c ON s.course_id = c.course_id
        LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
        WHERE s.profile_picture_path IS NOT NULL AND s.profile_picture_path != ''
        ORDER BY s.roll_number
    """)
    
    students_with_photos = cursor.fetchall()
    
    if not students_with_photos:
        print("❌ No students found with profile pictures in database")
        return False
    
    print(f"Found {len(students_with_photos)} students with profile pictures:\n")
    
    valid_photos = 0
    for student in students_with_photos:
        student_dict = dict(student)
        pic_path = student_dict['profile_picture_path']
        
        if os.path.exists(pic_path):
            print(f"✅ {student_dict['roll_number']} - {student_dict['name']}")
            print(f"   Photo: {os.path.basename(pic_path)}")
            print(f"   Course: {student_dict['course_name'] or 'Not Assigned'}")
            print(f"   Year: {student_dict['year_name'] or 'Not Assigned'}")
            valid_photos += 1
        else:
            print(f"❌ {student_dict['roll_number']} - {student_dict['name']}")
            print(f"   Missing photo: {pic_path}")
        print()
    
    conn.close()
    
    print(f"Summary: {valid_photos}/{len(students_with_photos)} students have accessible profile pictures")
    return valid_photos > 0

def test_profile_pictures_directory():
    """Test profile pictures directory"""
    print("\n=== Testing Profile Pictures Directory ===\n")
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    profile_pics_dir = os.path.join(project_root, 'src', 'assets', 'profile_pictures')
    
    if not os.path.exists(profile_pics_dir):
        print(f"❌ Profile pictures directory not found: {profile_pics_dir}")
        return False
    
    print(f"✅ Profile pictures directory exists: {profile_pics_dir}")
    
    # List all files in the directory
    files = os.listdir(profile_pics_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    print(f"Found {len(image_files)} image files:")
    for img_file in image_files:
        file_path = os.path.join(profile_pics_dir, img_file)
        file_size = os.path.getsize(file_path)
        print(f"  - {img_file} ({file_size} bytes)")
    
    return len(image_files) > 0

def main():
    """Main test function"""
    print("🔍 Testing ID Card Profile Picture Functionality")
    print("=" * 50)
    
    # Test 1: Check profile pictures directory
    dir_test = test_profile_pictures_directory()
    
    # Test 2: Check database profile picture paths
    db_test = test_profile_picture_paths()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"📁 Profile Pictures Directory: {'✅ PASS' if dir_test else '❌ FAIL'}")
    print(f"🗃️  Database Profile Paths: {'✅ PASS' if db_test else '❌ FAIL'}")
    
    if dir_test and db_test:
        print("\n🎉 Profile picture setup looks good!")
        print("You can now test ID card generation in the main application:")
        print("1. Open the Student Database Management System")
        print("2. Go to the ID Card tab")
        print("3. Enter a roll number of a student with a profile picture")
        print("4. Click 'Load Student' and then 'Generate ID Card'")
        print("5. The generated ID card should now show the student's photo!")
    else:
        print("\n⚠️  Issues found with profile picture setup.")
        print("Please check the above details and ensure:")
        print("- Profile pictures directory exists and contains images")
        print("- Database has students with valid profile_picture_path values")
    
    return dir_test and db_test

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
