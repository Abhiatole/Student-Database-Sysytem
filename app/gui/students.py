import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.db.models import Student
from PIL import Image, ImageTk
import os

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
        # Profile picture
        ttk.Label(form, text="Profile Picture:").pack(anchor='w')
        self.profile_pic_path = tk.StringVar()
        self.profile_pic_label = ttk.Label(form, text="No file selected")
        self.profile_pic_label.pack(anchor='w')
        ttk.Button(form, text="Upload", command=self.upload_profile_picture).pack(anchor='w', pady=2)
        # Buttons
        btn_frame = ttk.Frame(form)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add", command=self.add_student, bootstyle="success").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_student, bootstyle="info").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_student, bootstyle="danger").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form, bootstyle="secondary").pack(side='left', padx=2)
        # Search
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Go", command=self.search_students).pack(side="left", padx=2)
        ttk.Button(search_frame, text="Show All", command=self.refresh_student_list).pack(side="left", padx=2)
        # Student list
        columns = [f[0] for f in fields] + ['profile_picture_path']
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=20)
        for key in columns:
            self.tree.heading(key, text=key.replace('_', ' ').title())
            self.tree.column(key, width=100)
        self.tree.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def upload_profile_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.profile_pic_path.set(file_path)
            self.profile_pic_label.config(text=os.path.basename(file_path))

    def get_form_data(self):
        data = {k: v.get() for k, v in self.entries.items()}
        # Convert numeric fields
        for k in ['tenth_percent', 'twelfth_percent', 'course_id', 'academic_year_id']:
            if data[k]:
                try:
                    data[k] = float(data[k]) if 'percent' in k else int(data[k])
                except ValueError:
                    data[k] = None
        data['profile_picture_path'] = self.profile_pic_path.get() if self.profile_pic_path.get() else None
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
            self.clear_form()
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
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")

    def delete_student(self):
        if not hasattr(self, 'tree'):
            messagebox.showerror("Error", "Student list not initialized.")
            return
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
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {e}")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.profile_pic_path.set("")
        self.profile_pic_label.config(text="No file selected")
        self.tree.selection_remove(self.tree.selection())

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
            if key in self.entries:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, values[idx])
        # Profile picture
        if 'profile_picture_path' in self.tree['columns']:
            idx = self.tree['columns'].index('profile_picture_path')
            pic_path = values[idx]
            self.profile_pic_path.set(pic_path if pic_path else "")
            self.profile_pic_label.config(text=os.path.basename(pic_path) if pic_path else "No file selected")

    def search_students(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.refresh_student_list()
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for student in Student.get_all():
            if any(query in str(value).lower() for value in student.values()):
                values = [student.get(f) for f in self.tree['columns']]
                self.tree.insert('', 'end', values=values)

from ttkbootstrap import ttk

class StudentManagementTab:
    def __init__(self, parent):
        self.setup_student_management_tab(parent)

    def setup_student_management_tab(self, parent_frame):
        self.parent_frame = parent_frame
        ttk.Label(parent_frame, text="Student Record Management (CRUD)", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)

        form_frame = ttk.LabelFrame(parent_frame, text="Student Details", padding=10)
        form_frame.pack(side="left", fill="y", padx=10, pady=10)

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
        for idx, (key, label) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=idx, column=0, sticky="w", pady=2)
            entry = ttk.Entry(form_frame)
            entry.grid(row=idx, column=1, pady=2, sticky="ew")
            self.entries[key] = entry

        # Profile picture
        ttk.Label(form_frame, text="Profile Picture:").grid(row=len(fields), column=0, sticky="w", pady=2)
        self.profile_pic_path = tk.StringVar()
        self.profile_pic_label = ttk.Label(form_frame, text="No file selected")
        self.profile_pic_label.grid(row=len(fields), column=1, sticky="w")
        ttk.Button(form_frame, text="Upload", command=self.upload_profile_picture).grid(row=len(fields), column=2, padx=5)

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="Add", command=self.add_student, bootstyle="success").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_student, bootstyle="info").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_student, bootstyle="danger").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form, bootstyle="secondary").pack(side='left', padx=2)

        # Search
        search_frame = ttk.Frame(parent_frame)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Go", command=self.search_students).pack(side="left", padx=2)
        ttk.Button(search_frame, text="Show All", command=self.refresh_student_list).pack(side="left", padx=2)

        # Treeview
        columns = [f[0] for f in fields] + ['profile_picture_path']
        self.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', height=20)
        for key in columns:
            self.tree.heading(key, text=key.replace('_', ' ').title())
            self.tree.column(key, width=100)
        # Scrollbars
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(parent_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        self.refresh_student_list()

    def upload_profile_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.profile_pic_path.set(file_path)
            self.profile_pic_label.config(text=os.path.basename(file_path))

    def get_form_data(self):
        data = {k: v.get() for k, v in self.entries.items()}
        # Convert numeric fields
        for k in ['tenth_percent', 'twelfth_percent', 'course_id', 'academic_year_id']:
            if data[k]:
                try:
                    data[k] = float(data[k]) if 'percent' in k else int(data[k])
                except ValueError:
                    data[k] = None
        data['profile_picture_path'] = self.profile_pic_path.get() if self.profile_pic_path.get() else None
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
            self.clear_form()
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
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")

    def delete_student(self):
        if not hasattr(self, 'tree'):
            messagebox.showerror("Error", "Student list not initialized.")
            return
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
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {e}")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.profile_pic_path.set("")
        self.profile_pic_label.config(text="No file selected")
        self.tree.selection_remove(self.tree.selection())

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
            if key in self.entries:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, values[idx])
        # Profile picture
        if 'profile_picture_path' in self.tree['columns']:
            idx = self.tree['columns'].index('profile_picture_path')
            pic_path = values[idx]
            self.profile_pic_path.set(pic_path if pic_path else "")
            self.profile_pic_label.config(text=os.path.basename(pic_path) if pic_path else "No file selected")

    def search_students(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.refresh_student_list()
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for student in Student.get_all():
            if any(query in str(value).lower() for value in student.values()):
                values = [student.get(f) for f in self.tree['columns']]
                self.tree.insert('', 'end', values=values)
