import tkinter as tk
from ttkbootstrap import ttk
from app.db.database import get_db_connection
from tkinter import messagebox

class MarksTab:
    def __init__(self, parent):
        self.setup_marks_entry_tab(parent)

    def setup_marks_entry_tab(self, parent_frame):
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
        roll_number = self.marks_roll_entry.get().strip()
        course_name = self.marks_course_combobox.get().strip()
        semester = self.marks_semester_entry.get().strip()
        subject = self.marks_subject_entry.get().strip()
        marks_obtained = self.marks_obtained_entry.get().strip()
        max_marks = self.marks_max_entry.get().strip()
        grade = self.marks_grade_entry.get().strip()
        if not (roll_number and course_name and semester and subject and marks_obtained and max_marks and grade):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
            student_row = cursor.fetchone()
            cursor.execute("SELECT course_id FROM courses WHERE course_name=?", (course_name,))
            course_row = cursor.fetchone()
            if not student_row or not course_row:
                messagebox.showerror("Error", "Student or course not found.")
                return
            student_id = student_row[0]
            course_id = course_row[0]
            cursor.execute(
                "INSERT INTO marks (student_id, course_id, subject_name, semester, marks_obtained, max_marks, grade) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (student_id, course_id, subject, int(semester), float(marks_obtained), float(max_marks), grade)
            )
            conn.commit()
            messagebox.showinfo("Success", "Marks added successfully.")
            self.clear_marks_entry_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def clear_marks_entry_fields(self):
        self.marks_roll_entry.delete(0, tk.END)
        self.marks_course_combobox.set('')
        self.marks_semester_entry.delete(0, tk.END)
        self.marks_subject_entry.delete(0, tk.END)
        self.marks_obtained_entry.delete(0, tk.END)
        self.marks_max_entry.delete(0, tk.END)
        self.marks_grade_entry.delete(0, tk.END)

    def display_student_marks(self):
        roll_number = self.marks_roll_entry.get().strip()
        if not roll_number:
            messagebox.showwarning("Input Error", "Please enter a roll number to display marks.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
            student_row = cursor.fetchone()
            if not student_row:
                messagebox.showerror("Error", "Student not found.")
                return
            student_id = student_row[0]
            cursor.execute(
                "SELECT subject_name, semester, marks_obtained, max_marks, grade FROM marks WHERE student_id = ?",
                (student_id,),
            )
            rows = cursor.fetchall()
            for row in self.marks_tree.get_children():
                self.marks_tree.delete(row)
            if not rows:
                messagebox.showinfo("No Data", "No marks found for the given roll number.")
                return
            for row in rows:
                self.marks_tree.insert("", "end", values=row)
            messagebox.showinfo("Success", "Marks displayed successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
