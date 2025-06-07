import tkinter as tk
from tkinter import ttk, messagebox
from app.utils.security import hash_password
from app.db.database import get_db_connection

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.withdraw()
        self.login_root = tk.Toplevel(master)
        self.login_root.title("Login")
        self.login_root.geometry("400x350")
        self.login_root.resizable(False, False)
        # ... rest of the login logic ...
