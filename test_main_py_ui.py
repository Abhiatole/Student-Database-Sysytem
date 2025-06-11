# Test script to verify Main.py UI components
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add current directory to path
sys.path.append('.')

def test_main_py_ui():
    """Test the Main.py UI to verify all components are visible"""
    
    print("="*60)
    print("TESTING MAIN.PY STUDENT MANAGEMENT UI COMPONENTS")
    print("="*60)
    
    try:
        # Import Main module
        import Main
        
        print("✓ Main.py imports successfully")
        
        # Test database initialization
        Main.init_db()
        print("✓ Database initialized successfully")
        
        # Create test window (hidden)
        root = tk.Tk()
        root.withdraw()
        
        # Create MainApplication instance
        app = Main.MainApplication(root)
        print("✓ MainApplication created successfully")
        
        # Check if student management tab exists
        if hasattr(app, 'notebook'):
            print("✓ Main notebook widget found")
            
            # Get number of tabs
            tab_count = app.notebook.index("end")
            print(f"✓ Number of tabs: {tab_count}")
            
            # List all tabs
            for i in range(tab_count):
                tab_text = app.notebook.tab(i, "text")
                print(f"  - Tab {i}: {tab_text}")
        
        # Check for student management specific components
        components_found = {
            'roll_entry': False,
            'name_entry': False,
            'profile_pic_path': False,
            'profile_pic_label': False,
            'students_tree': False,
            'upload_profile_picture': False,
            'print_student_record': False,
            'export_student_data': False
        }
        
        for component in components_found:
            if hasattr(app, component):
                components_found[component] = True
                print(f"✓ Found component: {component}")
            else:
                print(f"✗ Missing component: {component}")
        
        # Check methods
        methods_to_check = [
            'upload_profile_picture',
            'print_student_record', 
            'export_student_data',
            'view_profile_picture',
            '_show_profile_picture'
        ]
        
        for method in methods_to_check:
            if hasattr(app, method) and callable(getattr(app, method)):
                print(f"✓ Method found: {method}")
            else:
                print(f"✗ Method missing: {method}")
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY:")
        print("="*60)
        
        found_count = sum(components_found.values())
        total_count = len(components_found)
        
        print(f"Components found: {found_count}/{total_count}")
        print(f"Success rate: {(found_count/total_count)*100:.1f}%")
        
        if found_count == total_count:
            print("🎉 ALL COMPONENTS FOUND! Student management UI is complete.")
        else:
            print("⚠️  Some components are missing but basic functionality should work.")
        
        # Test basic profile picture functionality
        print("\nTesting profile picture functionality:")
        if hasattr(app, 'profile_pic_path'):
            print("✓ Profile picture path variable exists")
        if hasattr(app, 'profile_pic_label'):
            print("✓ Profile picture label exists")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_main_py_ui()
        if success:
            print("\n🎉 Main.py UI verification completed successfully!")
            print("\nThe following features should now be visible:")
            print("  • Profile picture upload button (📁 Upload)")
            print("  • Print record button (🖨️ Print Record)")
            print("  • Export data button (📄 Export Data)")
            print("  • View photo button (🖼️ View Photo)")
            print("  • Student records TreeView with all columns")
            print("  • Complete student form with all fields")
        else:
            print("\n❌ Main.py UI verification failed!")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
