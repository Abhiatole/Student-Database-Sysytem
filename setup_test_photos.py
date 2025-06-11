#!/usr/bin/env python3
"""
Script to associate existing profile pictures with students for testing ID card functionality
"""

import os
import sqlite3

def setup_test_profile_pictures():
    """Associate existing profile pictures with students"""
    print("🔧 Setting up test profile pictures for students...")
    
    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), 'student_management_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get profile pictures directory
    profile_pics_dir = os.path.join(os.path.dirname(__file__), 'profile_pictures')
    
    if not os.path.exists(profile_pics_dir):
        print("❌ Profile pictures directory not found")
        return False
    
    # Get list of available profile pictures
    image_files = [f for f in os.listdir(profile_pics_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    if not image_files:
        print("❌ No image files found in profile pictures directory")
        return False
    
    print(f"Found {len(image_files)} profile pictures:")
    for img in image_files:
        print(f"  - {img}")
    
    # Get first few students
    cursor.execute("SELECT student_id, roll_number, name FROM students LIMIT ?", (len(image_files),))
    students = cursor.fetchall()
    
    if not students:
        print("❌ No students found in database")
        return False
    
    print(f"\nAssociating pictures with {len(students)} students:")
    
    # Associate each student with a profile picture
    for i, student in enumerate(students):
        if i < len(image_files):
            student_id, roll_number, name = student
            image_file = image_files[i]
            image_path = os.path.join(profile_pics_dir, image_file)
            
            # Update student record with profile picture path
            cursor.execute("""
                UPDATE students 
                SET profile_picture_path = ? 
                WHERE student_id = ?
            """, (image_path, student_id))
            
            print(f"  ✅ {roll_number} ({name}) -> {image_file}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Successfully associated {min(len(students), len(image_files))} students with profile pictures!")
    return True

def main():
    """Main function"""
    print("📸 Profile Picture Setup for ID Card Testing")
    print("=" * 50)
    
    success = setup_test_profile_pictures()
    
    if success:
        print("\n✅ Setup complete! You can now test ID card generation:")
        print("1. Run the main application: python Main.py")
        print("2. Go to the ID Card tab")
        print("3. Enter roll number: STU001, STU002, STU003, etc.")
        print("4. Click 'Load Student' then 'Generate ID Card'")
        print("5. The ID card should now show the student's profile picture!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
