import tkinter as tk
from tkinter import ttk, messagebox
from app.db.models import Student
from datetime import datetime

class StudentManagementFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.create_widgets()
        self.refresh_student_list()

    def create_widgets(self):
        # Form fields
        form = ttk.LabelFrame(self, text="Student Details")
        form.pack(side='left', fill='y', padx=10, pady=10)
        self.entries = {}
        fields = [
            ('roll_number', 'Roll Number'),
            ('name', 'Name'),
            ('contact_number', 'Contact Number'),
            ('email', 'Email'),
            ('address', 'Address'),
            ('aadhaar_no', 'Aadhaar No'),
            ('date_of_birth', 'Date of Birth (YYYY-MM-DD)'),
            ('gender', 'Gender'),
            ('tenth_percent', '10th %'),
            ('twelfth_percent', '12th %'),
            ('blood_group', 'Blood Group'),
            ('mother_name', 'Mother Name'),
            ('enrollment_date', 'Enrollment Date (YYYY-MM-DD)'),
            ('course_id', 'Course ID'),
            ('academic_year_id', 'Academic Year ID'),
        ]
        for key, label in fields:
            ttk.Label(form, text=label).pack(anchor='w')
            entry = ttk.Entry(form)
            entry.pack(fill='x', pady=2)
            self.entries[key] = entry
        # Buttons
        btn_frame = ttk.Frame(form)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add", command=self.add_student).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_student).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_student).pack(side='left', padx=2)
        # Student list
        self.tree = ttk.Treeview(self, columns=[f[0] for f in fields], show='headings')
        for key, label in fields:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=100)
        self.tree.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def get_form_data(self):
        data = {k: v.get() for k, v in self.entries.items()}
        # Convert numeric fields
        for k in ['tenth_percent', 'twelfth_percent', 'course_id', 'academic_year_id']:
            if data[k]:
                try:
                    data[k] = float(data[k]) if 'percent' in k else int(data[k])
                except ValueError:
                    data[k] = None
        return data

    def add_student(self):
        data = self.get_form_data()
        if not data['roll_number'] or not data['name']:
            messagebox.showerror("Validation Error", "Roll Number and Name are required.")
            return
        data['enrollment_status'] = 1
        try:
            Student.create(data)
            self.refresh_student_list()
            messagebox.showinfo("Success", "Student added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")

    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Student", "Select a student to update.")
            return
        student_id = self.tree.item(selected[0])['values'][0]
        data = self.get_form_data()
        try:
            Student.update(student_id, data)
            self.refresh_student_list()
            messagebox.showinfo("Success", "Student updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Student", "Select a student to delete.")
            return
        student_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            try:
                Student.delete(student_id)
                self.refresh_student_list()
                messagebox.showinfo("Success", "Student deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {e}")

    def refresh_student_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for student in Student.get_all():
            values = [student.get(f) for f in self.tree['columns']]
            self.tree.insert('', 'end', values=values)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])['values']
        for idx, key in enumerate(self.tree['columns']):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, values[idx])

from ttkbootstrap import ttk

class StudentManagementTab:
    def __init__(self, parent):
        self.setup_student_management_tab(parent)

    def setup_student_management_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Student Record Management (CRUD)", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
        ttk.Label(parent_frame, text="[The comprehensive student CRUD interface from the original file would be placed here.]\n"
                                    "- Input fields for all student details.\n"
                                    "- Profile picture upload.\n"
                                    "- Add, Update, Delete, Clear buttons.\n"
                                    "- Search functionality.\n"
                                    "- Treeview to display all students.").pack(pady=20)
