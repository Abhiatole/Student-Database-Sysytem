# ==================================================================================
# Student Database Management System
# Enhanced Version with Advanced Features
#
# @developed by Rushikesh Atole and Team (Rewritten by Gemini)
#
# Key Features:
# - Professional Dashboard Home Screen with Live Stats and Charts
# - Advanced Reporting with PDF and CSV Export Options
# - Omni-Channel Sharing via Email with Delivery Logging
# - Visual Analytics with Matplotlib Charts (Bar, Pie)
# - Integrated Communication Hub for Feedback, Queries, and Announcements
# - Modern UI/UX with ttkbootstrap and Custom Title Bar
# - Robust CRUD operations for Student Management
# - ID Card and Payment Receipt Generation
# ==================================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import hashlib
import uuid
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import tempfile
import csv

# Import ttkbootstrap Style
from ttkbootstrap import Style
from ttkbootstrap import ttk

# --- PDF and Charting Libraries ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Global Configuration ---
DATABASE_NAME = "student_management_system.db"
# --- Placeholder paths for images. Create these images or update paths. ---
# For best results, use .png files with transparent backgrounds where appropriate.
LOGO_PATH = "logo.png"  # Recommended size: 64x64 pixels
COLLEGE_BANNER_PATH = "college_banner.png" # Recommended size: 800x200 pixels
ID_CARD_BG_PATH = "id_card_bg.png" # Recommended size: 400x250 pixels

# --- Email Configuration (for the "Share via Email" feature) ---
# IMPORTANT: Use an "App Password" for Gmail if 2-Factor Authentication is enabled.
EMAIL_ADDRESS = "your_email@gmail.com"  # Sender's email address
EMAIL_PASSWORD = "your_app_password"    # Sender's email app password

# --- Utility Functions ---

