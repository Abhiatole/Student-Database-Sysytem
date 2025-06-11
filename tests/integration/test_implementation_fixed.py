#!/usr/bin/env python3
"""
Test implementation script to verify all enhancements are working correctly
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

def test_database_connection():
    """Test database connection and sample data"""
    print("=== Testing Database Connection ===")
    db_path = Path(__file__).parent / 'student_management_system.db'
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in database: {user_count}")
        
        # Test students table
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"✅ Students in database: {student_count}")
        
        # Test marks table
        cursor.execute("SELECT COUNT(*) FROM marks")
        marks_count = cursor.fetchone()[0]
        print(f"✅ Marks records in database: {marks_count}")
        
        # Display sample login credentials
        print("\n📋 Sample Login Credentials:")
        cursor.execute("SELECT user_id, password_hash, role FROM users LIMIT 5")
        for user_id, password_hash, role in cursor.fetchall():
            # Show shortened password hash for security
            short_hash = password_hash[:10] + "..."
            print(f"   {role}: {user_id} / [hash: {short_hash}]")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_profile_pictures_directory():
    """Test profile pictures directory structure"""
    print("\n=== Testing Profile Pictures Directory ===")
    profile_dir = Path(__file__).parent / 'profile_pictures'
    
    if profile_dir.exists():
        print("✅ Profile pictures directory exists")
        subdirs = [d for d in profile_dir.iterdir() if d.is_dir()]
        print(f"✅ Profile subdirectories: {len(subdirs)}")
        return True
    else:
        print("⚠️  Profile pictures directory not found - will be created on first upload")
        return True

def test_imports():
    """Test all required imports for enhanced features"""
    print("\n=== Testing Required Imports ===")
    
    required_modules = [
        'tkinter',
        'ttkbootstrap',
        'PIL',
        'reportlab',
        'uuid',
        'datetime',
        'os',
        'platform'
    ]
    
    success_count = 0
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
    
    return success_count == len(required_modules)

def test_file_structure():
    """Test the file structure integrity"""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        'Main.py',
        'app/gui/login.py',
        'app/gui/students.py',
        'app/db/database.py',
        'seed_sample_data.py'
    ]
    
    success_count = 0
    base_path = Path(__file__).parent
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
            success_count += 1
        else:
            print(f"❌ {file_path} missing")
    
    return success_count == len(required_files)

def test_enhanced_features():
    """Test the presence of enhanced features in code"""
    print("\n=== Testing Enhanced Features Implementation ===")
    
    # Test login.py enhancements
    login_file = Path(__file__).parent / 'app' / 'gui' / 'login.py'
    if login_file.exists():
        try:
            content = login_file.read_text(encoding='utf-8')
            features = [
                ('Session tracking', 'session_data'),
                ('Enhanced styling', 'ttkbootstrap'),
                ('Logo display', 'logo'),
                ('Sample credentials', 'Sample Login Credentials')
            ]
            
            for feature_name, search_term in features:
                if search_term in content:
                    print(f"✅ Login: {feature_name} implemented")
                else:
                    print(f"❌ Login: {feature_name} not found")
        except UnicodeDecodeError:
            print("⚠️  Could not read login.py due to encoding issues, but file exists")
    
    # Test students.py enhancements
    students_file = Path(__file__).parent / 'app' / 'gui' / 'students.py'
    if students_file.exists():
        try:
            content = students_file.read_text(encoding='utf-8')
            features = [
                ('Profile picture upload', 'upload_profile_picture'),
                ('Print functionality', 'print_student_record'),
                ('Export functionality', 'export_student_data'),
                ('PDF generation', 'reportlab'),
                ('Image viewing', 'view_profile_picture')
            ]
            
            for feature_name, search_term in features:
                if search_term in content:
                    print(f"✅ Students: {feature_name} implemented")
                else:
                    print(f"❌ Students: {feature_name} not found")
        except UnicodeDecodeError:
            print("⚠️  Could not read students.py due to encoding issues, but file exists")

def main():
    """Run all tests"""
    print("🚀 Student Database Management System - Implementation Test")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_database_connection,
        test_profile_pictures_directory,
        test_imports,
        test_enhanced_features
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The implementation is ready.")
        print("\n📖 Usage Instructions:")
        print("1. Run: python Main.py")
        print("2. Use sample credentials from show_credentials.py")
        print("3. Test new features: Print, Export, Profile Pictures")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()
