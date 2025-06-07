import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.db.models import Student
from ttkbootstrap.tooltip import ToolTip
from PIL import Image, ImageTk
import os
import random
from datetime import datetime, timedelta
from app.db.database import get_db_connection

def ensure_deleted_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'deleted' not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN deleted INTEGER DEFAULT 0")
        conn.commit()
    conn.close()

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
        # For course_id and academic_year_id, extract the ID if selected from dropdown
        for k in ['course_id', 'academic_year_id']:
            if data[k] and '-' in data[k]:
                data[k] = int(data[k].split('-')[0].strip())
            elif data[k]:
                try:
                    data[k] = int(data[k])
                except ValueError:
                    pass  # Let validation handle it
        # Convert numeric fields
        for k in ['tenth_percent', 'twelfth_percent']:
            if data[k]:
                try:
                    data[k] = float(data[k])
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
            # Refresh dashboard
            from app.main import MainApplication
            app = self.winfo_toplevel().main_app_instance if hasattr(self.winfo_toplevel(), 'main_app_instance') else None
            if app and app.dashboard_tab_instance:
                app.dashboard_tab_instance.refresh_stats()
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
            updated = Student.update(student_id, data)
            if updated:
                self.refresh_student_list()
                messagebox.showinfo("Success", "Student updated successfully.")
                self.clear_form()
            else:
                messagebox.showwarning("Update Failed", "No changes were made or student not found.")
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
        roll_number = self.tree.item(selected[0])['values'][0]
        # Lookup student_id by roll_number
        from app.db.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            messagebox.showwarning("Delete Failed", "Student not found or could not be deleted.")
            return
        student_id = row[0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            try:
                deleted = Student.delete(student_id)
                if deleted:
                    self.refresh_student_list()
                    messagebox.showinfo("Success", "Student deleted successfully.")
                    self.clear_form()
                    # Refresh dashboard
                    from app.main import MainApplication
                    app = self.winfo_toplevel().main_app_instance if hasattr(self.winfo_toplevel(), 'main_app_instance') else None
                    if app and app.dashboard_tab_instance:
                        app.dashboard_tab_instance.refresh_stats()
                else:
                    messagebox.showwarning("Delete Failed", "Student not found or could not be deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {e}")

    def batch_delete_students(self):
        if not hasattr(self, 'tree'):
            messagebox.showerror("Error", "Student list not initialized.")
            return
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Students", "Select students to delete.")
            return
        if not messagebox.askyesno("Confirm Batch Delete", f"Are you sure you want to delete {len(selected_items)} students?"):
            return
        deleted_count = 0
        for item in selected_items:
            roll_number = self.tree.item(item)['values'][1]  # [1] because [0] is student_id
            from app.db.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
            row = cursor.fetchone()
            conn.close()
            if row:
                student_id = row[0]
                try:
                    if Student.delete(student_id):
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting student: {e}")
        self.refresh_student_list()
        messagebox.showinfo("Batch Delete", f"Deleted {deleted_count} students.")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.profile_pic_path.set("")
        self.profile_pic_label.config(text="No file selected")
        if hasattr(self, 'tree'):
            self.tree.selection_remove(self.tree.selection())
        messagebox.showinfo("Cleared", "Form cleared.")

    def refresh_student_list(self):
        if not hasattr(self, 'tree'):
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        students = Student.get_all()
        if not students:
            messagebox.showinfo("No Data", "No students found in the database.")
        for student in students:
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

    def generate_sample_students(self):
        first_names = ["Amit", "Priya", "Rahul", "Sneha", "Vikas", "Anjali", "Rohan", "Pooja", "Suresh", "Neha"]
        last_names = ["Sharma", "Patel", "Singh", "Gupta", "Mehta", "Jain", "Kumar", "Verma", "Reddy", "Chopra"]
        blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        genders = ["Male", "Female", "Other"]
        courses = [1, 2, 3, 4, 5]
        years = [1, 2, 3, 4, 5]

        used_roll_numbers = set()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT roll_number FROM students")
        existing_roll_numbers = set(row[0] for row in cursor.fetchall())
        for i in range(100):
            while True:
                roll_number = f"R{random.randint(10000,99999)}"
                if roll_number not in used_roll_numbers and roll_number not in existing_roll_numbers:
                    used_roll_numbers.add(roll_number)
                    break
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            contact_number = f"9{random.randint(100000000,999999999)}"
            email = f"{fname.lower()}.{lname.lower()}{random.randint(1,99)}@example.com"
            address = f"{random.randint(1,200)}, Main Street, City"
            aadhaar_no = f"{random.randint(100000000000,999999999999)}"
            dob = (datetime.now() - timedelta(days=random.randint(6000, 9000))).strftime("%Y-%m-%d")
            gender = random.choice(genders)
            tenth_percent = round(random.uniform(60, 99), 2)
            twelfth_percent = round(random.uniform(60, 99), 2)
            blood_group = random.choice(blood_groups)
            mother_name = f"{random.choice(first_names)} {lname}"
            enrollment_date = (datetime.now() - timedelta(days=random.randint(0, 1000))).strftime("%Y-%m-%d")
            course_id = random.choice(courses)
            academic_year_id = random.choice(years)
            profile_picture_path = None

            data = {
                "roll_number": roll_number,
                "name": name,
                "contact_number": contact_number,
                "email": email,
                "address": address,
                "aadhaar_no": aadhaar_no,
                "date_of_birth": dob,
                "gender": gender,
                "tenth_percent": tenth_percent,
                "twelfth_percent": twelfth_percent,
                "blood_group": blood_group,
                "mother_name": mother_name,
                "enrollment_date": enrollment_date,
                "course_id": course_id,
                "academic_year_id": academic_year_id,
                "profile_picture_path": profile_picture_path,
                "enrollment_status": 1
            }
            try:
                Student.create(data)
            except Exception as e:
                print(f"Error adding sample student: {e}")

        conn.close()
        self.refresh_student_list()
        messagebox.showinfo("Success", "100 random student entries added.")

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
            if key == "gender":
                entry = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], state="normal")
            elif key == "blood_group":
                entry = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="normal")
            elif key == "course_id":
                # Fetch course names from DB
                from app.db.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT course_id, course_name FROM courses")
                courses = cursor.fetchall()
                conn.close()
                course_options = [f"{row['course_id']} - {row['course_name']}" for row in courses]
                entry = ttk.Combobox(form_frame, values=course_options, state="normal")
            elif key == "academic_year_id":
                from app.db.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT year_id, year_name FROM academic_years")
                years = cursor.fetchall()
                conn.close()
                year_options = [f"{row['year_id']} - {row['year_name']}" for row in years]
                entry = ttk.Combobox(form_frame, values=year_options, state="normal")
            else:
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
        # Add "Move to Bin" button
        ttk.Button(btn_frame, text="Move to Bin", command=self.bulk_soft_delete, bootstyle="danger").pack(side='left', padx=2)
        # Add tooltip for "Move to Bin" button
        ToolTip(btn_frame.winfo_children()[-1], text="Move selected students to bin (soft delete)")

        # Add "Generate Sample Data" button
        sample_btn = ttk.Button(btn_frame, text="Generate 100 Sample Students", command=self.generate_sample_students, bootstyle="warning")
        sample_btn.pack(side='left', padx=2)
        ToolTip(sample_btn, text="Add 100 random student entries for demo/testing")

        # Search
        search_frame = ttk.Frame(parent_frame)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Go", command=self.search_students).pack(side="left", padx=2)
        ttk.Button(search_frame, text="Show All", command=self.refresh_student_list).pack(side="left", padx=2)

        # Treeview
        columns = ['student_id'] + [f[0] for f in fields] + ['profile_picture_path']
        self.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', height=20)
        for key in columns:
            self.tree.heading(key, text=key.replace('_', ' ').title())
            # Optionally hide the student_id column
            if key == 'student_id':
                self.tree.column(key, width=0, stretch=False)
            else:
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
        # For course_id and academic_year_id, extract the ID if selected from dropdown
        for k in ['course_id', 'academic_year_id']:
            if data[k] and '-' in data[k]:
                data[k] = int(data[k].split('-')[0].strip())
            elif data[k]:
                try:
                    data[k] = int(data[k])
                except ValueError:
                    pass  # Let validation handle it
        # Convert numeric fields
        for k in ['tenth_percent', 'twelfth_percent']:
            if data[k]:
                try:
                    data[k] = float(data[k])
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
            # Refresh dashboard
            from app.main import MainApplication
            app = self.winfo_toplevel().main_app_instance if hasattr(self.winfo_toplevel(), 'main_app_instance') else None
            if app and app.dashboard_tab_instance:
                app.dashboard_tab_instance.refresh_stats()
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
            updated = Student.update(student_id, data)
            if updated:
                self.refresh_student_list()
                messagebox.showinfo("Success", "Student updated successfully.")
                self.clear_form()
            else:
                messagebox.showwarning("Update Failed", "No changes were made or student not found.")
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
        roll_number = self.tree.item(selected[0])['values'][0]
        # Lookup student_id by roll_number
        from app.db.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            messagebox.showwarning("Delete Failed", "Student not found or could not be deleted.")
            return
        student_id = row[0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            try:
                deleted = Student.delete(student_id)
                if deleted:
                    self.refresh_student_list()
                    messagebox.showinfo("Success", "Student deleted successfully.")
                    self.clear_form()
                    # Refresh dashboard
                    from app.main import MainApplication
                    app = self.winfo_toplevel().main_app_instance if hasattr(self.winfo_toplevel(), 'main_app_instance') else None
                    if app and app.dashboard_tab_instance:
                        app.dashboard_tab_instance.refresh_stats()
                else:
                    messagebox.showwarning("Delete Failed", "Student not found or could not be deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {e}")

    def batch_delete_students(self):
        if not hasattr(self, 'tree'):
            messagebox.showerror("Error", "Student list not initialized.")
            return
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Students", "Select students to delete.")
            return
        if not messagebox.askyesno("Confirm Batch Delete", f"Are you sure you want to delete {len(selected_items)} students?"):
            return
        deleted_count = 0
        for item in selected_items:
            roll_number = self.tree.item(item)['values'][1]  # [1] because [0] is student_id
            from app.db.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
            row = cursor.fetchone()
            conn.close()
            if row:
                student_id = row[0]
                try:
                    if Student.delete(student_id):
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting student: {e}")
        self.refresh_student_list()
        messagebox.showinfo("Batch Delete", f"Deleted {deleted_count} students.")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.profile_pic_path.set("")
        self.profile_pic_label.config(text="No file selected")
        if hasattr(self, 'tree'):
            self.tree.selection_remove(self.tree.selection())
        messagebox.showinfo("Cleared", "Form cleared.")

    def refresh_student_list(self):
        if not hasattr(self, 'tree'):
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        students = Student.get_all()
        if not students:
            messagebox.showinfo("No Data", "No students found in the database.")
        for student in students:
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

    def generate_sample_students(self):
        first_names = ["Amit", "Priya", "Rahul", "Sneha", "Vikas", "Anjali", "Rohan", "Pooja", "Suresh", "Neha"]
        last_names = ["Sharma", "Patel", "Singh", "Gupta", "Mehta", "Jain", "Kumar", "Verma", "Reddy", "Chopra"]
        blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        genders = ["Male", "Female", "Other"]
        courses = [1, 2, 3, 4, 5]
        years = [1, 2, 3, 4, 5]

        used_roll_numbers = set()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT roll_number FROM students")
        existing_roll_numbers = set(row[0] for row in cursor.fetchall())
        for i in range(100):
            while True:
                roll_number = f"R{random.randint(10000,99999)}"
                if roll_number not in used_roll_numbers and roll_number not in existing_roll_numbers:
                    used_roll_numbers.add(roll_number)
                    break
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            contact_number = f"9{random.randint(100000000,999999999)}"
            email = f"{fname.lower()}.{lname.lower()}{random.randint(1,99)}@example.com"
            address = f"{random.randint(1,200)}, Main Street, City"
            aadhaar_no = f"{random.randint(100000000000,999999999999)}"
            dob = (datetime.now() - timedelta(days=random.randint(6000, 9000))).strftime("%Y-%m-%d")
            gender = random.choice(genders)
            tenth_percent = round(random.uniform(60, 99), 2)
            twelfth_percent = round(random.uniform(60, 99), 2)
            blood_group = random.choice(blood_groups)
            mother_name = f"{random.choice(first_names)} {lname}"
            enrollment_date = (datetime.now() - timedelta(days=random.randint(0, 1000))).strftime("%Y-%m-%d")
            course_id = random.choice(courses)
            academic_year_id = random.choice(years)
            profile_picture_path = None

            data = {
                "roll_number": roll_number,
                "name": name,
                "contact_number": contact_number,
                "email": email,
                "address": address,
                "aadhaar_no": aadhaar_no,
                "date_of_birth": dob,
                "gender": gender,
                "tenth_percent": tenth_percent,
                "twelfth_percent": twelfth_percent,
                "blood_group": blood_group,
                "mother_name": mother_name,
                "enrollment_date": enrollment_date,
                "course_id": course_id,
                "academic_year_id": academic_year_id,
                "profile_picture_path": profile_picture_path,
                "enrollment_status": 1
            }
            try:
                Student.create(data)
            except Exception as e:
                print(f"Error adding sample student: {e}")

        conn.close()
        self.refresh_student_list()
        messagebox.showinfo("Success", "100 random student entries added.")

class BinTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_bin_tab(parent)

    def setup_bin_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Deleted Students (Bin)", font=("Helvetica", 16, "bold"), bootstyle="danger").pack(pady=10)
        columns = ['student_id', 'roll_number', 'name', 'email', 'deleted']
        self.tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=120)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Restore Selected", command=self.restore_selected, bootstyle="success").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete Permanently", command=self.permanent_delete_selected, bootstyle="danger").pack(side='left', padx=2)
        self.refresh_bin()

    def refresh_bin(self):
        from app.db.models import Student
        for row in self.tree.get_children():
            self.tree.delete(row)
        for student in Student.get_bin():
            values = [student.get(f) for f in self.tree['columns']]
            self.tree.insert('', 'end', values=values)

    def restore_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Students", "Select students to restore.")
            return
        student_ids = [self.tree.item(item)['values'][0] for item in selected_items]
        from app.db.models import Student
        count = Student.restore(student_ids)
        self.refresh_bin()
        messagebox.showinfo("Restored", f"{count} students restored.")

    def permanent_delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Students", "Select students to permanently delete.")
            return
        if not messagebox.askyesno("Confirm", "This will permanently delete selected students. Continue?"):
            return
        student_ids = [self.tree.item(item)['values'][0] for item in selected_items]
        from app.db.models import Student
        count = Student.permanent_delete(student_ids)
        self.refresh_bin()
        messagebox.showinfo("Deleted", f"{count} students permanently deleted.")

class Student:
    # ...existing methods...

    @staticmethod
    def soft_delete(student_ids):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('UPDATE students SET deleted=1 WHERE student_id=?', [(sid,) for sid in student_ids])
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def restore(student_ids):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('UPDATE students SET deleted=0 WHERE student_id=?', [(sid,) for sid in student_ids])
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def permanent_delete(student_ids):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('DELETE FROM students WHERE student_id=?', [(sid,) for sid in student_ids])
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def get_all(include_deleted=False):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if include_deleted:
                cursor.execute('SELECT * FROM students')
            else:
                cursor.execute('SELECT * FROM students WHERE deleted=0')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_bin():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE deleted=1')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def bulk_soft_delete(student_ids):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select Students", "Select students to move to bin.")
            return
        student_ids = [self.tree.item(item)['values'][0] for item in selected_items]  # [0] is student_id
        if not messagebox.askyesno("Confirm", f"Move {len(student_ids)} students to bin?"):
            return
        from app.db.models import Student
        count = Student.soft_delete(student_ids)
        self.refresh_student_list()
        messagebox.showinfo("Moved to Bin", f"{count} students moved to bin.")
