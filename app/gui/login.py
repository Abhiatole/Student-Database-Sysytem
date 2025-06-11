import tkinter as tk
from tkinter import ttk, messagebox
from app.utils.security import verify_password
from app.db.database import get_db_connection
from ttkbootstrap import Style
import os

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.withdraw()
        self.login_root = tk.Toplevel(master)
        self.login_root.title("Student Database Management System - Login")
        self.login_root.geometry("500x400")
        self.login_root.resizable(False, False)
        
        # Apply theme
        self.style = Style(theme="superhero")
        
        # Center the window
        self.center_window()
        
        self.create_widgets()
        
        # Bind Enter key to login
        self.login_root.bind('<Return>', lambda event: self.login())
        
        # Set focus to username entry
        self.username_entry.focus_set()

    def center_window(self):
        """Center the login window on screen"""
        self.login_root.update_idletasks()
        x = (self.login_root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.login_root.winfo_screenheight() // 2) - (400 // 2)
        self.login_root.geometry(f"500x400+{x}+{y}")

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.login_root, padding=30)
        main_frame.pack(expand=True, fill="both")
        
        # Header with logo area
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 20))
        
        # Try to load logo
        try:
            resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
            logo_path = os.path.join(resources_dir, "logo.png")
            if os.path.exists(logo_path):
                from app.utils.image_utils import load_image
                logo_img = load_image(logo_path, size=(64, 64))
                if logo_img:
                    ttk.Label(header_frame, image=logo_img).pack()
                    # Keep a reference to prevent garbage collection
                    header_frame.logo_img = logo_img
        except:
            pass
        
        ttk.Label(header_frame, text="Student Database Management System", 
                 font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=5)
        ttk.Label(header_frame, text="Please login to continue", 
                 font=("Helvetica", 10), bootstyle="secondary").pack()
        
        # Login form
        form_frame = ttk.LabelFrame(main_frame, text="Login", padding=20, bootstyle="info")
        form_frame.pack(fill="x", pady=10)
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
        self.username_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
        self.password_entry = ttk.Entry(form_frame, show="*", font=("Helvetica", 11), width=30)
        self.password_entry.pack(fill="x", pady=(0, 15))
        
        # Login button
        login_btn = ttk.Button(form_frame, text="🔐 Login", command=self.login, 
                              bootstyle="success", width=25)
        login_btn.pack(pady=5)
        
        # Register button
        register_btn = ttk.Button(form_frame, text="👤 Register New User", command=self.open_register, 
                                 bootstyle="info-outline", width=25)
        register_btn.pack(pady=5)
        
        # Sample credentials info
        info_frame = ttk.LabelFrame(main_frame, text="Sample Credentials", padding=15, bootstyle="warning")
        info_frame.pack(fill="x", pady=(10, 0))
        
        credentials_text = """Admin: admin / admin123
Student Examples:
• john_doe / password123
• jane_smith / password123"""
          ttk.Label(info_frame, text=credentials_text, font=("Consolas", 9), 
                 bootstyle="warning").pack(anchor="w")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            self.username_entry.focus_set()
            return
            
        # Disable login button during authentication
        login_btn = None
        for widget in self.login_root.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Button) and "Login" in str(grandchild.cget('text')):
                                login_btn = grandchild
                                break
        
        if login_btn:
            login_btn.config(state="disabled", text="🔄 Authenticating...")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, password_hash, name, role FROM users WHERE user_id=?", (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and verify_password(password, user['password_hash']):
                # Store user session info
                self.current_user = {
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'role': user['role']
                }
                
                messagebox.showinfo("Login Successful", f"Welcome, {user['name']}!")
                
                # Close login window and show main application
                self.login_root.destroy()
                self.master.deiconify()
                self.master.update()
                
                # Import and start main application
                from app.main import MainApplication
                app = MainApplication(self.master)
                # Pass user session to main app
                app.current_user = self.current_user
                
            else:
                messagebox.showerror("Login Failed", 
                                   "Invalid username or password.\n\nTip: Try admin/admin123 or john_doe/password123")
                self.password_entry.delete(0, tk.END)
                self.username_entry.focus_set()
                
        except Exception as e:
            messagebox.showerror("Authentication Error", f"An error occurred during login: {e}")
            
        finally:
            # Re-enable login button
            if login_btn:
                login_btn.config(state="normal", text="🔐 Login")

    def open_register(self):
        from app.gui.register import RegisterWindow
        RegisterWindow(self.login_root)