def hash_password(password):
    """Hashes the password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Makes rows accessible by column name
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        -- Users Table (for login)
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'student'))
        );

        -- Faculties Table
        CREATE TABLE IF NOT EXISTS faculties (
            faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_name TEXT NOT NULL UNIQUE
        );

        -- Academic Years Table
        CREATE TABLE IF NOT EXISTS academic_years (
            year_id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_name TEXT NOT NULL UNIQUE
        );

        -- Courses Table
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL UNIQUE,
            faculty_id INTEGER,
            FOREIGN KEY (faculty_id) REFERENCES faculties(faculty_id)
        );

        -- Students Table
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            user_id TEXT UNIQUE,
            name TEXT NOT NULL,
            contact_number TEXT,
            email TEXT,
            address TEXT,
            aadhaar_no TEXT UNIQUE,
            date_of_birth TEXT,
            gender TEXT,
            tenth_percent REAL,
            twelfth_percent REAL,
            blood_group TEXT,
            mother_name TEXT,
            enrollment_status INTEGER DEFAULT 1, -- 1 for Active, 0 for Inactive
            enrollment_date TEXT NOT NULL,
            course_id INTEGER,
            academic_year_id INTEGER,
            profile_picture_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id),
            FOREIGN KEY (academic_year_id) REFERENCES academic_years(year_id)
        );

        -- Marks Table
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            semester INTEGER NOT NULL,
            marks_obtained REAL,
            max_marks REAL,
            grade TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        );

        -- Payments Table
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            amount_paid REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_type TEXT,
            receipt_number TEXT UNIQUE NOT NULL,
            description TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        -- Communications Table (for feedback, queries, and announcements)
        CREATE TABLE IF NOT EXISTS communications (
            comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT, -- user_id of sender, can be NULL for public feedback
            sender_name TEXT, -- Name if not a registered user
            sender_email TEXT, -- Email if not a registered user
            subject TEXT NOT NULL,
            message_text TEXT NOT NULL,
            response_text TEXT,
            type TEXT NOT NULL CHECK(type IN ('query', 'feedback', 'announcement')),
            status TEXT DEFAULT 'Pending', -- e.g., Pending, Answered, Read
            timestamp TEXT NOT NULL,
            response_timestamp TEXT,
            FOREIGN KEY(sender_id) REFERENCES users(user_id) ON DELETE SET NULL
        );

        -- Delivery Log Table (for tracking report/artefact distribution)
        CREATE TABLE IF NOT EXISTS delivery_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            artefact_type TEXT NOT NULL, -- e.g., 'report', 'receipt', 'ID card'
            artefact_identifier TEXT NOT NULL, -- e.g., report name, receipt_number
            recipient_address TEXT NOT NULL, -- e.g., email address, 'Downloaded', 'Printed'
            channel TEXT NOT NULL, -- e.g., 'email', 'download', 'print'
            delivery_status TEXT NOT NULL, -- e.g., 'Sent', 'Failed', 'Completed'
            timestamp TEXT NOT NULL,
            error_message TEXT -- For logging failures
        );
    ''')

    # --- Insert Default Data (if tables are empty) ---
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, password_hash, name, role) VALUES (?, ?, ?, ?)",
                       ('admin', hash_password('admin'), 'Administrator', 'admin'))

        faculties = [('School of Computer Science',), ('School of Management',), ('School of Science',)]
        cursor.executemany("INSERT OR IGNORE INTO faculties (faculty_name) VALUES (?)", faculties)

        academic_years = [('First Year',), ('Second Year',), ('Third Year',), ('Fourth Year',), ('Fifth Year',)]
        cursor.executemany("INSERT OR IGNORE INTO academic_years (year_name) VALUES (?)", academic_years)

        # Get faculty IDs to link with courses
        faculty_ids = {name: i+1 for i, (name,) in enumerate(faculties)}
        courses = [
            ('BCA', faculty_ids['School of Computer Science']),
            ('MCA', faculty_ids['School of Computer Science']),
            ('BBA', faculty_ids['School of Management']),
            ('B.Sc. (Physics)', faculty_ids['School of Science']),
            ('Integrated MCA', faculty_ids['School of Computer Science'])
        ]
        cursor.executemany("INSERT OR IGNORE INTO courses (course_name, faculty_id) VALUES (?, ?)", courses)

    except sqlite3.Error as e:
        print(f"Error inserting default data: {e}")
    finally:
        conn.commit()
        conn.close()

def load_image(path, size=None):
    """Loads an image from a path and resizes it, returning a PhotoImage object."""
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        messagebox.showerror("Image Error", f"Error loading image {path}: {e}")
        return None

def log_delivery(artefact_type, artefact_identifier, recipient, channel, status, error=''):
    """Logs a delivery attempt to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO delivery_logs (artefact_type, artefact_identifier, recipient_address, channel, delivery_status, timestamp, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (artefact_type, artefact_identifier, recipient, channel, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to log delivery: {e}")
    finally:
        if conn:
            conn.close()

# --- Custom Title Bar Class (for a modern look) ---
class CustomTitleBar(tk.Frame):
    def __init__(self, parent, title_text, style_obj):
        super().__init__(parent, bg=style_obj.colors.primary)
        self.parent = parent
        self.pack(side="top", fill="x")

        self.title_label = ttk.Label(self, text=title_text, bootstyle="inverse-primary", font=("Helvetica", 10, "bold"))
        self.title_label.pack(side="left", padx=10, pady=5)

        # Buttons
        button_frame = ttk.Frame(self, style="primary.TFrame")
        button_frame.pack(side="right", padx=2, pady=2)
        ttk.Button(button_frame, text="✕", command=self.parent.destroy, bootstyle="danger", width=3).pack(side="right")
        ttk.Button(button_frame, text="🗖", command=self.toggle_maximize, bootstyle="info", width=3).pack(side="right")
        ttk.Button(button_frame, text="—", command=self.safe_iconify, bootstyle="info", width=3).pack(side="right")

        # Drag functionality
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        self._is_maximized = False

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def stop_move(self, event):
        self._x = None
        self._y = None

    def do_move(self, event):
        if self._is_maximized: return
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.parent.winfo_x() + deltax
        y = self.parent.winfo_y() + deltay
        self.parent.geometry(f"+{x}+{y}")
    
    def toggle_maximize(self):
        if self._is_maximized:
            self.parent.wm_state('normal')
        else:
            self.parent.wm_state('zoomed')
        self._is_maximized = not self._is_maximized

    def safe_iconify(self):
        """Safe iconify that works with or without override-redirect"""
        try:
            # Check if override-redirect is set
            if self.parent.overrideredirect():
                # If override-redirect is True, we can't use iconify(), so we'll hide the window instead
                self.parent.withdraw()
                # You could also implement a custom taskbar icon here if needed
            else:
                # Normal iconify works when override-redirect is False
                self.parent.iconify()
        except Exception as e:
            print(f"Error minimizing window: {e}")
            # Fallback: just hide the window
            self.parent.withdraw()

# --- Email Dialog Window ---
class EmailDialog(tk.Toplevel):
    def __init__(self, parent, attachment_path, report_name):
        super().__init__(parent)
        self.title("Share Report via Email")
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()

        self.attachment_path = attachment_path
        self.report_name = report_name

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Send Report", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(main_frame, text=f"Attachment: {os.path.basename(attachment_path)}").pack()

        ttk.Label(main_frame, text="Recipient Email:").pack(pady=(10, 0), anchor='w')
        self.email_entry = ttk.Entry(main_frame, width=50)
        self.email_entry.pack(fill='x')

        ttk.Label(main_frame, text="Subject:").pack(pady=(10, 0), anchor='w')
        self.subject_entry = ttk.Entry(main_frame, width=50)
        self.subject_entry.pack(fill='x')
        self.subject_entry.insert(0, f"Student Management System Report: {self.report_name}")

        ttk.Label(main_frame, text="Message:").pack(pady=(10, 0), anchor='w')
        self.message_text = tk.Text(main_frame, height=5)
        self.message_text.pack(fill='x', expand=True)
        self.message_text.insert("1.0", f"Please find the attached report: {self.report_name}.\n\nGenerated from the Student Database Management System.")

        send_button = ttk.Button(main_frame, text="Send Email", command=self.send_email, bootstyle="success")
        send_button.pack(pady=20)

    def send_email(self):
        recipient = self.email_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.message_text.get("1.0", tk.END).strip()

        if not recipient or not subject:
            messagebox.showerror("Input Error", "Recipient Email and Subject are required.", parent=self)
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with open(self.attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(self.attachment_path)}")
            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            log_delivery(
                artefact_type='report',
                artefact_identifier=self.report_name,
                recipient=recipient,
                channel='email',
                status='Sent'
            )
            messagebox.showinfo("Success", "Email sent successfully!", parent=self)
            self.destroy()

        except Exception as e:
            log_delivery(
                artefact_type='report',
                artefact_identifier=self.report_name,
                recipient=recipient,
                channel='email',
                status='Failed',
                error=str(e)
            )
            messagebox.showerror("Email Error", f"Failed to send email: {e}", parent=self)

# --- Login and Registration Windows (Simplified for brevity) ---
# The logic is similar to the original file, focusing on the MainApplication rewrite.
class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.withdraw()
        self.login_root = tk.Toplevel(master)
        self.login_root.title("Login")
        self.login_root.geometry("400x350")
        self.login_root.resizable(False, False)
        self.style = Style(theme="superhero")
        self.title_bar = CustomTitleBar(self.login_root, "Student Database Management System", self.style)

        # Center window
        self.login_root.update_idletasks()
        x = self.login_root.winfo_screenwidth() // 2 - self.login_root.winfo_width() // 2
        y = self.login_root.winfo_screenheight() // 2 - self.login_root.winfo_height() // 2
        self.login_root.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(self.login_root, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="System Login", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(pady=20)

        ttk.Label(main_frame, text="User ID:").pack(pady=5, anchor='w')
        self.username_entry = ttk.Entry(main_frame, width=35)
        self.username_entry.pack()
        self.username_entry.insert(0, "admin") # Default for easy testing
        self.username_entry.focus_set()

        ttk.Label(main_frame, text="Password:").pack(pady=5, anchor='w')
        self.password_entry = ttk.Entry(main_frame, width=35, show="*")
        self.password_entry.pack()
        self.password_entry.insert(0, "admin") # Default for easy testing        ttk.Button(main_frame, text="Login", command=self.authenticate, bootstyle="success").pack(pady=20, fill='x')
        
        # Additional options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(pady=10)
        
        ttk.Button(options_frame, text="Register New User", command=self.open_register, bootstyle="info-outline").pack(side="left", padx=5)
        ttk.Button(options_frame, text="Forgot Password", command=self.open_forgot_password, bootstyle="warning-outline").pack(side="right", padx=5)
        
        # Bind Enter key to login
        self.login_root.bind('<Return>', lambda event=None: self.authenticate())

    def open_register(self):
        """Open the registration window."""
        self.login_root.withdraw()
        RegistrationWindow(self.master, self)
        
    def open_forgot_password(self):
        """Open the forgot password window."""
        self.login_root.withdraw()
        ForgotPasswordWindow(self.master, self)

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_pw = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=? AND password_hash=?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.login_root.destroy()
            MainApplication(self.master) # Launch main app
        else:
            messagebox.showerror("Login Failed", "Invalid User ID or password.", parent=self.login_root)

class RegistrationWindow:
    def __init__(self, master, login_window_instance):
        self.master = master
        self.login_window_instance = login_window_instance
        master.withdraw()
        self.reg_root = tk.Toplevel(master)
        self.reg_root.title("Register New User")
        self.reg_root.geometry("450x500")
        self.reg_root.resizable(False, False)
        # Fixed: Removed overrideredirect(True) to allow proper iconify/minimize functionality
        # self.reg_root.overrideredirect(True)

        self.style = Style(theme="superhero")
        # Using standard window decorations instead of custom title bar to avoid iconify errors
        # self.title_bar = CustomTitleBar(self.reg_root, "Register New User", self.style)

        self.reg_root.update_idletasks()
        x = self.reg_root.winfo_screenwidth() // 2 - self.reg_root.winfo_width() // 2
        y = self.reg_root.winfo_screenheight() // 2 - self.reg_root.winfo_height() // 2
        self.reg_root.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.reg_root.protocol("WM_DELETE_WINDOW", self.on_reg_window_close)

    def create_widgets(self):
        main_frame = ttk.Frame(self.reg_root, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="New User Registration", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=20)

        ttk.Label(main_frame, text="Full Name:", font=("Helvetica", 12)).pack(pady=(10, 5))
        self.fullname_entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
        self.fullname_entry.pack(pady=5)
        self.fullname_entry.focus_set()

        ttk.Label(main_frame, text="User ID:", font=("Helvetica", 12)).pack(pady=(10, 5))
        self.userid_entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
        self.userid_entry.pack(pady=5)

        ttk.Label(main_frame, text="Password:", font=("Helvetica", 12)).pack(pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.password_entry.pack(pady=5)

        ttk.Label(main_frame, text="Confirm Password:", font=("Helvetica", 12)).pack(pady=5)
        self.confirm_password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.confirm_password_entry.pack(pady=5)

        register_button = ttk.Button(main_frame, text="Register", command=self.register_user, bootstyle="success")
        register_button.pack(pady=20)

        back_button = ttk.Button(main_frame, text="Back to Login", command=self.on_reg_window_close, bootstyle="secondary")
        back_button.pack(pady=5)

        self.reg_root.bind('<Return>', lambda event=None: self.register_user())

    def register_user(self):
        fullname = self.fullname_entry.get().strip()
        username = self.userid_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not fullname or not username or not password or not confirm_password:
            messagebox.showwarning("Input Error", "All fields are required.", parent=self.reg_root)
            return
            
        if password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match.", parent=self.reg_root)
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id=?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Registration Failed", "User ID already exists. Please choose a different one.", parent=self.reg_root)
                conn.close()
                return
            hashed_pw = hash_password(password)
            cursor.execute("INSERT INTO users (user_id, password_hash, name, role) VALUES (?, ?, ?, ?)", 
                          (username, hashed_pw, fullname, 'student'))
            conn.commit()
            messagebox.showinfo("Registration Successful", f"User '{fullname}' registered successfully! You can now log in.", parent=self.reg_root)
            self.on_reg_window_close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during registration: {e}", parent=self.reg_root)
        finally:
            if conn:
                conn.close()

    def on_reg_window_close(self):
        self.reg_root.destroy()
        self.login_window_instance.login_root.deiconify()

# --- Password Update Window ---
class PasswordUpdateWindow:
    def __init__(self, master, login_window_instance):
        self.master = master
        self.login_window_instance = login_window_instance
        master.withdraw()
        self.update_root = tk.Toplevel(master)
        self.update_root.title("Update Password")
        self.update_root.geometry("400x350")
        self.update_root.resizable(False, False)
        # Fixed: Removed overrideredirect(True) to allow proper iconify/minimize functionality
        # self.update_root.overrideredirect(True)

        self.style = Style(theme="superhero")
        # Using standard window decorations instead of custom title bar to avoid iconify errors
        # self.title_bar = CustomTitleBar(self.update_root, "Update Password", self.style)

        self.update_root.update_idletasks()
        x = self.update_root.winfo_screenwidth() // 2 - self.update_root.winfo_width() // 2
        y = self.update_root.winfo_screenheight() // 2 - self.update_root.winfo_height() // 2
        self.update_root.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.update_root.protocol("WM_DELETE_WINDOW", self.on_update_window_close)

    def create_widgets(self):
        main_frame = ttk.Frame(self.update_root, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Update Password", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=20)

        ttk.Label(main_frame, text="User ID:", font=("Helvetica", 12)).pack(pady=(10, 5))
        self.userid_entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
        self.userid_entry.pack(pady=5)
        self.userid_entry.focus_set()

        ttk.Label(main_frame, text="Old Password:", font=("Helvetica", 12)).pack(pady=5)
        self.old_password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.old_password_entry.pack(pady=5)

        ttk.Label(main_frame, text="New Password:", font=("Helvetica", 12)).pack(pady=5)
        self.new_password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.new_password_entry.pack(pady=5)

        ttk.Label(main_frame, text="Confirm New Password:", font=("Helvetica", 12)).pack(pady=5)
        self.confirm_new_password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.confirm_new_password_entry.pack(pady=5)

        update_button = ttk.Button(main_frame, text="Update Password", command=self.update_password, bootstyle="success")
        update_button.pack(pady=20)

        back_button = ttk.Button(main_frame, text="Back to Login", command=self.on_update_window_close, bootstyle="secondary")
        back_button.pack(pady=5)

        self.update_root.bind('<Return>', lambda event=None: self.update_password())

    def update_password(self):
        username = self.userid_entry.get().strip()
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_new_password = self.confirm_new_password_entry.get().strip()

        if not username or not old_password or not new_password or not confirm_new_password:
            messagebox.showwarning("Input Error", "All fields are required.", parent=self.update_root)
            return

        if new_password != confirm_new_password:
            messagebox.showerror("Password Mismatch", "New passwords do not match.", parent=self.update_root)
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            row = cursor.fetchone()
            if not row or hash_password(old_password) != row[0]:
                messagebox.showerror("Authentication Failed", "User ID or old password is incorrect.", parent=self.update_root)
                return
            cursor.execute("UPDATE users SET password=? WHERE username=?", (hash_password(new_password), username))
            conn.commit()
            messagebox.showinfo("Password Updated", "Password updated successfully! Please login with your new password.", parent=self.update_root)
            self.on_update_window_close()
        except sqlite3.Error as e:            messagebox.showerror("Database Error", f"An error occurred: {e}", parent=self.update_root)
        finally:
            if conn:
                conn.close()
                
    def on_update_window_close(self):
        self.update_root.destroy()
        self.login_window_instance.login_root.deiconify()

# --- Forgot Password Window ---
class ForgotPasswordWindow:
    def __init__(self, master, login_window_instance):
        self.master = master
        self.login_window_instance = login_window_instance
        master.withdraw()
        self.forgot_root = tk.Toplevel(master)
        self.forgot_root.title("Forgot Password")
        self.forgot_root.geometry("450x400")
        self.forgot_root.resizable(False, False)
        # Fixed: Removed overrideredirect(True) to allow proper iconify/minimize functionality
        # self.forgot_root.overrideredirect(True)

        self.style = Style(theme="superhero")
        # Using standard window decorations instead of custom title bar to avoid iconify errors
        # self.title_bar = CustomTitleBar(self.forgot_root, "Password Recovery", self.style)

        self.forgot_root.update_idletasks()
        x = self.forgot_root.winfo_screenwidth() // 2 - self.forgot_root.winfo_width() // 2
        y = self.forgot_root.winfo_screenheight() // 2 - self.forgot_root.winfo_height() // 2
        self.forgot_root.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.forgot_root.protocol("WM_DELETE_WINDOW", self.on_forgot_window_close)

    def create_widgets(self):
        main_frame = ttk.Frame(self.forgot_root, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Password Recovery", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=20)
        ttk.Label(main_frame, text="Enter your User ID to reset password", font=("Helvetica", 10)).pack(pady=(0, 20))

        ttk.Label(main_frame, text="User ID:", font=("Helvetica", 12)).pack(pady=(10, 5))
        self.userid_entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
        self.userid_entry.pack(pady=5)
        self.userid_entry.focus_set()

        ttk.Label(main_frame, text="New Password:", font=("Helvetica", 12)).pack(pady=(15, 5))
        self.new_password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.new_password_entry.pack(pady=5)

        ttk.Label(main_frame, text="Confirm New Password:", font=("Helvetica", 12)).pack(pady=(10, 5))
        self.confirm_password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Helvetica", 12))
        self.confirm_password_entry.pack(pady=5)

        # Security question section
        ttk.Label(main_frame, text="Security Verification:", font=("Helvetica", 12, "bold")).pack(pady=(20, 10))
        ttk.Label(main_frame, text="What is 5 + 3? (Enter the number)", font=("Helvetica", 10)).pack(pady=5)
        self.security_entry = ttk.Entry(main_frame, width=10, font=("Helvetica", 12))
        self.security_entry.pack(pady=5)

        reset_button = ttk.Button(main_frame, text="Reset Password", command=self.reset_password, bootstyle="success")
        reset_button.pack(pady=20)

        back_button = ttk.Button(main_frame, text="Back to Login", command=self.on_forgot_window_close, bootstyle="secondary")
        back_button.pack(pady=5)

        self.forgot_root.bind('<Return>', lambda event=None: self.reset_password())

    def reset_password(self):
        username = self.userid_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        security_answer = self.security_entry.get().strip()

        if not username or not new_password or not confirm_password or not security_answer:
            messagebox.showwarning("Input Error", "All fields are required.", parent=self.forgot_root)
            return

        # Simple security check
        if security_answer != "8":
            messagebox.showerror("Security Check Failed", "Incorrect security answer. Please try again.", parent=self.forgot_root)
            return

        if new_password != confirm_password:
            messagebox.showerror("Password Mismatch", "New passwords do not match.", parent=self.forgot_root)
            return

        if len(new_password) < 4:
            messagebox.showwarning("Password Too Short", "Password must be at least 4 characters long.", parent=self.forgot_root)
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id=?", (username,))
            user = cursor.fetchone()
            if not user:
                messagebox.showerror("User Not Found", "User ID does not exist in the system.", parent=self.forgot_root)
                return

            # Update password
            hashed_pw = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash=? WHERE user_id=?", (hashed_pw, username))
            conn.commit()
            messagebox.showinfo("Password Reset Successful", "Password has been reset successfully! You can now log in with your new password.", parent=self.forgot_root)
            self.on_forgot_window_close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}", parent=self.forgot_root)
        finally:
            if conn:
                conn.close()

    def on_forgot_window_close(self):
        self.forgot_root.destroy()
        self.login_window_instance.login_root.deiconify()

# --- Main Application Class ---
class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.deiconify()
        self.master.title("Student Database Management System")
        self.master.geometry("1366x768")
        self.master.minsize(1024, 600)
        # Fixed: Remove overrideredirect to allow normal window operations like minimize/maximize
        # self.master.overrideredirect(True)  # This prevents iconify() from working

        self.style = Style(theme="superhero")  # This now works!
        # Use standard window decorations instead of custom title bar to avoid iconify issues
        # self.title_bar = CustomTitleBar(self.master, "Student Database Management System", self.style)

        # Center the window
        self.master.update_idletasks()
        x = self.master.winfo_screenwidth() // 2 - self.master.winfo_width() // 2
        y = self.master.winfo_screenheight() // 2 - self.master.winfo_height() // 2
        self.master.geometry(f"+{x}+{y}")

        # Load images
        self.logo_img = load_image(LOGO_PATH, size=(64, 64))
        self.banner_img = load_image(COLLEGE_BANNER_PATH, size=(800, 200))

        self.create_main_widgets()

    def create_main_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(expand=True, fill="both")

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Define tabs
        tabs = {
            "🏠 Home": self.setup_home_tab,
            "🎓 Student Management": self.setup_student_management_tab,
            "📊 Reporting & Export": self.setup_reports_tab,
            "📈 Analytics & Insights": self.setup_analytics_tab,
            "💳 ID Card Generation": self.setup_id_card_tab,
            "🧾 Receipt Generation": self.setup_receipt_tab,
            "💬 Communications": self.setup_communications_tab,
            "Marks Entry": self.setup_marks_entry_tab,  # Add Marks Entry tab here
        }

        for text, setup_func in tabs.items():
            frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=text)
            setup_func(frame)
            
    def setup_marks_entry_tab(self, parent_frame):
        """Marks Entry: Add and view marks for students."""
        ttk.Label(parent_frame, text="Marks Entry", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
    
        input_frame = ttk.LabelFrame(parent_frame, text="Enter Marks", padding=10, bootstyle="info")
        input_frame.pack(pady=10, padx=10, fill="x", expand=False)
    
        ttk.Label(input_frame, text="Student Roll Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.marks_roll_entry = ttk.Entry(input_frame, width=25)
        self.marks_roll_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
        ttk.Label(input_frame, text="Course:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.marks_course_combobox = ttk.Combobox(input_frame, values=self._get_course_names(), width=20)
        self.marks_course_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
    
        ttk.Label(input_frame, text="Semester:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.marks_semester_entry = ttk.Entry(input_frame, width=25)
        self.marks_semester_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
        ttk.Label(input_frame, text="Subject Name:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.marks_subject_entry = ttk.Entry(input_frame, width=20)
        self.marks_subject_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
    
        ttk.Label(input_frame, text="Marks Obtained:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.marks_obtained_entry = ttk.Entry(input_frame, width=25)
        self.marks_obtained_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    
        ttk.Label(input_frame, text="Max Marks:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.marks_max_entry = ttk.Entry(input_frame, width=20)
        self.marks_max_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
    
        ttk.Label(input_frame, text="Grade:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.marks_grade_entry = ttk.Entry(input_frame, width=25)
        self.marks_grade_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    
        ttk.Button(input_frame, text="Add Marks", command=self.add_marks, bootstyle="success").grid(row=4, column=0, columnspan=4, pady=10)
    
        # Marks Display
        display_frame = ttk.LabelFrame(parent_frame, text="Student Marks", padding=10, bootstyle="primary")
        display_frame.pack(pady=10, padx=10, fill="both", expand=True)
    
        self.marks_tree = ttk.Treeview(display_frame, columns=("Subject", "Semester", "Marks", "Max", "Grade"), show="headings")
        for col in self.marks_tree["columns"]:
            self.marks_tree.heading(col, text=col)
            self.marks_tree.column(col, width=100, anchor="center")
        self.marks_tree.pack(fill="both", expand=True)
    
        ttk.Button(display_frame, text="Show Marks", command=self.display_student_marks, bootstyle="info").pack(pady=5)

    def _get_course_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in cursor.fetchall()]
        conn.close()
        return courses

    def add_marks(self):
        roll = self.marks_roll_entry.get().strip()
        course = self.marks_course_combobox.get().strip()
        semester = self.marks_semester_entry.get().strip()
        subject = self.marks_subject_entry.get().strip()
        marks = self.marks_obtained_entry.get().strip()
        max_marks = self.marks_max_entry.get().strip()
        grade = self.marks_grade_entry.get().strip()
    
        if not all([roll, course, semester, subject, marks, max_marks, grade]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return
    
        try:
            semester = int(semester)
            marks = float(marks)
            max_marks = float(max_marks)
        except ValueError:
            messagebox.showerror("Input Error", "Semester, Marks, and Max Marks must be numbers.")
            return
    
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll,))
            student = cursor.fetchone()
            if not student:
                messagebox.showerror("Error", "Student not found.")
                return
            student_id = student[0]
    
            cursor.execute("SELECT course_id FROM courses WHERE course_name=?", (course,))
            course_row = cursor.fetchone()
            if not course_row:
                messagebox.showerror("Error", "Course not found.")
                return
            course_id = course_row[0]
    
            cursor.execute(
                "INSERT INTO marks (student_id, course_id, subject_name, semester, marks_obtained, max_marks, grade) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (student_id, course_id, subject, semester, marks, max_marks, grade)
            )
            conn.commit()
            messagebox.showinfo("Success", "Marks added successfully!")
            self.display_student_marks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add marks: {e}")
        finally:
            conn.close()
    
    def display_student_marks(self):
        roll = self.marks_roll_entry.get().strip()
        for item in self.marks_tree.get_children():
            self.marks_tree.delete(item)
        if not roll:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.subject_name, m.semester, m.marks_obtained, m.max_marks, m.grade
            FROM marks m
            JOIN students s ON m.student_id = s.student_id
            WHERE s.roll_number = ?
            ORDER BY m.semester, m.subject_name
        """, (roll,))
        for row in cursor.fetchall():
            self.marks_tree.insert("", "end", values=row)
        conn.close()
            
    # ============================================================================
    # --------------------------------- HOME TAB ---------------------------------
    # ============================================================================
    def setup_home_tab(self, parent_frame):
        """Dashboard: Shows quick stats and a pie chart of student distribution."""
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # --- Header ---
        header_frame = ttk.Frame(parent_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=10)
        if self.logo_img:
            ttk.Label(header_frame, image=self.logo_img).pack(side="left", padx=10)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(title_frame, text="Welcome to the Dashboard", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(anchor='w')
        ttk.Label(title_frame, text="Your central hub for student data management and insights.", font=("Helvetica", 12)).pack(anchor='w')

        # --- Main Content Area ---
        content_frame = ttk.Frame(parent_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # --- Quick Stats Cards ---
        stats_frame = ttk.Frame(content_frame, padding=10)
        stats_frame.grid(row=0, column=0, sticky="ns", padx=10)
        ttk.Label(stats_frame, text="Quick Statistics", font=("Helvetica", 14, "bold"), bootstyle="info").pack(pady=(0, 10), anchor='w')

        conn = get_db_connection()
        total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        active_courses = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        total_revenue = conn.execute("SELECT SUM(amount_paid) FROM payments").fetchone()[0] or 0
        conn.close()

        self._create_stat_card(stats_frame, "Total Students", f"{total_students}", "primary")
        self._create_stat_card(stats_frame, "Active Courses", f"{active_courses}", "success")
        self._create_stat_card(stats_frame, "Total Revenue (INR)", f"{total_revenue:,.2f}", "warning")
        
        # --- Charts / Visuals Frame ---
        chart_frame = ttk.LabelFrame(content_frame, text="Analytics Snapshot", padding=15, bootstyle="info")
        chart_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        self.create_faculty_pie_chart(chart_frame)

        # --- Footer ---
        footer_label = ttk.Label(parent_frame, text="@developed by Rushikesh Atole and Team", font=("Helvetica", 10, "italic"), bootstyle="secondary")
        footer_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)

    def _create_stat_card(self, parent, title, value, bootstyle):
        card = ttk.Frame(parent, padding=15, bootstyle=bootstyle)
        card.pack(fill="x", pady=5)
        ttk.Label(card, text=title, font=("Helvetica", 11, "bold"), bootstyle=f"inverse-{bootstyle}").pack(anchor='w')
        ttk.Label(card, text=value, font=("Helvetica", 20, "bold"), bootstyle=f"inverse-{bootstyle}").pack(anchor='w')

    def create_faculty_pie_chart(self, parent_frame):
        """Creates and embeds a pie chart showing students per faculty."""
        try:
            conn = get_db_connection()
            query = """
                SELECT f.faculty_name, COUNT(s.student_id)
                FROM faculties f
                LEFT JOIN courses c ON f.faculty_id = c.faculty_id
                LEFT JOIN students s ON c.course_id = s.course_id
                GROUP BY f.faculty_name
                HAVING COUNT(s.student_id) > 0;
            """
            data = conn.execute(query).fetchall()
            conn.close()

            labels = [row['faculty_name'] for row in data]
            sizes = [row[1] for row in data]

            if not labels:
                ttk.Label(parent_frame, text="No student data to display chart.").pack()
                return

            fig = Figure(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor(self.style.colors.bg)
            ax = fig.add_subplot(111)
            ax.set_title("Student Distribution by Faculty", color=self.style.colors.fg)
            
            wedges, texts, autotexts = ax.pie(
                sizes, autopct='%1.1f%%', startangle=90,
                textprops=dict(color=self.style.colors.fg)
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            
            # Create legend
            ax.legend(wedges, labels, title="Faculties", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                      facecolor=self.style.colors.light,
                      labelcolor=self.style.colors.fg)
            
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except Exception as e:
            ttk.Label(parent_frame, text=f"Could not load chart: {e}").pack()
    # ============================================================================
    # --------------------------- STUDENT MGMT TAB -------------------------------
    # ============================================================================
    def setup_student_management_tab(self, parent_frame):
        """Complete CRUD interface for student management."""
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # Header
        ttk.Label(parent_frame, text="Student Record Management", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)

        # Main container with two frames: input and display
        main_container = ttk.Frame(parent_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # === INPUT FORM ===
        input_frame = ttk.LabelFrame(main_container, text="Student Information", padding=15, bootstyle="info")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure((1, 3, 5), weight=1)

        # Row 1
        ttk.Label(input_frame, text="Roll Number*:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.roll_entry = ttk.Entry(input_frame, width=20)
        self.roll_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Full Name*:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=25)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Email:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(input_frame, width=25)
        self.email_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        # Row 2
        ttk.Label(input_frame, text="Contact Number:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.contact_entry = ttk.Entry(input_frame, width=20)
        self.contact_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Date of Birth:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.dob_entry = ttk.Entry(input_frame, width=20)
        self.dob_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(input_frame, text="(YYYY-MM-DD)", font=("Helvetica", 8)).grid(row=1, column=3, padx=5, pady=(25, 0), sticky="w")

        ttk.Label(input_frame, text="Gender:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.gender_combo = ttk.Combobox(input_frame, values=["Male", "Female", "Other"], width=15)
        self.gender_combo.grid(row=1, column=5, padx=5, pady=5, sticky="ew")

        # Row 3
        ttk.Label(input_frame, text="Aadhaar Number:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.aadhaar_entry = ttk.Entry(input_frame, width=20)
        self.aadhaar_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Blood Group:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.blood_combo = ttk.Combobox(input_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], width=15)
        self.blood_combo.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Mother's Name:").grid(row=2, column=4, padx=5, pady=5, sticky="w")
        self.mother_entry = ttk.Entry(input_frame, width=25)
        self.mother_entry.grid(row=2, column=5, padx=5, pady=5, sticky="ew")

        # Row 4
        ttk.Label(input_frame, text="10th %:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.tenth_entry = ttk.Entry(input_frame, width=15)
        self.tenth_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="12th %:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.twelfth_entry = ttk.Entry(input_frame, width=15)
        self.twelfth_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Course*:").grid(row=3, column=4, padx=5, pady=5, sticky="w")
        self.course_combo = ttk.Combobox(input_frame, values=self._get_course_names(), width=20)
        self.course_combo.grid(row=3, column=5, padx=5, pady=5, sticky="ew")

        # Row 5
        ttk.Label(input_frame, text="Academic Year*:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.year_combo = ttk.Combobox(input_frame, values=self._get_academic_years(), width=20)
        self.year_combo.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Enrollment Status:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.status_combo = ttk.Combobox(input_frame, values=["Active", "Inactive"], width=15)
        self.status_combo.grid(row=4, column=3, padx=5, pady=5, sticky="ew")
        self.status_combo.set("Active")        # Row 6 - Address (spanning multiple columns)
        ttk.Label(input_frame, text="Address:").grid(row=5, column=0, padx=5, pady=5, sticky="nw")
        self.address_text = tk.Text(input_frame, height=3, width=60)
        self.address_text.grid(row=5, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Row 7 - Profile Picture Section
        ttk.Label(input_frame, text="Profile Picture:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        
        # Profile picture frame
        pic_frame = ttk.Frame(input_frame)
        pic_frame.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.profile_pic_path = tk.StringVar()
        self.profile_pic_label = ttk.Label(pic_frame, text="No file selected", foreground="gray")
        self.profile_pic_label.pack(side='left', fill='x', expand=True)
        
        upload_btn = ttk.Button(pic_frame, text="📁 Upload", command=self.upload_profile_picture, bootstyle="info")
        upload_btn.pack(side='right', padx=(5, 0))

        # Print and Export buttons
        utility_frame = ttk.Frame(input_frame)
        utility_frame.grid(row=6, column=3, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Button(utility_frame, text="🖨️ Print Record", command=self.print_student_record, bootstyle="primary").pack(side='left', padx=2)
        ttk.Button(utility_frame, text="📄 Export Data", command=self.export_student_data, bootstyle="warning").pack(side='left', padx=2)
        ttk.Button(utility_frame, text="🖼️ View Photo", command=self.view_profile_picture, bootstyle="info-outline").pack(side='left', padx=2)

        # === ACTION BUTTONS ===
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=7, column=0, columnspan=6, pady=15)

        ttk.Button(button_frame, text="Add Student", command=self.add_student, bootstyle="success").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Student", command=self.update_student, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Student", command=self.delete_student, bootstyle="danger").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_student_form, bootstyle="secondary").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Search Student", command=self.search_student, bootstyle="info").pack(side="left", padx=5)

        # === SEARCH SECTION ===
        search_frame = ttk.LabelFrame(main_container, text="Search Students", padding=10, bootstyle="warning")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(search_frame, text="Search by:").pack(side="left", padx=5)
        self.search_criteria = ttk.Combobox(search_frame, values=["Name", "Roll Number", "Course", "Email"], width=15)
        self.search_criteria.pack(side="left", padx=5)
        self.search_criteria.set("Name")

        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        ttk.Button(search_frame, text="Show All", command=self.load_all_students, bootstyle="info").pack(side="right", padx=5)

        # === STUDENT LIST DISPLAY ===
        list_frame = ttk.LabelFrame(main_container, text="Student Records", padding=10, bootstyle="primary")
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview with scrollbars
        self.students_tree = ttk.Treeview(list_frame, 
                                         columns=("Roll", "Name", "Course", "Year", "Email", "Contact", "Status"), 
                                         show="headings", 
                                         bootstyle="primary")

        # Configure column headings and widths
        columns_config = {
            "Roll": ("Roll No", 100),
            "Name": ("Full Name", 180),
            "Course": ("Course", 150),
            "Year": ("Academic Year", 120),
            "Email": ("Email", 200),
            "Contact": ("Contact", 120),
            "Status": ("Status", 80)
        }

        for col, (heading, width) in columns_config.items():
            self.students_tree.heading(col, text=heading)
            self.students_tree.column(col, width=width, anchor="w")

        self.students_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.students_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.students_tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.students_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.students_tree.configure(xscrollcommand=h_scrollbar.set)        # Bind double-click to load student data
        self.students_tree.bind("<Double-1>", self.on_student_select)

        # Load all students initially
        self.load_all_students()

    def _get_academic_years(self):
        """Get list of academic years from database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT year_name FROM academic_years")
        years = [row[0] for row in cursor.fetchall()]
        conn.close()
        return years

    def upload_profile_picture(self):
        """Enhanced profile picture upload with validation"""
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Validate image
                img = Image.open(file_path)
                
                # Create profile pictures directory
                profile_pics_dir = os.path.join(os.path.dirname(__file__), "profile_pictures")
                os.makedirs(profile_pics_dir, exist_ok=True)
                
                # Generate unique filename
                import uuid
                file_extension = os.path.splitext(file_path)[1]
                new_filename = f"profile_{uuid.uuid4().hex[:8]}{file_extension}"
                new_path = os.path.join(profile_pics_dir, new_filename)
                
                # Resize and save image
                img_resized = img.resize((150, 150), Image.Resampling.LANCZOS)
                img_resized.save(new_path, quality=90)
                
                # Update UI
                self.profile_pic_path.set(new_path)
                self.profile_pic_label.config(text=f"✅ {os.path.basename(new_path)}", foreground="green")
                
                messagebox.showinfo("Success", "Profile picture uploaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {e}")

    def view_profile_picture(self):
        """View profile picture of selected student"""
        selected = self.students_tree.selection()
        if not selected:
            if hasattr(self, 'profile_pic_path') and self.profile_pic_path.get():
                self._show_profile_picture(self.profile_pic_path.get())
            else:
                messagebox.showwarning("No Selection", "Please select a student or upload a profile picture first.")
            return
            
        # Get profile picture path from selected student
        # This would need to be implemented based on your data structure
        messagebox.showinfo("Info", "Profile picture viewing functionality will be implemented when student is selected.")

    def _show_profile_picture(self, pic_path):
        """Display profile picture in popup"""
        if not os.path.exists(pic_path):
            messagebox.showerror("Error", "Profile picture file not found.")
            return
            
        try:
            # Create popup window
            pic_window = tk.Toplevel(self.root)
            pic_window.title("Profile Picture")
            pic_window.geometry("300x350")
            pic_window.resizable(False, False)
            
            # Load and display image
            img = Image.open(pic_path)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            label = ttk.Label(pic_window, image=photo)
            label.image = photo  # Keep reference
            label.pack(pady=10)
            
            # Close button
            ttk.Button(pic_window, text="Close", command=pic_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {e}")

    def print_student_record(self):
        """Print selected student record"""
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student record to print.")
            return
        
        try:
            # Get selected student data
            item = self.students_tree.item(selected[0])
            values = item['values']
            
            # Create a simple print dialog or export to PDF
            messagebox.showinfo("Print", f"Print functionality for student: {values[1]}\nThis would generate a PDF report.")
            # TODO: Implement actual PDF generation using reportlab
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print record: {e}")

    def export_student_data(self):
        """Export selected student data to CSV"""
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select student(s) to export.")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Roll No', 'Name', 'Course', 'Year', 'Email', 'Contact', 'Status']
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                
                for item in selected:
                    values = self.students_tree.item(item)['values']
                    writer.writerow(values)
                        
            messagebox.showinfo("Export Complete", f"Data exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def add_student(self):
        """Add a new student to the database."""
        if not self._validate_student_form():
            return

        student_data = self._get_form_data()
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if roll number already exists
            cursor.execute("SELECT roll_number FROM students WHERE roll_number=?", (student_data['roll_number'],))
            if cursor.fetchone():
                messagebox.showerror("Duplicate Entry", "A student with this roll number already exists.")
                return

            # Get course_id and year_id
            cursor.execute("SELECT course_id FROM courses WHERE course_name=?", (student_data['course'],))
            course_row = cursor.fetchone()
            if not course_row:
                messagebox.showerror("Error", "Selected course not found.")
                return
            course_id = course_row[0]

            cursor.execute("SELECT year_id FROM academic_years WHERE year_name=?", (student_data['academic_year'],))
            year_row = cursor.fetchone()
            if not year_row:
                messagebox.showerror("Error", "Selected academic year not found.")
                return
            year_id = year_row[0]

            # Insert new student
            cursor.execute("""
                INSERT INTO students (roll_number, name, contact_number, email, address, aadhaar_no, 
                                    date_of_birth, gender, tenth_percent, twelfth_percent, blood_group, 
                                    mother_name, enrollment_status, enrollment_date, course_id, academic_year_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_data['roll_number'], student_data['name'], student_data['contact_number'],
                student_data['email'], student_data['address'], student_data['aadhaar_no'],
                student_data['date_of_birth'], student_data['gender'], student_data['tenth_percent'],
                student_data['twelfth_percent'], student_data['blood_group'], student_data['mother_name'],
                1 if student_data['enrollment_status'] == 'Active' else 0,
                datetime.now().strftime("%Y-%m-%d"), course_id, year_id
            ))
            
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.clear_student_form()
            self.load_all_students()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add student: {e}")
        finally:
            conn.close()

    def update_student(self):
        """Update existing student data."""
        roll_number = self.roll_entry.get().strip()
        if not roll_number:
            messagebox.showwarning("Selection Error", "Please enter a roll number to update.")
            return

        if not self._validate_student_form():
            return

        student_data = self._get_form_data()
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if student exists
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
            student_row = cursor.fetchone()
            if not student_row:
                messagebox.showerror("Error", "Student with this roll number not found.")
                return

            # Get course_id and year_id
            cursor.execute("SELECT course_id FROM courses WHERE course_name=?", (student_data['course'],))
            course_id = cursor.fetchone()[0]

            cursor.execute("SELECT year_id FROM academic_years WHERE year_name=?", (student_data['academic_year'],))
            year_id = cursor.fetchone()[0]

            # Update student
            cursor.execute("""
                UPDATE students SET name=?, contact_number=?, email=?, address=?, aadhaar_no=?, 
                                  date_of_birth=?, gender=?, tenth_percent=?, twelfth_percent=?, 
                                  blood_group=?, mother_name=?, enrollment_status=?, course_id=?, academic_year_id=?
                WHERE roll_number=?
            """, (
                student_data['name'], student_data['contact_number'], student_data['email'],
                student_data['address'], student_data['aadhaar_no'], student_data['date_of_birth'],
                student_data['gender'], student_data['tenth_percent'], student_data['twelfth_percent'],
                student_data['blood_group'], student_data['mother_name'],
                1 if student_data['enrollment_status'] == 'Active' else 0,
                course_id, year_id, roll_number
            ))
            
            conn.commit()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.load_all_students()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update student: {e}")
        finally:
            conn.close()

    def delete_student(self):
        """Delete selected student."""
        roll_number = self.roll_entry.get().strip()
        if not roll_number:
            messagebox.showwarning("Selection Error", "Please enter a roll number to delete.")
            return

        result = messagebox.askyesno("Confirm Deletion", 
                                   f"Are you sure you want to delete student with roll number '{roll_number}'?\n"
                                   "This will also remove all associated marks and payment records.")
        if not result:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Student with this roll number not found.")
                return

            cursor.execute("DELETE FROM students WHERE roll_number=?", (roll_number,))
            conn.commit()
            
            messagebox.showinfo("Success", "Student deleted successfully!")
            self.clear_student_form()
            self.load_all_students()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete student: {e}")
        finally:
            conn.close()

    def search_student(self):
        """Search for a specific student and load their data."""
        roll_number = self.roll_entry.get().strip()
        if not roll_number:
            messagebox.showwarning("Input Error", "Please enter a roll number to search.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, c.course_name, ay.year_name 
                FROM students s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                WHERE s.roll_number=?
            """, (roll_number,))
            
            student = cursor.fetchone()
            if not student:
                messagebox.showinfo("Not Found", "No student found with this roll number.")
                return            # Populate form with student data
            self._populate_form_with_student(student)
            messagebox.showinfo("Found", f"Student '{student['name']}' loaded successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to search student: {e}")
        finally:
            conn.close()

    def clear_student_form(self):
        """Clear all form fields."""
        entries = [self.roll_entry, self.name_entry, self.email_entry, self.contact_entry,
                  self.dob_entry, self.aadhaar_entry, self.mother_entry, self.tenth_entry, self.twelfth_entry]
        
        for entry in entries:
            entry.delete(0, tk.END)
            
        combos = [self.gender_combo, self.blood_combo, self.course_combo, self.year_combo, self.status_combo]
        for combo in combos:
            combo.set("")
            
        self.address_text.delete("1.0", tk.END)
        self.status_combo.set("Active")  # Default status

    def load_all_students(self):
        """Load all students into the treeview."""
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.roll_number, s.name, c.course_name, ay.year_name, s.email, s.contact_number,
                       CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END as status
                FROM students s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                ORDER BY s.name
            """)
            
            for row in cursor.fetchall():
                # Extract individual values from the Row object
                values = [
                    row[0],  # roll_number
                    row[1],  # name
                    row[2],  # course_name
                    row[3],  # year_name
                    row[4],  # email
                    row[5],  # contact_number
                    row[6]   # status
                ]
                self.students_tree.insert("", "end", values=values)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")
        finally:
            conn.close()

    def on_search_change(self, event):
        """Handle real-time search as user types."""
        search_term = self.search_entry.get().strip()
        criteria = self.search_criteria.get()
        
        if not search_term:
            self.load_all_students()
            return

        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if criteria == "Name":
                query = """
                    SELECT s.roll_number, s.name, c.course_name, ay.year_name, s.email, s.contact_number,
                           CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END as status
                    FROM students s
                    LEFT JOIN courses c ON s.course_id = c.course_id
                    LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                    WHERE s.name LIKE ?
                    ORDER BY s.name
                """
                cursor.execute(query, (f"%{search_term}%",))
            elif criteria == "Roll Number":
                query = """
                    SELECT s.roll_number, s.name, c.course_name, ay.year_name, s.email, s.contact_number,
                           CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END as status
                    FROM students s
                    LEFT JOIN courses c ON s.course_id = c.course_id
                    LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                    WHERE s.roll_number LIKE ?
                    ORDER BY s.name
                """
                cursor.execute(query, (f"%{search_term}%",))
            elif criteria == "Course":
                query = """
                    SELECT s.roll_number, s.name, c.course_name, ay.year_name, s.email, s.contact_number,
                           CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END as status
                    FROM students s
                    LEFT JOIN courses c ON s.course_id = c.course_id
                    LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                    WHERE c.course_name LIKE ?
                    ORDER BY s.name
                """
                cursor.execute(query, (f"%{search_term}%",))
            elif criteria == "Email":
                query = """                    SELECT s.roll_number, s.name, c.course_name, ay.year_name, s.email, s.contact_number,
                           CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END as status
                    FROM students s
                    LEFT JOIN courses c ON s.course_id = c.course_id
                    LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                    WHERE s.email LIKE ?
                    ORDER BY s.name
                """
                cursor.execute(query, (f"%{search_term}%",))
            
            for row in cursor.fetchall():
                # Extract individual values from the Row object
                values = [
                    row[0],  # roll_number
                    row[1],  # name
                    row[2],  # course_name
                    row[3],  # year_name
                    row[4],  # email
                    row[5],  # contact_number
                    row[6]   # status
                ]
                self.students_tree.insert("", "end", values=values)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to search students: {e}")
        finally:
            conn.close()

    def on_student_select(self, event):
        """Handle double-click on student row to load data into form."""
        selection = self.students_tree.selection()
        if not selection:
            return

        item = self.students_tree.item(selection[0])
        roll_number = item['values'][0]
        
        # Load student data into form
        self.roll_entry.delete(0, tk.END)
        self.roll_entry.insert(0, roll_number)
        self.search_student()

    def _validate_student_form(self):
        """Validate required form fields."""
        required_fields = {
            'Roll Number': self.roll_entry.get().strip(),
            'Name': self.name_entry.get().strip(),
            'Course': self.course_combo.get().strip(),
            'Academic Year': self.year_combo.get().strip(),
        }
        
        for field_name, value in required_fields.items():
            if not value:
                messagebox.showwarning("Validation Error", f"{field_name} is required.")
                return False
                
        # Validate percentage fields
        tenth = self.tenth_entry.get().strip()
        twelfth = self.twelfth_entry.get().strip()
        
        if tenth:
            try:
                tenth_val = float(tenth)
                if not (0 <= tenth_val <= 100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "10th percentage must be a number between 0 and 100.")
                return False
                
        if twelfth:
            try:
                twelfth_val = float(twelfth)
                if not (0 <= twelfth_val <= 100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "12th percentage must be a number between 0 and 100.")
                return False
        
        return True

    def _get_form_data(self):
        """Extract all form data into a dictionary."""
        return {
            'roll_number': self.roll_entry.get().strip(),
            'name': self.name_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'contact_number': self.contact_entry.get().strip(),
            'date_of_birth': self.dob_entry.get().strip(),
            'gender': self.gender_combo.get().strip(),
            'aadhaar_no': self.aadhaar_entry.get().strip(),
            'blood_group': self.blood_combo.get().strip(),
            'mother_name': self.mother_entry.get().strip(),
            'tenth_percent': float(self.tenth_entry.get().strip()) if self.tenth_entry.get().strip() else None,
            'twelfth_percent': float(self.twelfth_entry.get().strip()) if self.twelfth_entry.get().strip() else None,
            'course': self.course_combo.get().strip(),
            'academic_year': self.year_combo.get().strip(),
            'enrollment_status': self.status_combo.get().strip(),
            'address': self.address_text.get("1.0", tk.END).strip()
        }

    def _populate_form_with_student(self, student):
        """Populate form fields with student data."""
        self.clear_student_form()
        
        # Basic info
        self.roll_entry.insert(0, student['roll_number'] or '')
        self.name_entry.insert(0, student['name'] or '')
        self.email_entry.insert(0, student['email'] or '')
        self.contact_entry.insert(0, student['contact_number'] or '')
        self.dob_entry.insert(0, student['date_of_birth'] or '')
        
        # Combo boxes
        if student['gender']:
            self.gender_combo.set(student['gender'])
        if student['blood_group']:
            self.blood_combo.set(student['blood_group'])
        if student['course_name']:
            self.course_combo.set(student['course_name'])
        if student['year_name']:
            self.year_combo.set(student['year_name'])
            
        # Other fields
        self.aadhaar_entry.insert(0, student['aadhaar_no'] or '')
        self.mother_entry.insert(0, student['mother_name'] or '')
        
        if student['tenth_percent']:
            self.tenth_entry.insert(0, str(student['tenth_percent']))
        if student['twelfth_percent']:
            self.twelfth_entry.insert(0, str(student['twelfth_percent']))
            
        # Status
        status = "Active" if student['enrollment_status'] == 1 else "Inactive"
        self.status_combo.set(status)
        
        # Address
        if student['address']:
            self.address_text.insert("1.0", student['address'])


    # ============================================================================
    # -------------------------- REPORTING & EXPORT TAB --------------------------
    # ============================================================================
    def setup_reports_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # --- Controls ---
        controls_frame = ttk.LabelFrame(parent_frame, text="Generate & Export Reports", padding=15, bootstyle="info")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_type_combo = ttk.Combobox(controls_frame, values=["Full Student List", "Enrollment Report", "Payment History"])
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.report_type_combo.set("Full Student List")
        
        ttk.Button(controls_frame, text="Generate Report", command=self.generate_report, bootstyle="primary").grid(row=0, column=2, padx=10)

        # --- Output & Actions ---
        output_frame = ttk.Frame(parent_frame)
        output_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.report_tree = ttk.Treeview(output_frame, show="headings", bootstyle="primary")
        self.report_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = ttk.Scrollbar(output_frame, orient="vertical", command=self.report_tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.report_tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(output_frame, orient="horizontal", command=self.report_tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.report_tree.configure(xscrollcommand=scrollbar_x.set)

        # --- Action Buttons (initially disabled) ---
        self.actions_frame = ttk.Frame(parent_frame)
        self.actions_frame.grid(row=2, column=0, sticky="e", padx=10, pady=10)

        self.export_pdf_btn = ttk.Button(self.actions_frame, text="Export to PDF", command=self.export_report_pdf, state="disabled")
        self.export_pdf_btn.pack(side="left", padx=5)

        self.export_csv_btn = ttk.Button(self.actions_frame, text="Export to CSV", command=self.export_report_csv, state="disabled")
        self.export_csv_btn.pack(side="left", padx=5)
        
        self.share_email_btn = ttk.Button(self.actions_frame, text="Share via Email...", command=self.share_report_email, state="disabled")
        self.share_email_btn.pack(side="left", padx=5)

    def generate_report(self):
        report_type = self.report_type_combo.get()
        if not report_type:
            messagebox.showwarning("Selection Error", "Please select a report type.")
            return

        # Clear previous report
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        self.report_tree["columns"] = []

        conn = get_db_connection()
        
        if report_type == "Full Student List":
            query = """
                SELECT s.roll_number as 'Roll No', s.name as 'Name', c.course_name as 'Course', 
                       ay.year_name as 'Year', f.faculty_name as 'Faculty', s.email as 'Email', 
                       s.contact_number as 'Contact', s.enrollment_date as 'Enroll Date'
                FROM students s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
                ORDER BY s.name;
            """
            self.current_report_data = conn.execute(query).fetchall()

        elif report_type == "Enrollment Report":
            query = """
                SELECT s.enrollment_date as 'Date', s.roll_number as 'Roll No', s.name as 'Name', 
                    c.course_name as 'Course', 
                    CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END AS 'Status'
                FROM students s JOIN courses c ON s.course_id = c.course_id
                ORDER BY s.enrollment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()

        elif report_type == "Payment History":
            query = """
                SELECT p.payment_date as 'Date', s.name as 'Student', p.amount_paid as 'Amount', 
                    p.payment_type as 'Type', p.receipt_number as 'Receipt#'
                FROM payments p JOIN students s ON p.student_id = s.student_id
                ORDER BY p.payment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        
        conn.close()

        if not self.current_report_data:
            messagebox.showinfo("No Data", "No data found for the selected report.")
            self.export_pdf_btn.config(state="disabled")
            self.export_csv_btn.config(state="disabled")
            self.share_email_btn.config(state="disabled")
            return

        # Populate Treeview
        headers = list(self.current_report_data[0].keys())
        self.report_tree["columns"] = headers
        for col in headers:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120, anchor='w')

        for row in self.current_report_data:
            self.report_tree.insert("", "end", values=list(row))
        
        # Enable action buttons
        self.export_pdf_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")
        self.share_email_btn.config(state="normal")
        
    def export_report_pdf(self):
        report_type = self.report_type_combo.get()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            initialfile=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        if not filepath: return
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph(f"{report_type} Report", styles['h1']))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['h3']))
            story.append(Spacer(1, 24))

            headers = list(self.current_report_data[0].keys())
            data = [headers] + [list(map(str, row)) for row in self.current_report_data]
            
            table = Table(data, hAlign='LEFT')
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007bff")), # Primary color
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f0f0f0")), # Light background
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6)
            ])
            table.setStyle(table_style)
            story.append(table)
            doc.build(story)
            
            log_delivery('report', report_type, 'User Download', 'download', 'Completed')
            messagebox.showinfo("Success", f"Report saved successfully to:\n{filepath}")
        except Exception as e:
            log_delivery('report', report_type, 'User Download', 'download', 'Failed', str(e))
            messagebox.showerror("Export Error", f"Failed to generate PDF: {e}")
            
    def export_report_csv(self):
        report_type = self.report_type_combo.get()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not filepath: return

        try:
            headers = list(self.current_report_data[0].keys())
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for row in self.current_report_data:
                    writer.writerow(list(row))
            
            log_delivery('report', report_type, 'User Download', 'download', 'Completed')
            messagebox.showinfo("Success", f"Report saved successfully to:\n{filepath}")
        except Exception as e:
            log_delivery('report', report_type, 'User Download', 'download', 'Failed', str(e))
            messagebox.showerror("Export Error", f"Failed to generate CSV: {e}")

    def share_report_email(self):
        # First, save a temporary PDF to attach
        report_type = self.report_type_combo.get()
        temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")

        # Reuse PDF generation logic
        self.export_report_pdf.__self__.current_report_data = self.current_report_data
        self.export_report_pdf.__self__.report_type_combo = self.report_type_combo
        
        # A bit of a hack to call the PDF export on a temporary file
        try:
            doc = SimpleDocTemplate(temp_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            story.append(Paragraph(f"{report_type} Report", styles['h1']))
            headers = list(self.current_report_data[0].keys())
            data = [headers] + [list(map(str, row)) for row in self.current_report_data]
            table = Table(data, hAlign='LEFT')
            table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
            story.append(table)
            doc.build(story)
            
            # Now open the email dialog
            EmailDialog(self.master, temp_path, report_type)

        except Exception as e:
            messagebox.showerror("Error", f"Could not prepare file for sharing: {e}")


    # ============================================================================
    # --------------------------- ANALYTICS & INSIGHTS TAB -----------------------
    # ============================================================================
    def setup_analytics_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # --- Controls ---
        controls_frame = ttk.LabelFrame(parent_frame, text="Generate Visual Analytics", padding=15, bootstyle="info")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text="Insight Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.analytics_combo = ttk.Combobox(controls_frame, values=["Students per Course", "Enrollment Status Breakdown"])
        self.analytics_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.analytics_combo.set("Students per Course")
        
        ttk.Button(controls_frame, text="Generate Chart", command=self.generate_chart, bootstyle="primary").grid(row=0, column=2, padx=10)
        
        # --- Chart Canvas ---
        self.chart_display_frame = ttk.Frame(parent_frame, padding=10)
        self.chart_display_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def generate_chart(self):
        # Clear previous chart
        for widget in self.chart_display_frame.winfo_children():
            widget.destroy()

        insight = self.analytics_combo.get()
        conn = get_db_connection()

        fig = Figure(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor(self.style.colors.bg)
        ax = fig.add_subplot(111)
        
        if insight == "Students per Course":
            query = """
                SELECT c.course_name, COUNT(s.student_id) as count
                FROM courses c LEFT JOIN students s ON c.course_id = s.course_id
                GROUP BY c.course_name ORDER BY count DESC;
            """
            data = conn.execute(query).fetchall()
            labels = [row['course_name'] for row in data]
            values = [row['count'] for row in data]
            
            ax.set_title("Number of Students per Course", color=self.style.colors.fg)
            ax.bar(labels, values, color=self.style.colors.primary)
            ax.set_ylabel("Number of Students", color=self.style.colors.fg)
            ax.tick_params(axis='x', rotation=45, colors=self.style.colors.fg)
            ax.tick_params(axis='y', colors=self.style.colors.fg)

        elif insight == "Enrollment Status Breakdown":
            query = """
                SELECT CASE WHEN enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END as status, 
                    COUNT(student_id) as count
                FROM students GROUP BY status;
            """
            data = conn.execute(query).fetchall()
            labels = [row['status'] for row in data]
            values = [row['count'] for row in data]

            ax.set_title("Student Enrollment Status", color=self.style.colors.fg)
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                colors=[self.style.colors.success, self.style.colors.danger],
                textprops=dict(color=self.style.colors.fg))
            ax.axis('equal')

        conn.close()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)    # ============================================================================
    # ----------------------------- ID CARD GENERATION TAB -----------------------
    # ============================================================================
    def setup_id_card_tab(self, parent_frame):
        """ID Card Generation functionality."""
        ttk.Label(parent_frame, text="Student ID Card Generation", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)

        main_frame = ttk.Frame(parent_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Student Selection", padding=15, bootstyle="info")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Student Roll Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.id_roll_entry = ttk.Entry(input_frame, width=20)
        self.id_roll_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(input_frame, text="Load Student", command=self.load_student_for_id, bootstyle="info").grid(row=0, column=2, padx=10)
        ttk.Button(input_frame, text="Generate ID Card", command=self.generate_id_card, bootstyle="success").grid(row=0, column=3, padx=5)
        ttk.Button(input_frame, text="Download ID Card", command=self.download_id_card, bootstyle="warning").grid(row=0, column=4, padx=5)

        # Student info display
        info_frame = ttk.LabelFrame(main_frame, text="Student Information", padding=15, bootstyle="secondary")
        info_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        self.id_student_info = tk.Text(info_frame, height=12, width=40, state="disabled", wrap="word")
        self.id_student_info.pack(fill="both", expand=True)

        # ID Card preview
        preview_frame = ttk.LabelFrame(main_frame, text="ID Card Preview", padding=15, bootstyle="primary")
        preview_frame.grid(row=1, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.id_card_canvas = tk.Canvas(preview_frame, width=400, height=250, bg="white", relief="solid", borderwidth=1)
        self.id_card_canvas.grid(row=0, column=0, padx=10, pady=10)

        # Initial empty card
        self.draw_empty_id_card()

    def load_student_for_id(self):
        """Load student data for ID card generation."""
        roll_number = self.id_roll_entry.get().strip()
        if not roll_number:
            messagebox.showwarning("Input Error", "Please enter a roll number.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, c.course_name, ay.year_name, f.faculty_name
                FROM students s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
                WHERE s.roll_number=?
            """, (roll_number,))
            
            student = cursor.fetchone()
            if not student:
                messagebox.showerror("Not Found", "No student found with this roll number.")
                return

            # Display student information
            self.id_student_info.config(state="normal")
            self.id_student_info.delete("1.0", tk.END)
            
            info_text = f"""Student Details:
            
Roll Number: {student['roll_number']}
Name: {student['name']}
Course: {student['course_name'] or 'Not assigned'}
Academic Year: {student['year_name'] or 'Not assigned'}
Faculty: {student['faculty_name'] or 'Not assigned'}
Email: {student['email'] or 'Not provided'}
Contact: {student['contact_number'] or 'Not provided'}
Date of Birth: {student['date_of_birth'] or 'Not provided'}
Blood Group: {student['blood_group'] or 'Not provided'}
Address: {student['address'] or 'Not provided'}
Enrollment Date: {student['enrollment_date']}
Status: {'Active' if student['enrollment_status'] == 1 else 'Inactive'}"""

            self.id_student_info.insert("1.0", info_text)
            self.id_student_info.config(state="disabled")
            
            # Store student data for ID generation
            self.current_id_student = student
            
            # Update ID card preview
            self.draw_id_card_preview(student)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load student: {e}")
        finally:
            conn.close()

    def draw_empty_id_card(self):
        """Draw empty ID card template."""
        self.id_card_canvas.delete("all")
        
        # Card border
        self.id_card_canvas.create_rectangle(10, 10, 390, 240, outline="navy", width=3, fill="lightblue")
        
        # Header
        self.id_card_canvas.create_rectangle(10, 10, 390, 50, fill="navy")
        self.id_card_canvas.create_text(200, 30, text="STUDENT ID CARD", fill="white", font=("Arial", 14, "bold"))
        
        # Placeholder text
        self.id_card_canvas.create_text(200, 125, text="Load a student to generate ID card", fill="gray", font=("Arial", 12))
    
    def draw_id_card_preview(self, student):
        """Draw ID card with student information."""
        self.id_card_canvas.delete("all")
        
        # Card border and background
        self.id_card_canvas.create_rectangle(10, 10, 390, 240, outline="navy", width=3, fill="lightblue")
        
        # Header
        self.id_card_canvas.create_rectangle(10, 10, 390, 50, fill="navy")
        self.id_card_canvas.create_text(200, 30, text="STUDENT ID CARD", fill="white", font=("Arial", 14, "bold"))
        
        # Photo section
        photo_x1, photo_y1, photo_x2, photo_y2 = 20, 60, 100, 140
        self.id_card_canvas.create_rectangle(photo_x1, photo_y1, photo_x2, photo_y2, outline="black", width=2, fill="white")
          # Try to load and display profile picture
        if student['profile_picture_path'] and os.path.exists(student['profile_picture_path']):
            try:
                # Load and resize image for preview
                img = Image.open(student['profile_picture_path'])
                img_resized = img.resize((75, 75), Image.Resampling.LANCZOS)
                self.preview_photo = ImageTk.PhotoImage(img_resized)
                
                # Calculate center position for the photo
                photo_center_x = (photo_x1 + photo_x2) // 2
                photo_center_y = (photo_y1 + photo_y2) // 2
                
                self.id_card_canvas.create_image(photo_center_x, photo_center_y, image=self.preview_photo)
            except Exception as e:
                # If image loading fails, show placeholder
                self.id_card_canvas.create_text(60, 100, text="PHOTO\nERROR", fill="red", font=("Arial", 8))
        else:
            # No profile picture available
            self.id_card_canvas.create_text(60, 100, text="NO\nPHOTO", fill="gray", font=("Arial", 8))
        
        # Student information
        info_x = 110
        start_y = 65
        line_height = 15
        
        details = [
            f"Name: {student['name']}",
            f"Roll No: {student['roll_number']}",
            f"Course: {student['course_name'] or 'N/A'}",
            f"Year: {student['year_name'] or 'N/A'}",
            f"DOB: {student['date_of_birth'] or 'N/A'}",
            f"Blood Group: {student['blood_group'] or 'N/A'}"
        ]
        
        for i, detail in enumerate(details):
            self.id_card_canvas.create_text(info_x, start_y + (i * line_height), text=detail, 
                                          anchor="w", fill="black", font=("Arial", 9))
        
        # Footer
        self.id_card_canvas.create_text(200, 160, text="Valid for Academic Session", fill="black", font=("Arial", 8))
        self.id_card_canvas.create_text(200, 175, text=f"Issued: {datetime.now().strftime('%Y-%m-%d')}", 
                                      fill="black", font=("Arial", 8))
          # College signature area
        self.id_card_canvas.create_text(200, 205, text="Authorized Signature", fill="black", font=("Arial", 8))
        self.id_card_canvas.create_line(150, 220, 250, 220, fill="black")

    def generate_id_card(self):
        """Generate and save ID card as image."""
        if not hasattr(self, 'current_id_student'):
            messagebox.showwarning("No Student", "Please load a student first.")
            return

        try:
            # Create a higher resolution image for printing
            img_width, img_height = 800, 500  # Doubled resolution
            img = Image.new('RGB', (img_width, img_height), 'lightblue')
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a better font
                title_font = ImageFont.truetype("arial.ttf", 28)
                text_font = ImageFont.truetype("arial.ttf", 18)
                small_font = ImageFont.truetype("arial.ttf", 16)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw border
            draw.rectangle([20, 20, img_width-20, img_height-20], outline='navy', width=6)
            
            # Header background
            draw.rectangle([20, 20, img_width-20, 100], fill='navy')
            
            # Title
            title_text = "STUDENT ID CARD"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((img_width - title_width) // 2, 45), title_text, fill='white', font=title_font)
            
            # Photo area
            draw.rectangle([40, 120, 200, 280], outline='black', width=4, fill='white')
              # Try to load and paste actual profile picture
            student = self.current_id_student
            if student['profile_picture_path'] and os.path.exists(student['profile_picture_path']):
                try:
                    # Load and resize profile picture
                    profile_img = Image.open(student['profile_picture_path'])
                    # Resize to fit the photo area (152x152 pixels with some padding)
                    profile_img_resized = profile_img.resize((152, 152), Image.Resampling.LANCZOS)
                    # Paste the image in the photo area
                    img.paste(profile_img_resized, (44, 124))  # Positioned within the border
                except Exception as e:
                    # If image loading fails, show error message
                    error_text = "IMAGE\nERROR"
                    error_bbox = draw.textbbox((0, 0), error_text, font=text_font)
                    error_width = error_bbox[2] - error_bbox[0]
                    draw.text((120 - error_width//2, 190), error_text, fill='red', font=text_font)
            else:
                # No profile picture available
                photo_text = "NO\nPHOTO"
                photo_bbox = draw.textbbox((0, 0), photo_text, font=text_font)
                photo_width = photo_bbox[2] - photo_bbox[0]
                draw.text((120 - photo_width//2, 190), photo_text, fill='gray', font=text_font)
            
            # Student details
            student = self.current_id_student
            details = [
                f"Name: {student['name']}",
                f"Roll Number: {student['roll_number']}",
                f"Course: {student['course_name'] or 'Not Assigned'}",
                f"Academic Year: {student['year_name'] or 'Not Assigned'}",
                f"Date of Birth: {student['date_of_birth'] or 'Not Provided'}",
                f"Blood Group: {student['blood_group'] or 'Not Provided'}",
                f"Contact: {student['contact_number'] or 'Not Provided'}"
            ]
            
            y_offset = 130
            for detail in details:
                draw.text((220, y_offset), detail, fill='black', font=text_font)
                y_offset += 25
            
            # Footer information
            draw.text((400, 320), "Valid for Current Academic Session", fill='black', font=small_font, anchor="mm")
            draw.text((400, 345), f"Issued on: {datetime.now().strftime('%Y-%m-%d')}", fill='black', font=small_font, anchor="mm")
            
            # Signature line
            draw.line([300, 400, 500, 400], fill='black', width=2)
            draw.text((400, 415), "Authorized Signature", fill='black', font=small_font, anchor="mm")
              # Save file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                initialfile=f"ID_Card_{student['roll_number']}_{datetime.now().strftime('%Y%m%d')}.png"
            )
            
            if file_path:
                img.save(file_path, "PNG", quality=95)
                  # Log the generation
                log_delivery('ID Card', student['roll_number'], 'User Download', 'download', 'Completed')
                
                messagebox.showinfo("Success", f"ID Card generated successfully!\nSaved to: {file_path}")
            
        except Exception as e:
            log_delivery('ID Card', self.current_id_student['roll_number'] if hasattr(self, 'current_id_student') else 'Unknown', 
                        'User Download', 'download', 'Failed', str(e))
            messagebox.showerror("Generation Error", f"Failed to generate ID card: {e}")

    def download_id_card(self):
        """Download ID card for the currently loaded student."""
        if not hasattr(self, 'current_id_student'):
            messagebox.showwarning("No Student", "Please load a student first using 'Load Student' button.")
            return

        try:
            # Create a higher resolution image for download
            img_width, img_height = 800, 500  # High resolution for printing
            img = Image.new('RGB', (img_width, img_height), 'lightblue')
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a better font
                title_font = ImageFont.truetype("arial.ttf", 28)
                text_font = ImageFont.truetype("arial.ttf", 18)
                small_font = ImageFont.truetype("arial.ttf", 16)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw border
            draw.rectangle([20, 20, img_width-20, img_height-20], outline='navy', width=6)
            
            # Header background
            draw.rectangle([20, 20, img_width-20, 100], fill='navy')
            
            # Title
            title_text = "STUDENT ID CARD"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((img_width - title_width) // 2, 45), title_text, fill='white', font=title_font)
            
            # Photo area
            draw.rectangle([40, 120, 200, 280], outline='black', width=4, fill='white')
              # Try to load and paste actual profile picture
            student = self.current_id_student
            if student['profile_picture_path'] and os.path.exists(student['profile_picture_path']):
                try:
                    # Load and resize profile picture
                    profile_img = Image.open(student['profile_picture_path'])
                    # Resize to fit the photo area (152x152 pixels with some padding)
                    profile_img_resized = profile_img.resize((152, 152), Image.Resampling.LANCZOS)
                    # Paste the image in the photo area
                    img.paste(profile_img_resized, (44, 124))  # Positioned within the border
                except Exception as e:
                    # If image loading fails, show error message
                    error_text = "IMAGE\nERROR"
                    error_bbox = draw.textbbox((0, 0), error_text, font=text_font)
                    error_width = error_bbox[2] - error_bbox[0]
                    draw.text((120 - error_width//2, 190), error_text, fill='red', font=text_font)
            else:
                # No profile picture available
                photo_text = "NO\nPHOTO"
                photo_bbox = draw.textbbox((0, 0), photo_text, font=text_font)
                photo_width = photo_bbox[2] - photo_bbox[0]
                draw.text((120 - photo_width//2, 190), photo_text, fill='gray', font=text_font)
            
            # Student details
            student = self.current_id_student
            details = [
                f"Name: {student['name']}",
                f"Roll Number: {student['roll_number']}",
                f"Course: {student['course_name'] or 'Not Assigned'}",
                f"Academic Year: {student['year_name'] or 'Not Assigned'}",
                f"Date of Birth: {student['date_of_birth'] or 'Not Provided'}",
                f"Blood Group: {student['blood_group'] or 'Not Provided'}",
                f"Contact: {student['contact_number'] or 'Not Provided'}"
            ]
            
            y_offset = 130
            for detail in details:
                draw.text((220, y_offset), detail, fill='black', font=text_font)
                y_offset += 25
            
            # Footer information
            draw.text((400, 320), "Valid for Current Academic Session", fill='black', font=small_font, anchor="mm")
            draw.text((400, 345), f"Issued on: {datetime.now().strftime('%Y-%m-%d')}", fill='black', font=small_font, anchor="mm")
            
            # Signature line
            draw.line([300, 400, 500, 400], fill='black', width=2)
            draw.text((400, 415), "Authorized Signature", fill='black', font=small_font, anchor="mm")
            
            # Auto-save with timestamp
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = f"ID_Card_{student['roll_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path = os.path.join(downloads_folder, filename)
            
            # Ensure downloads folder exists
            os.makedirs(downloads_folder, exist_ok=True)
            
            img.save(file_path, "PNG", quality=95)
            
            # Log the download
            log_delivery('ID Card', student['roll_number'], 'User Download', 'download', 'Completed')
            
            messagebox.showinfo("Download Complete", f"ID Card downloaded successfully!\nSaved to: {file_path}")
            
        except Exception as e:
            log_delivery('ID Card', self.current_id_student['roll_number'] if hasattr(self, 'current_id_student') else 'Unknown', 
                        'User Download', 'download', 'Failed', str(e))
            messagebox.showerror("Download Error", f"Failed to download ID card: {e}")

    # ============================================================================
    # --------------------------- RECEIPT GENERATION TAB -------------------------
    # ============================================================================
    def setup_receipt_tab(self, parent_frame):
        """Payment Receipt Generation functionality."""
        ttk.Label(parent_frame, text="Payment Receipt Generation", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)

        main_frame = ttk.Frame(parent_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)

        # Payment entry section
        entry_frame = ttk.LabelFrame(main_frame, text="Payment Details", padding=15, bootstyle="info")
        entry_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        entry_frame.columnconfigure((1, 3), weight=1)

        # Row 1
        ttk.Label(entry_frame, text="Student Roll Number*:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.receipt_roll_entry = ttk.Entry(entry_frame, width=20)
        self.receipt_roll_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(entry_frame, text="Amount Paid*:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.receipt_amount_entry = ttk.Entry(entry_frame, width=15)
        self.receipt_amount_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Row 2
        ttk.Label(entry_frame, text="Payment Type*:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.receipt_type_combo = ttk.Combobox(entry_frame, values=["Tuition Fee", "Exam Fee", "Library Fee", "Other"], width=20)
        self.receipt_type_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(entry_frame, text="Payment Date:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.receipt_date_entry = ttk.Entry(entry_frame, width=15)
        self.receipt_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.receipt_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Row 3
        ttk.Label(entry_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.receipt_desc_text = tk.Text(entry_frame, height=3, width=40)
        self.receipt_desc_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Action buttons
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        ttk.Button(button_frame, text="Record Payment", command=self.record_payment, bootstyle="success").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Generate Receipt", command=self.generate_receipt, bootstyle="primary").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Download Receipt", command=self.download_receipt, bootstyle="info").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_receipt_form, bootstyle="secondary").pack(side="left", padx=5)

        # Payment history section
        history_frame = ttk.LabelFrame(main_frame, text="Payment History", padding=15, bootstyle="primary")
        history_frame.grid(row=1, column=0, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        # Treeview for payment history
        self.payment_tree = ttk.Treeview(history_frame, 
                                        columns=("Date", "Student", "Amount", "Type", "Receipt#", "Description"), 
                                        show="headings", bootstyle="primary")

        columns_config = {
            "Date": ("Payment Date", 100),
            "Student": ("Student Name", 150),
            "Amount": ("Amount (₹)", 100),
            "Type": ("Payment Type", 120),
            "Receipt#": ("Receipt Number", 130),
            "Description": ("Description", 200)
        }

        for col, (heading, width) in columns_config.items():
            self.payment_tree.heading(col, text=heading)
            self.payment_tree.column(col, width=width, anchor="w")

        self.payment_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars for payment tree
        v_scroll_payment = ttk.Scrollbar(history_frame, orient="vertical", command=self.payment_tree.yview)
        v_scroll_payment.grid(row=0, column=1, sticky="ns")
        self.payment_tree.configure(yscrollcommand=v_scroll_payment.set)

        h_scroll_payment = ttk.Scrollbar(history_frame, orient="horizontal", command=self.payment_tree.xview)
        h_scroll_payment.grid(row=1, column=0, sticky="ew")
        self.payment_tree.configure(xscrollcommand=h_scroll_payment.set)

        # Load payment history
        self.load_payment_history()

        # Double-click to regenerate receipt
        self.payment_tree.bind("<Double-1>", self.regenerate_receipt_from_history)

    def record_payment(self):
        """Record a new payment in the database."""
        roll_number = self.receipt_roll_entry.get().strip()
        amount = self.receipt_amount_entry.get().strip()
        payment_type = self.receipt_type_combo.get().strip()
        payment_date = self.receipt_date_entry.get().strip()
        description = self.receipt_desc_text.get("1.0", tk.END).strip()

        # Validation
        if not all([roll_number, amount, payment_type, payment_date]):
            messagebox.showwarning("Input Error", "Please fill all required fields (marked with *).")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive amount.")
            return

        # Validate date format
        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter date in YYYY-MM-DD format.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if student exists
            cursor.execute("SELECT student_id, name FROM students WHERE roll_number=?", (roll_number,))
            student = cursor.fetchone()
            if not student:
                messagebox.showerror("Error", "Student with this roll number not found.")
                return

            student_id = student[0]
            
            # Generate unique receipt number
            receipt_number = f"RCP{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Insert payment record
            cursor.execute("""
                INSERT INTO payments (student_id, amount_paid, payment_date, payment_type, receipt_number, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, amount, payment_date, payment_type, receipt_number, description))
            
            conn.commit()
            
            messagebox.showinfo("Success", f"Payment recorded successfully!\nReceipt Number: {receipt_number}")
            self.load_payment_history()
            
            # Store for receipt generation
            self.current_payment_data = {
                'student_id': student_id,
                'student_name': student[1],
                'roll_number': roll_number,
                'amount': amount,
                'payment_type': payment_type,
                'payment_date': payment_date,
                'receipt_number': receipt_number,
                'description': description
            }
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to record payment: {e}")
        finally:            conn.close()

    def generate_receipt(self):
        """Generate payment receipt PDF."""
        if not hasattr(self, 'current_payment_data'):
            messagebox.showwarning("No Payment", "Please record a payment first or select from history.")
            return
            
        try:
            payment = self.current_payment_data
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Receipt_{payment['receipt_number']}.pdf"
            )
            
            if not file_path:
                return

            # Create PDF receipt
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Header
            story.append(Paragraph("PAYMENT RECEIPT", styles['h1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Receipt Number: {payment['receipt_number']}", styles['h2']))
            story.append(Spacer(1, 24))

            # Payment details table
            data = [
                ["Field", "Details"],
                ["Student Name", payment['student_name']],
                ["Roll Number", payment['roll_number']],
                ["Payment Date", payment['payment_date']],
                ["Payment Type", payment['payment_type']],
                ["Amount Paid", f"₹ {payment['amount']:.2f}"],
                ["Description", payment['description'] if payment['description'] else "N/A"],
                ["Receipt Number", payment['receipt_number']],
                ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]

            table = Table(data, colWidths=[2*72, 3*72])  # 2 inches, 3 inches
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007bff")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            story.append(table)
            story.append(Spacer(1, 36))

            # Footer
            story.append(Paragraph("Thank you for your payment!", styles['h3']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("This is a computer-generated receipt.", styles['Normal']))
            story.append(Paragraph("For any queries, please contact the administration.", styles['Normal']))

            # Build PDF
            doc.build(story)
            
            # Log the generation
            log_delivery('Receipt', payment['receipt_number'], 'User Download', 'download', 'Completed')
            
            messagebox.showinfo("Success", f"Receipt generated successfully!\nSaved to: {file_path}")
            
        except Exception as e:
            log_delivery('Receipt', payment['receipt_number'] if hasattr(self, 'current_payment_data') else 'Unknown', 
                        'User Download', 'download', 'Failed', str(e))
            messagebox.showerror("Generation Error", f"Failed to generate receipt: {e}")

    def download_receipt(self):
        """Download receipt from payment history."""
        selection = self.payment_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a payment from the history to download its receipt.")
            return

        item = self.payment_tree.item(selection[0])
        receipt_number = item['values'][4]  # Receipt number column

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, s.name, s.roll_number
                FROM payments p
                JOIN students s ON p.student_id = s.student_id
                WHERE p.receipt_number = ?
            """, (receipt_number,))
            
            payment_row = cursor.fetchone()
            if not payment_row:
                messagebox.showerror("Error", "Payment record not found.")
                return

            # Set current payment data for receipt generation
            self.current_payment_data = {
                'student_id': payment_row['student_id'],
                'student_name': payment_row['name'],
                'roll_number': payment_row['roll_number'],
                'amount': payment_row['amount_paid'],
                'payment_type': payment_row['payment_type'],
                'payment_date': payment_row['payment_date'],
                'receipt_number': payment_row['receipt_number'],
                'description': payment_row['description'] or ''
            }
            
            # Generate and download receipt
            self.generate_receipt()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load payment details: {e}")
        finally:
            conn.close()

    def clear_receipt_form(self):
        """Clear all receipt form fields."""
        self.receipt_roll_entry.delete(0, tk.END)
        self.receipt_amount_entry.delete(0, tk.END)
        self.receipt_type_combo.set("")
        self.receipt_date_entry.delete(0, tk.END)
        self.receipt_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.receipt_desc_text.delete("1.0", tk.END)

    def load_payment_history(self):
        """Load payment history into treeview."""
        # Clear existing items
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.payment_date, s.name, p.amount_paid, p.payment_type, p.receipt_number, p.description
                FROM payments p
                JOIN students s ON p.student_id = s.student_id
                ORDER BY p.payment_date DESC, p.payment_id DESC
            """)
            
            for row in cursor.fetchall():
                # Format amount with currency symbol
                formatted_row = list(row)
                formatted_row[2] = f"₹ {row[2]:.2f}"
                self.payment_tree.insert("", "end", values=formatted_row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load payment history: {e}")
        finally:
            conn.close()

    def regenerate_receipt_from_history(self, event):
        """Regenerate receipt from selected payment history."""
        selection = self.payment_tree.selection()
        if not selection:
            return

        item = self.payment_tree.item(selection[0])
        receipt_number = item['values'][4]  # Receipt number column

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, s.name, s.roll_number
                FROM payments p
                JOIN students s ON p.student_id = s.student_id
                WHERE p.receipt_number = ?
            """, (receipt_number,))
            
            payment_row = cursor.fetchone()
            if not payment_row:
                messagebox.showerror("Error", "Payment record not found.")
                return

            # Set current payment data for receipt generation
            self.current_payment_data = {
                'student_id': payment_row['student_id'],
                'student_name': payment_row['name'],
                'roll_number': payment_row['roll_number'],
                'amount': payment_row['amount_paid'],
                'payment_type': payment_row['payment_type'],
                'payment_date': payment_row['payment_date'],
                'receipt_number': payment_row['receipt_number'],
                'description': payment_row['description'] or ''
            }
            
            # Generate receipt
            self.generate_receipt()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load payment details: {e}")
        finally:
            conn.close()
      # ============================================================================
    # --------------------------- COMMUNICATIONS HUB TAB -------------------------
    # ============================================================================
    def setup_communications_tab(self, parent_frame):
        """Communications Hub for feedback, queries, and announcements."""
        ttk.Label(parent_frame, text="Communications Hub", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)

        # Create notebook for different communication types
        comm_notebook = ttk.Notebook(parent_frame)
        comm_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === FEEDBACK & QUERIES TAB ===
        queries_frame = ttk.Frame(comm_notebook)
        comm_notebook.add(queries_frame, text="📝 Feedback & Queries")
        self.setup_queries_tab(queries_frame)

        # === ANNOUNCEMENTS TAB ===
        announcements_frame = ttk.Frame(comm_notebook)
        comm_notebook.add(announcements_frame, text="📢 Announcements")
        self.setup_announcements_tab(announcements_frame)

        # === COMMUNICATION LOG TAB ===
        log_frame = ttk.Frame(comm_notebook)
        comm_notebook.add(log_frame, text="📊 Communication Log")
        self.setup_communication_log_tab(log_frame)

    def setup_queries_tab(self, parent_frame):
        """Setup tab for viewing and responding to feedback and queries."""
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # Controls
        controls_frame = ttk.Frame(parent_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ttk.Label(controls_frame, text="Filter by Type:").pack(side="left", padx=5)
        self.query_filter = ttk.Combobox(controls_frame, values=["All", "Feedback", "Query"], width=15)
        self.query_filter.pack(side="left", padx=5)
        self.query_filter.set("All")
        self.query_filter.bind("<<ComboboxSelected>>", self.filter_communications)

        ttk.Label(controls_frame, text="Status:").pack(side="left", padx=(20, 5))
        self.status_filter = ttk.Combobox(controls_frame, values=["All", "Pending", "Answered"], width=15)
        self.status_filter.pack(side="left", padx=5)
        self.status_filter.set("All")
        self.status_filter.bind("<<ComboboxSelected>>", self.filter_communications)

        ttk.Button(controls_frame, text="Refresh", command=self.load_communications, bootstyle="info").pack(side="right", padx=5)

        # Communications list and details
        main_frame = ttk.Frame(parent_frame)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Communications list
        list_frame = ttk.LabelFrame(main_frame, text="Communications", padding=10, bootstyle="info")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.comm_tree = ttk.Treeview(list_frame, 
                                     columns=("Type", "Sender", "Subject", "Status", "Date"), 
                                     show="headings", bootstyle="primary")

        columns_config = {
            "Type": ("Type", 80),
            "Sender": ("Sender", 120),
            "Subject": ("Subject", 200),
            "Status": ("Status", 80),
            "Date": ("Date", 100)
        }

        for col, (heading, width) in columns_config.items():
            self.comm_tree.heading(col, text=heading)
            self.comm_tree.column(col, width=width, anchor="w")

        self.comm_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for communications list
        comm_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.comm_tree.yview)
        comm_scroll.grid(row=0, column=1, sticky="ns")
        self.comm_tree.configure(yscrollcommand=comm_scroll.set)

        # Details and response frame
        details_frame = ttk.LabelFrame(main_frame, text="Communication Details", padding=10, bootstyle="primary")
        details_frame.grid(row=0, column=1, sticky="nsew")
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)

        # Communication details display
        self.comm_details = tk.Text(details_frame, height=10, wrap="word", state="disabled")
        self.comm_details.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Response section
        response_frame = ttk.LabelFrame(details_frame, text="Response", padding=10, bootstyle="success")
        response_frame.grid(row=1, column=0, sticky="nsew")
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)

        self.response_text = tk.Text(response_frame, height=6, wrap="word")
        self.response_text.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        response_buttons = ttk.Frame(response_frame)
        response_buttons.grid(row=1, column=0, sticky="ew")

        ttk.Button(response_buttons, text="Send Response", command=self.send_response, bootstyle="success").pack(side="left", padx=5)
        ttk.Button(response_buttons, text="Mark as Read", command=self.mark_as_read, bootstyle="info").pack(side="left", padx=5)

        # Bind selection event
        self.comm_tree.bind("<<TreeviewSelect>>", self.on_communication_select)

        # Load communications
        self.load_communications()

    def setup_announcements_tab(self, parent_frame):
        """Setup tab for creating and managing announcements."""
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # Announcement creation form
        create_frame = ttk.LabelFrame(parent_frame, text="Create New Announcement", padding=15, bootstyle="warning")
        create_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        create_frame.columnconfigure(1, weight=1)

        ttk.Label(create_frame, text="Subject*:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.announcement_subject = ttk.Entry(create_frame, width=50)
        self.announcement_subject.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(create_frame, text="Message*:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.announcement_message = tk.Text(create_frame, height=6, width=60)
        self.announcement_message.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        button_frame = ttk.Frame(create_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Post Announcement", command=self.post_announcement, bootstyle="success").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_announcement_form, bootstyle="secondary").pack(side="left", padx=5)

        # Announcements list
        list_frame = ttk.LabelFrame(parent_frame, text="Recent Announcements", padding=10, bootstyle="info")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.announcements_tree = ttk.Treeview(list_frame, 
                                              columns=("Subject", "Date", "Status"), 
                                              show="headings", bootstyle="primary")

        announcements_columns = {
            "Subject": ("Subject", 300),
            "Date": ("Posted Date", 150),
            "Status": ("Status", 100)
        }

        for col, (heading, width) in announcements_columns.items():
            self.announcements_tree.heading(col, text=heading)
            self.announcements_tree.column(col, width=width, anchor="w")

        self.announcements_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for announcements
        ann_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.announcements_tree.yview)
        ann_scroll.grid(row=0, column=1, sticky="ns")
        self.announcements_tree.configure(yscrollcommand=ann_scroll.set)

        # Load announcements
        self.load_announcements()

    def setup_communication_log_tab(self, parent_frame):
        """Setup tab for viewing communication statistics and logs."""
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        # Statistics
        stats_frame = ttk.LabelFrame(parent_frame, text="Communication Statistics", padding=15, bootstyle="info")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.update_communication_stats(stats_frame)

        # Delivery logs
        log_frame = ttk.LabelFrame(parent_frame, text="Delivery Logs", padding=10, bootstyle="primary")
        log_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.delivery_tree = ttk.Treeview(log_frame, 
                                         columns=("Type", "Identifier", "Recipient", "Channel", "Status", "Date"), 
                                         show="headings", bootstyle="primary")

        delivery_columns = {
            "Type": ("Artefact Type", 100),
            "Identifier": ("Identifier", 120),
            "Recipient": ("Recipient", 150),
            "Channel": ("Channel", 80),
            "Status": ("Status", 80),
            "Date": ("Date", 130)
        }

        for col, (heading, width) in delivery_columns.items():
            self.delivery_tree.heading(col, text=heading)
            self.delivery_tree.column(col, width=width, anchor="w")

        self.delivery_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for delivery logs
        delivery_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.delivery_tree.yview)
        delivery_scroll.grid(row=0, column=1, sticky="ns")
        self.delivery_tree.configure(yscrollcommand=delivery_scroll.set)

        # Load delivery logs
        self.load_delivery_logs()

    def load_communications(self):
        """Load communications from database."""
        # Clear existing items
        for item in self.comm_tree.get_children():
            self.comm_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT comm_id, type, sender_name, sender_email, subject, status, timestamp
                FROM communications
                WHERE type IN ('feedback', 'query')
                ORDER BY timestamp DESC
            """
            
            cursor.execute(query)
            
            for row in cursor.fetchall():
                # Format sender info
                sender = row['sender_name'] if row['sender_name'] else row['sender_email']
                if not sender:
                    sender = "Anonymous"
                
                self.comm_tree.insert("", "end", values=(
                    row['type'].title(),
                    sender,
                    row['subject'],
                    row['status'],
                    row['timestamp']
                ), tags=(str(row['comm_id']),))
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load communications: {e}")
        finally:
            conn.close()

    def filter_communications(self, event=None):
        """Filter communications based on selected criteria."""
        type_filter = self.query_filter.get()
        status_filter = self.status_filter.get()
        
        # Clear existing items
        for item in self.comm_tree.get_children():
            self.comm_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT comm_id, type, sender_name, sender_email, subject, status, timestamp
                FROM communications
                WHERE type IN ('feedback', 'query')
            """
            params = []
            
            if type_filter != "All":
                query += " AND type = ?"
                params.append(type_filter.lower())
                
            if status_filter != "All":
                query += " AND status = ?"
                params.append(status_filter)
                
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                sender = row['sender_name'] if row['sender_name'] else row['sender_email']
                if not sender:
                    sender = "Anonymous"
                
                self.comm_tree.insert("", "end", values=(
                    row['type'].title(),
                    sender,
                    row['subject'],
                    row['status'],
                    row['timestamp']
                ), tags=(str(row['comm_id']),))
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to filter communications: {e}")
        finally:
            conn.close()

    def on_communication_select(self, event):
        """Handle selection of a communication item."""
        selection = self.comm_tree.selection()
        if not selection:
            return

        item = self.comm_tree.item(selection[0])
        comm_id = item['tags'][0] if item['tags'] else None
        
        if not comm_id:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM communications WHERE comm_id = ?", (comm_id,))
            comm = cursor.fetchone()
            
            if comm:
                # Display communication details
                self.comm_details.config(state="normal")
                self.comm_details.delete("1.0", tk.END)
                
                details = f"""From: {comm['sender_name'] or comm['sender_email'] or 'Anonymous'}
Email: {comm['sender_email'] or 'Not provided'}
Type: {comm['type'].title()}
Subject: {comm['subject']}
Date: {comm['timestamp']}
Status: {comm['status']}

Message:
{comm['message_text']}

Response:
{comm['response_text'] if comm['response_text'] else 'No response yet'}"""

                self.comm_details.insert("1.0", details)
                self.comm_details.config(state="disabled")
                
                # Clear response text area
                self.response_text.delete("1.0", tk.END)
                if comm['response_text']:
                    self.response_text.insert("1.0", comm['response_text'])
                
                # Store current communication ID
                self.current_comm_id = comm_id
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load communication details: {e}")
        finally:
            conn.close()

    def send_response(self):
        """Send response to selected communication."""
        if not hasattr(self, 'current_comm_id'):
            messagebox.showwarning("No Selection", "Please select a communication to respond to.")
            return

        response = self.response_text.get("1.0", tk.END).strip()
        if not response:
            messagebox.showwarning("Input Error", "Please enter a response.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE communications 
                SET response_text = ?, status = 'Answered', response_timestamp = ?
                WHERE comm_id = ?
            """, (response, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.current_comm_id))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Response sent successfully!")
            self.load_communications()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to send response: {e}")
        finally:
            conn.close()

    def mark_as_read(self):
        """Mark communication as read."""
        if not hasattr(self, 'current_comm_id'):
            messagebox.showwarning("No Selection", "Please select a communication.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE communications SET status = 'Read' WHERE comm_id = ?", (self.current_comm_id,))
            conn.commit()
            
            messagebox.showinfo("Success", "Communication marked as read!")
            self.load_communications()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update status: {e}")
        finally:
            conn.close()

    def post_announcement(self):
        """Post a new announcement."""
        subject = self.announcement_subject.get().strip()
        message = self.announcement_message.get("1.0", tk.END).strip()
        
        if not subject or not message:
            messagebox.showwarning("Input Error", "Please enter both subject and message.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO communications (sender_id, subject, message_text, type, status, timestamp)
                VALUES ('admin', ?, ?, 'announcement', 'Posted', ?)
            """, (subject, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Announcement posted successfully!")
            self.clear_announcement_form()
            self.load_announcements()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to post announcement: {e}")
        finally:
            conn.close()

    def clear_announcement_form(self):
        """Clear announcement form."""
        self.announcement_subject.delete(0, tk.END)
        self.announcement_message.delete("1.0", tk.END)

    def load_announcements(self):
        """Load announcements from database."""
        # Clear existing items
        for item in self.announcements_tree.get_children():
            self.announcements_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT subject, timestamp, status
                FROM communications
                WHERE type = 'announcement'
                ORDER BY timestamp DESC
            """)
            
            for row in cursor.fetchall():
                self.announcements_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load announcements: {e}")
        finally:
            conn.close()

    def update_communication_stats(self, parent_frame):
        """Update communication statistics display."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get statistics
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM communications WHERE type = 'feedback'")
            stats['feedback'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM communications WHERE type = 'query'")
            stats['queries'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM communications WHERE type = 'announcement'")
            stats['announcements'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM communications WHERE status = 'Pending'")
            stats['pending'] = cursor.fetchone()[0]
            
            # Display statistics
            stats_grid = ttk.Frame(parent_frame)
            stats_grid.pack(fill="x")
            
            ttk.Label(stats_grid, text=f"Total Feedback: {stats['feedback']}", font=("Helvetica", 12)).grid(row=0, column=0, padx=20, pady=5, sticky="w")
            ttk.Label(stats_grid, text=f"Total Queries: {stats['queries']}", font=("Helvetica", 12)).grid(row=0, column=1, padx=20, pady=5, sticky="w")
            ttk.Label(stats_grid, text=f"Total Announcements: {stats['announcements']}", font=("Helvetica", 12)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
            ttk.Label(stats_grid, text=f"Pending Items: {stats['pending']}", font=("Helvetica", 12, "bold")).grid(row=1, column=1, padx=20, pady=5, sticky="w")
            
        except sqlite3.Error as e:
            ttk.Label(parent_frame, text=f"Error loading statistics: {e}").pack()
        finally:
            conn.close()

    def load_delivery_logs(self):
        """Load delivery logs from database."""
        # Clear existing items
        for item in self.delivery_tree.get_children():
            self.delivery_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT artefact_type, artefact_identifier, recipient_address, channel, delivery_status, timestamp
                FROM delivery_logs
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            
            for row in cursor.fetchall():
                self.delivery_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load delivery logs: {e}")
        finally:
            conn.close()

# --- Main Execution ---
if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
        exit(1)

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()