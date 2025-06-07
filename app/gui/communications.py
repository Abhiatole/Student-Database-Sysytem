from ttkbootstrap import ttk
import tkinter as tk
from tkinter import messagebox
from app.db.database import get_db_connection
from datetime import datetime

# Communication hub logic (feedback, queries, announcements)
class CommunicationsTab:
    def __init__(self, parent):
        self.setup_communications_tab(parent)

    def setup_communications_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Communications Hub", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
        form = ttk.LabelFrame(parent_frame, text="Submit Feedback/Query", padding=10)
        form.pack(pady=10, fill="x")
        ttk.Label(form, text="Your Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(form)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(form)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form, text="Subject:").grid(row=2, column=0, padx=5, pady=5)
        self.subject_entry = ttk.Entry(form)
        self.subject_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(form, text="Message:").grid(row=3, column=0, padx=5, pady=5)
        self.message_entry = ttk.Entry(form, width=50)
        self.message_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(form, text="Submit", command=self.submit_communication, bootstyle="success").grid(row=4, column=0, columnspan=2, pady=10)

    def submit_communication(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        subject = self.subject_entry.get().strip()
        message = self.message_entry.get().strip()
        if not (name and email and subject and message):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO communications (sender_name, sender_email, subject, message_text, type, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, subject, message, "query", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Your message has been submitted.")
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.message_entry.delete(0, tk.END)
