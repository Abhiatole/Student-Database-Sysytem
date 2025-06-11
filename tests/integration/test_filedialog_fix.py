#!/usr/bin/env python3
"""
Test script to verify that the initialfile parameter works correctly
in filedialog.asksaveasfilename()
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def test_id_card_dialog():
    """Test the ID card file dialog with the correct initialfile parameter"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Test the fixed ID card dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialfile=f"ID_Card_TEST123_{datetime.now().strftime('%Y%m%d')}.png",
            title="Test ID Card Save Dialog"
        )
        
        if file_path:
            print(f"✅ ID Card dialog test PASSED - Selected file: {file_path}")
            return True
        else:
            print("⚠️  ID Card dialog test - User cancelled")
            return False
            
    except Exception as e:
        print(f"❌ ID Card dialog test FAILED: {e}")
        return False
    finally:
        if 'root' in locals():
            root.destroy()

def test_receipt_dialog():
    """Test the receipt file dialog with the correct initialfile parameter"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Test the fixed receipt dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"Receipt_TEST_RCP_001.pdf",
            title="Test Receipt Save Dialog"
        )
        
        if file_path:
            print(f"✅ Receipt dialog test PASSED - Selected file: {file_path}")
            return True
        else:
            print("⚠️  Receipt dialog test - User cancelled")
            return False
            
    except Exception as e:
        print(f"❌ Receipt dialog test FAILED: {e}")
        return False
    finally:
        if 'root' in locals():
            root.destroy()

def main():
    """Run all dialog tests"""
    print("🧪 Testing File Dialog Fixes...")
    print("=" * 50)
    
    print("\n1. Testing ID Card File Dialog...")
    id_test_result = test_id_card_dialog()
    
    print("\n2. Testing Receipt File Dialog...")
    receipt_test_result = test_receipt_dialog()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   ID Card Dialog:  {'✅ PASS' if id_test_result else '❌ FAIL'}")
    print(f"   Receipt Dialog:  {'✅ PASS' if receipt_test_result else '❌ FAIL'}")
    
    if id_test_result and receipt_test_result:
        print("\n🎉 ALL TESTS PASSED! The initialfile parameter fix is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
