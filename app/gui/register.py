from ttkbootstrap import ttk
import tkinter as tk
from tkinter import messagebox

# Registration window logic for new users
class RegisterWindow:
    def __init__(self, master):
        self.master = master
        self.setup_register_window()

    def setup_register_window(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("Register New User")
        self.window.geometry("400x400")
        ttk.Label(self.window, text="Register New User", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
        form_frame = ttk.Frame(self.window, padding=10)
        form_frame.pack(fill="both", expand=True)
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, pady=5)
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        ttk.Label(form_frame, text="Name:").grid(row=2, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=2, column=1, pady=5)
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky="w", pady=5)
        self.role_combo = ttk.Combobox(form_frame, values=["admin", "student"])
        self.role_combo.grid(row=3, column=1, pady=5)
        ttk.Button(form_frame, text="Register", command=self.register_user, bootstyle="success").grid(row=4, column=0, columnspan=2, pady=20)

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        name = self.name_entry.get().strip()
        role = self.role_combo.get().strip()
        if not (username and password and name and role):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        # Registration logic goes here
        messagebox.showinfo("Success", "User registered successfully!")
        self.window.destroy()
