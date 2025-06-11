from ttkbootstrap import ttk
import tkinter as tk
from tkinter import messagebox
from app.db.database import get_db_connection

# ID card generation logic
class IDCardTab:
    def __init__(self, parent):
        self.setup_id_card_tab(parent)

    def setup_id_card_tab(self, parent_frame):
        ttk.Label(parent_frame, text="ID Card Generation", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
        input_frame = ttk.Frame(parent_frame)
        input_frame.pack(pady=10)
        ttk.Label(input_frame, text="Enter Roll Number:").grid(row=0, column=0, padx=5, pady=5)
        self.roll_entry = ttk.Entry(input_frame)
        self.roll_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Generate ID Card", command=self.generate_id_card, bootstyle="success").grid(row=0, column=2, padx=5)
        self.id_card_frame = ttk.LabelFrame(parent_frame, text="ID Card Preview", padding=10)
        self.id_card_frame.pack(pady=10, fill="x")

    def generate_id_card(self):
        roll = self.roll_entry.get().strip()
        if not roll:
            messagebox.showwarning("Input Error", "Please enter a roll number.")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, course_id, academic_year_id FROM students WHERE roll_number=?", (roll,))
        student = cursor.fetchone()
        conn.close()
        for widget in self.id_card_frame.winfo_children():
            widget.destroy()
        if not student:
            ttk.Label(self.id_card_frame, text="Student not found.").pack()
            return
        name, course_id, year_id = student
        ttk.Label(self.id_card_frame, text=f"Name: {name}", font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(self.id_card_frame, text=f"Roll Number: {roll}").pack(anchor="w")
        ttk.Label(self.id_card_frame, text=f"Course ID: {course_id}").pack(anchor="w")
        ttk.Label(self.id_card_frame, text=f"Year ID: {year_id}").pack(anchor="w")
        ttk.Label(self.id_card_frame, text="(This is a sample ID card preview)").pack(anchor="w")
