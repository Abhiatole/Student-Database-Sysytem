# Test script to verify Student Management UI components
import tkinter as tk
from ttkbootstrap import Style, ttk
import sys
import os

# Add the project root to Python path
sys.path.append('.')

def test_student_management_ui():
    """Test the Student Management UI to verify all components are visible"""
    
    # Create test window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    style = Style(theme="superhero")
    
    # Create test frame
    test_frame = ttk.Frame(root)
    test_frame.pack(fill='both', expand=True)
    
    try:
        # Import and create StudentManagementTab
        from app.gui.students import StudentManagementTab
        
        # Create the student management tab
        student_tab = StudentManagementTab(test_frame)
        
        # Check if the student_frame exists
        if hasattr(student_tab, 'student_frame'):
            frame = student_tab.student_frame
            
            # Check for profile picture upload button
            profile_upload_found = False
            print_button_found = False
            export_button_found = False
            treeview_found = False
            
            def check_widgets(widget):
                nonlocal profile_upload_found, print_button_found, export_button_found, treeview_found
                
                # Check if it's a button with specific text
                if isinstance(widget, ttk.Button):
                    text = widget.cget('text') if hasattr(widget, 'cget') else str(widget)
                    if '📁 Upload' in str(text) or 'Upload' in str(text):
                        profile_upload_found = True
                        print(f"✓ Found profile upload button: {text}")
                    elif '🖨️ Print' in str(text) or 'Print' in str(text):
                        print_button_found = True
                        print(f"✓ Found print button: {text}")
                    elif '📄 Export' in str(text) or 'Export' in str(text):
                        export_button_found = True
                        print(f"✓ Found export button: {text}")
                
                # Check if it's a Treeview (for student records)
                if isinstance(widget, ttk.Treeview):
                    treeview_found = True
                    columns = widget['columns']
                    print(f"✓ Found student records Treeview with columns: {columns}")
                
                # Recursively check children
                try:
                    for child in widget.winfo_children():
                        check_widgets(child)
                except:
                    pass
            
            # Start checking from the student frame
            check_widgets(frame)
            
            # Report results
            print("\n" + "="*50)
            print("STUDENT MANAGEMENT UI VERIFICATION RESULTS:")
            print("="*50)
            print(f"Profile Picture Upload Button: {'✓ FOUND' if profile_upload_found else '✗ MISSING'}")
            print(f"Print Button: {'✓ FOUND' if print_button_found else '✗ MISSING'}")
            print(f"Export Button: {'✓ FOUND' if export_button_found else '✗ MISSING'}")
            print(f"Student Records TreeView: {'✓ FOUND' if treeview_found else '✗ MISSING'}")
            
            # Overall status
            all_found = all([profile_upload_found, print_button_found, export_button_found, treeview_found])
            print(f"\nOverall Status: {'✓ ALL COMPONENTS VISIBLE' if all_found else '✗ SOME COMPONENTS MISSING'}")
            
            if not all_found:
                print("\nMISSING COMPONENTS NEED TO BE ADDED!")
            
            return all_found
            
        else:
            print("✗ ERROR: StudentManagementTab does not have student_frame attribute")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: Failed to create StudentManagementTab: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        root.destroy()

if __name__ == "__main__":
    test_student_management_ui()
