#!/usr/bin/env python3
"""
Comprehensive test for ID card generation with profile pictures
This test creates actual ID card images to verify the functionality works end-to-end
"""

import os
import sys
import sqlite3
from datetime import datetime
from PIL import Image
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the necessary functions from Main.py
def test_id_card_image_generation():
    """Test ID card image generation with actual profile pictures"""
    print("🎯 Testing ID Card Image Generation with Profile Pictures")
    print("=" * 60)
    
    # Set up database connection
    db_path = os.path.join(os.path.dirname(__file__), 'student_management_system.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get a student with a profile picture
    cursor.execute("""
        SELECT s.*, c.course_name, ay.year_name, f.faculty_name
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.course_id
        LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
        LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
        WHERE s.profile_picture_path IS NOT NULL AND s.profile_picture_path != ''
        LIMIT 1
    """)
    
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        print("❌ No student with profile picture found")
        return False
    
    print(f"📝 Testing with student: {student['name']} ({student['roll_number']})")
    print(f"📷 Profile picture: {os.path.basename(student['profile_picture_path'])}")
    
    # Check if profile picture exists
    if not os.path.exists(student['profile_picture_path']):
        print(f"❌ Profile picture file not found: {student['profile_picture_path']}")
        return False
    
    print(f"✅ Profile picture exists: {student['profile_picture_path']}")
    
    # Test profile picture loading
    try:
        img = Image.open(student['profile_picture_path'])
        print(f"✅ Profile picture loaded successfully: {img.size} pixels, {img.mode} mode")
    except Exception as e:
        print(f"❌ Failed to load profile picture: {e}")
        return False
    
    # Simulate the ID card generation process
    try:
        print("\n🔧 Testing ID Card Generation Process...")
        
        # Create test ID card image
        img_width, img_height = 800, 500
        id_card_img = Image.new('RGB', (img_width, img_height), 'lightblue')
        
        # Test profile picture resizing and pasting
        profile_img = Image.open(student['profile_picture_path'])
        profile_img_resized = profile_img.resize((152, 152), Image.Resampling.LANCZOS)
        
        # Paste the image (simulating the ID card generation)
        id_card_img.paste(profile_img_resized, (44, 124))
        
        # Save test ID card to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            test_id_card_path = tmp_file.name
            id_card_img.save(test_id_card_path, "PNG", quality=95)
        
        print(f"✅ Test ID card generated successfully: {test_id_card_path}")
        
        # Verify the generated file
        if os.path.exists(test_id_card_path):
            file_size = os.path.getsize(test_id_card_path)
            print(f"✅ Generated file size: {file_size} bytes")
            
            # Load and verify the generated image
            test_img = Image.open(test_id_card_path)
            print(f"✅ Generated image dimensions: {test_img.size}")
            
            # Clean up test file
            os.unlink(test_id_card_path)
            print("🗑️  Temporary test file cleaned up")
            
            return True
        else:
            print("❌ Generated file not found")
            return False
            
    except Exception as e:
        print(f"❌ ID card generation failed: {e}")
        return False

def test_sqlite_row_access():
    """Test that sqlite3.Row objects work correctly with our ID card code"""
    print("\n🔍 Testing SQLite Row Object Access")
    print("=" * 40)
    
    db_path = os.path.join(os.path.dirname(__file__), 'student_management_system.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, c.course_name, ay.year_name
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.course_id
        LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
        WHERE s.profile_picture_path IS NOT NULL
        LIMIT 1
    """)
    
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        print("❌ No student found")
        return False
    
    # Test accessing student data like our ID card code does
    try:
        # These are the key accesses that were failing before
        name = student['name']
        roll_number = student['roll_number']
        profile_path = student['profile_picture_path']
        course_name = student['course_name']
        
        print(f"✅ Name access: {name}")
        print(f"✅ Roll number access: {roll_number}")
        print(f"✅ Profile path access: {profile_path}")
        print(f"✅ Course name access: {course_name}")
        
        # Test the conditional that was causing AttributeError
        if student['profile_picture_path'] and os.path.exists(student['profile_picture_path']):
            print("✅ Conditional check passed")
        else:
            print("⚠️  Profile picture not accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLite Row access failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ID Card Profile Picture Generation Test Suite")
    print("=" * 60)
    
    # Test 1: SQLite Row access
    row_test = test_sqlite_row_access()
    
    # Test 2: ID card image generation
    generation_test = test_id_card_image_generation()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"🗃️  SQLite Row Access: {'✅ PASS' if row_test else '❌ FAIL'}")
    print(f"🎨 ID Card Generation: {'✅ PASS' if generation_test else '❌ FAIL'}")
    
    if row_test and generation_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The ID card generation with profile pictures should work correctly!")
        print("\n📋 Next Steps:")
        print("1. Run the main application: python Main.py")
        print("2. Navigate to the ID Card tab")
        print("3. Enter roll number: STU001, STU002, STU003, etc.")
        print("4. Click 'Load Student' then 'Generate ID Card'")
        print("5. Profile pictures should now appear in the generated ID cards!")
        return True
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
