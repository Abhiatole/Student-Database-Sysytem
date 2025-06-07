# Payment and receipt management logic

from ttkbootstrap import ttk
import tkinter as tk
from tkinter import messagebox
from app.db.database import get_db_connection
from datetime import datetime

class ReceiptTab:
    def __init__(self, parent):
        self.setup_receipt_tab(parent)

    def setup_receipt_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Receipt Generation", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
        form = ttk.Frame(parent_frame)
        form.pack(pady=10)
        ttk.Label(form, text="Roll Number:").grid(row=0, column=0, padx=5, pady=5)
        self.roll_entry = ttk.Entry(form)
        self.roll_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text="Amount Paid:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(form)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form, text="Payment Type:").grid(row=2, column=0, padx=5, pady=5)
        self.type_entry = ttk.Entry(form)
        self.type_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(form, text="Generate Receipt", command=self.generate_receipt, bootstyle="success").grid(row=3, column=0, columnspan=2, pady=10)
        self.receipt_frame = ttk.LabelFrame(parent_frame, text="Receipt", padding=10)
        self.receipt_frame.pack(pady=10, fill="x")

    def generate_receipt(self):
        roll = self.roll_entry.get().strip()
        amount = self.amount_entry.get().strip()
        ptype = self.type_entry.get().strip()
        if not (roll and amount and ptype):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a number.")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name FROM students WHERE roll_number=?", (roll,))
        student = cursor.fetchone()
        if not student:
            conn.close()
            messagebox.showerror("Not Found", "Student not found.")
            return
        student_id, name = student
        payment_date = datetime.now().strftime("%Y-%m-%d")
        receipt_number = f"RCPT{student_id}{int(datetime.now().timestamp())}"
        cursor.execute(
            "INSERT INTO payments (student_id, amount_paid, payment_date, payment_type, receipt_number) VALUES (?, ?, ?, ?, ?)",
            (student_id, amount, payment_date, ptype, receipt_number)
        )
        conn.commit()
        conn.close()
        for widget in self.receipt_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.receipt_frame, text=f"Receipt #: {receipt_number}", font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(self.receipt_frame, text=f"Name: {name}").pack(anchor="w")
        ttk.Label(self.receipt_frame, text=f"Roll Number: {roll}").pack(anchor="w")
        ttk.Label(self.receipt_frame, text=f"Amount Paid: ₹{amount:.2f}").pack(anchor="w")
        ttk.Label(self.receipt_frame, text=f"Payment Type: {ptype}").pack(anchor="w")
        ttk.Label(self.receipt_frame, text=f"Date: {payment_date}").pack(anchor="w")
        ttk.Label(self.receipt_frame, text="(This is a sample receipt preview)").pack(anchor="w")
