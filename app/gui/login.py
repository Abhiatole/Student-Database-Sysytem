import tkinter as tk
from tkinter import ttk, messagebox
from app.utils.security import verify_password
from app.db.database import get_db_connection

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.withdraw()
        self.login_root = tk.Toplevel(master)
        self.login_root.title("Login")
        self.login_root.geometry("400x350")
        self.login_root.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.login_root, padding=30)
        frame.pack(expand=True, fill="both")
        ttk.Label(frame, text="User Login", font=("Helvetica", 18, "bold")).pack(pady=10)
        ttk.Label(frame, text="Username:").pack(anchor="w", pady=(20, 2))
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(fill="x")
        ttk.Label(frame, text="Password:").pack(anchor="w", pady=(10, 2))
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(fill="x")
        ttk.Button(frame, text="Login", command=self.login).pack(pady=20)
        ttk.Button(frame, text="Register", command=self.open_register).pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE user_id=?", (username,))
        row = cursor.fetchone()
        conn.close()
        from app.main import MainApplication  # <-- Import here to avoid circular import
        if row and verify_password(password, row[0]):
            self.login_root.destroy()
            self.master.deiconify()
            MainApplication(self.master)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_register(self):
        from app.gui.register import RegisterWindow
        RegisterWindow(self.login_root)
