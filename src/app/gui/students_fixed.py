import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import uuid
import csv
import tempfile
import subprocess
import platform
import random
from app.db.models import Student
from ttkbootstrap.tooltip import ToolTip
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from app.db.database import get_db_connection

def ensure_deleted_column():
    from app.db.database import get_db_connection
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
        self.checked_items = set()
        self.create_widgets()
        self.refresh_student_list()

    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left side - Form
        form_frame = ttk.LabelFrame(main_container, text="Student Details", padding=15)
        form_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Configure form_frame grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        
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
            ttk.Label(form_frame, text=label).grid(row=idx, column=0, sticky="w", pady=2, padx=(0, 5))
            
            if key == "gender":
                entry = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], state="readonly", width=25)
            elif key == "blood_group":
                entry = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly", width=25)
            elif key == "course_id":
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT course_id, course_name FROM courses")
                    courses = cursor.fetchall()
                    conn.close()
                    course_options = [f"{row['course_id']} - {row['course_name']}" for row in courses]
                    entry = ttk.Combobox(form_frame, values=course_options, state="readonly", width=25)
                except:
                    entry = ttk.Entry(form_frame, width=25)
            elif key == "academic_year_id":
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT year_id, year_name FROM academic_years")
                    years = cursor.fetchall()
                    conn.close()
                    year_options = [f"{row['year_id']} - {row['year_name']}" for row in years]
                    entry = ttk.Combobox(form_frame, values=year_options, state="readonly", width=25)
                except:
                    entry = ttk.Entry(form_frame, width=25)
            else:
                entry = ttk.Entry(form_frame, width=25)
            
            entry.grid(row=idx, column=1, pady=2, sticky="ew")
            self.entries[key] = entry

        # Profile picture section
        profile_row = len(fields)
        ttk.Label(form_frame, text="Profile Picture:").grid(row=profile_row, column=0, sticky="w", pady=2)
        
        # Profile picture frame
        pic_frame = ttk.Frame(form_frame)
        pic_frame.grid(row=profile_row, column=1, sticky="ew", pady=2)
        
        self.profile_pic_path = tk.StringVar()
        self.profile_pic_label = ttk.Label(pic_frame, text="No file selected", foreground="gray")
        self.profile_pic_label.pack(side='left', fill='x', expand=True)
        
        upload_btn = ttk.Button(pic_frame, text="📁 Upload", command=self.upload_profile_picture, width=12)
        upload_btn.pack(side='right', padx=(5, 0))

        # Main action buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=profile_row+1, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="➕ Add", command=self.add_student, bootstyle="success", width=12).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="✏️ Update", command=self.update_student, bootstyle="info", width=12).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_student, bootstyle="danger", width=12).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🧹 Clear", command=self.clear_form, bootstyle="secondary", width=12).pack(side='left', padx=2)

        # Utility buttons
        utility_frame = ttk.Frame(form_frame)
        utility_frame.grid(row=profile_row+2, column=0, columnspan=2, pady=5)
        
        ttk.Button(utility_frame, text="🖨️ Print", command=self.print_student_record, bootstyle="primary", width=12).pack(side='left', padx=2)
        ttk.Button(utility_frame, text="📄 Export", command=self.export_student_data, bootstyle="warning", width=12).pack(side='left', padx=2)
        ttk.Button(utility_frame, text="🖼️ View Photo", command=self.view_profile_picture, bootstyle="info-outline", width=12).pack(side='left', padx=2)

        # Right side - Student list and search
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Search section
        search_frame = ttk.LabelFrame(right_frame, text="Search Students", padding=10)
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_container = ttk.Frame(search_frame)
        search_container.pack(fill='x')
        
        ttk.Label(search_container, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_container, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(5, 10))
        
        ttk.Button(search_container, text="🔍 Search", command=self.search_students, bootstyle="outline-primary").pack(side="left", padx=2)
        ttk.Button(search_container, text="📋 Show All", command=self.refresh_student_list, bootstyle="outline-secondary").pack(side="left", padx=2)

        # Student list section
        list_frame = ttk.LabelFrame(right_frame, text="Student Records", padding=10)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview with scrollbars
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill='both', expand=True)
        
        columns = ['roll_number', 'name', 'contact_number', 'email', 'gender', 'course_id', 'profile_picture_path']
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = {
            'roll_number': 100,
            'name': 150,
            'contact_number': 120,
            'email': 180,
            'gender': 80,
            'course_id': 100,
            'profile_picture_path': 0  # Hidden
        }
        
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            width = column_widths.get(col, 100)
            if col == 'profile_picture_path':
                self.tree.column(col, width=0, stretch=False)  # Hide this column
            else:
                self.tree.column(col, width=width, minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        search_entry.bind('<Return>', lambda e: self.search_students())

    def upload_profile_picture(self):
        """Enhanced profile picture upload with validation"""
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Validate image
                img = Image.open(file_path)
                
                # Create profile pictures directory
                profile_pics_dir = os.path.join(os.path.dirname(__file__), "..", "..", "profile_pictures")
                os.makedirs(profile_pics_dir, exist_ok=True)
                
                # Generate unique filename
                file_extension = os.path.splitext(file_path)[1]
                new_filename = f"profile_{uuid.uuid4().hex[:8]}{file_extension}"
                new_path = os.path.join(profile_pics_dir, new_filename)
                
                # Resize and save image
                img_resized = img.resize((150, 150), Image.Resampling.LANCZOS)
                img_resized.save(new_path, quality=90)
                
                # Update UI
                self.profile_pic_path.set(new_path)
                self.profile_pic_label.config(text=f"✅ {os.path.basename(new_path)}", foreground="green")
                
                messagebox.showinfo("Success", "Profile picture uploaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {e}")

    def print_student_record(self):
        """Print selected student record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student record to print.")
            return
            
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                pdf_path = tmp_file.name
            
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], 
                                       fontSize=18, textColor=colors.darkblue, 
                                       alignment=1, spaceAfter=20)
            story.append(Paragraph("Student Record Report", title_style))
            story.append(Spacer(1, 12))
            
            # Process selected student
            for item in selected:
                values = self.tree.item(item)['values']
                
                # Student info
                student_name = values[1] if len(values) > 1 else 'N/A'
                roll_number = values[0] if len(values) > 0 else 'N/A'
                
                header_style = ParagraphStyle('Header', parent=styles['Heading2'],
                                            fontSize=14, textColor=colors.blue,
                                            spaceBefore=20, spaceAfter=10)
                story.append(Paragraph(f"Student: {student_name} (Roll: {roll_number})", header_style))
                
                # Create table
                field_names = ['Roll Number', 'Name', 'Contact', 'Email', 'Gender', 'Course ID']
                data = [['Field', 'Value']]
                
                for i, field in enumerate(field_names):
                    if i < len(values):
                        data.append([field, str(values[i]) if values[i] else 'N/A'])
                
                table = Table(data, colWidths=[2*inch, 3.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Footer
            footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                        fontSize=10, textColor=colors.grey,
                                        alignment=1, spaceBefore=30)
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            doc.build(story)
            
            # Open PDF
            try:
                if platform.system() == 'Windows':
                    os.startfile(pdf_path)
                else:
                    subprocess.call(['open', pdf_path] if platform.system() == 'Darwin' else ['xdg-open', pdf_path])
                messagebox.showinfo("Success", f"PDF generated successfully!\nSaved at: {pdf_path}")
            except:
                messagebox.showinfo("PDF Created", f"PDF saved at: {pdf_path}")
                
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to generate PDF: {e}")

    def export_student_data(self):
        """Export selected student data to CSV"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select student(s) to export.")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Roll Number', 'Name', 'Contact', 'Email', 'Gender', 'Course ID']
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                
                for item in selected:
                    values = self.tree.item(item)['values']
                    row_data = [str(v) if v else '' for v in values[:6]]  # First 6 columns
                    writer.writerow(row_data)
                        
            messagebox.showinfo("Export Complete", f"Data exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def view_profile_picture(self):
        """View profile picture of selected student"""
        selected = self.tree.selection()
        
        if not selected:
            pic_path = self.profile_pic_path.get()
            if pic_path and os.path.exists(pic_path):
                self._show_profile_picture(pic_path)
            else:
                messagebox.showwarning("No Selection", "Please select a student or upload a profile picture.")
            return
            
        # Get profile picture from selected student
        values = self.tree.item(selected[0])['values']
        if len(values) > 6 and values[6]:  # profile_picture_path is last column
            pic_path = values[6]
            if os.path.exists(pic_path):
                self._show_profile_picture(pic_path)
            else:
                messagebox.showwarning("File Not Found", "Profile picture file not found.")
        else:
            messagebox.showinfo("No Profile Picture", "Selected student has no profile picture.")

    def _show_profile_picture(self, pic_path):
        """Display profile picture in popup"""
        try:
            popup = tk.Toplevel(self)
            popup.title("Profile Picture")
            popup.geometry("400x450")
            popup.resizable(False, False)
            
            # Center popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - 200
            y = (popup.winfo_screenheight() // 2) - 225
            popup.geometry(f"400x450+{x}+{y}")
            
            # Load and display image
            img = Image.open(pic_path)
            img_resized = img.resize((350, 350), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_resized)
            
            img_label = tk.Label(popup, image=photo)
            img_label.image = photo  # Keep reference
            img_label.pack(pady=20)
            
            # File info
            info_label = tk.Label(popup, text=f"File: {os.path.basename(pic_path)}", 
                                font=("Arial", 10))
            info_label.pack()
            
            # Close button
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Display Error", f"Failed to display image: {e}")

    def get_form_data(self):
        """Get data from form fields"""
        data = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            
            # Handle dropdown values
            if key in ['course_id', 'academic_year_id'] and '-' in value:
                try:
                    data[key] = int(value.split('-')[0].strip())
                except:
                    data[key] = value
            elif key in ['tenth_percent', 'twelfth_percent'] and value:
                try:
                    data[key] = float(value)
                except:
                    data[key] = None
            else:
                data[key] = value if value else None
                
        data['profile_picture_path'] = self.profile_pic_path.get() if self.profile_pic_path.get() else None
        return data

    def add_student(self):
        """Add new student"""
        data = self.get_form_data()
        
        if not data.get('roll_number') or not data.get('name'):
            messagebox.showerror("Validation Error", "Roll Number and Name are required.")
            return
            
        data['enrollment_status'] = 1
        
        try:
            Student.create(data)
            self.refresh_student_list()
            self.clear_form()
            messagebox.showinfo("Success", "Student added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")

    def update_student(self):
        """Update selected student"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student to update.")
            return
            
        # Get student ID - we need to get it from the database based on roll number
        roll_number = self.tree.item(selected[0])['values'][0]
        data = self.get_form_data()
        
        try:
            # Find student by roll number and update
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE roll_number = ?", (roll_number,))
            result = cursor.fetchone()
            
            if result:
                student_id = result['student_id']
                updated = Student.update(student_id, data)
                if updated:
                    self.refresh_student_list()
                    self.clear_form()
                    messagebox.showinfo("Success", "Student updated successfully!")
                else:
                    messagebox.showwarning("Update Failed", "No changes were made.")
            else:
                messagebox.showerror("Error", "Student not found.")
                
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")

    def delete_student(self):
        """Delete selected student"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select student(s) to delete.")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Move selected student(s) to bin?"):
            return
            
        try:
            roll_numbers = [self.tree.item(item)['values'][0] for item in selected]
            
            # Get student IDs from roll numbers
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in roll_numbers)
            cursor.execute(f"SELECT student_id FROM students WHERE roll_number IN ({placeholders})", roll_numbers)
            student_ids = [row['student_id'] for row in cursor.fetchall()]
            conn.close()
            
            if student_ids:
                count = Student.soft_delete(student_ids)
                self.refresh_student_list()
                self.clear_form()
                messagebox.showinfo("Moved to Bin", f"{count} student(s) moved to bin.")
            else:
                messagebox.showerror("Error", "Students not found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete students: {e}")

    def clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            if hasattr(entry, 'delete'):
                entry.delete(0, tk.END)
            elif hasattr(entry, 'set'):
                entry.set('')
                
        self.profile_pic_path.set("")
        self.profile_pic_label.config(text="No file selected", foreground="gray")
        
        if hasattr(self, 'tree'):
            self.tree.selection_remove(self.tree.selection())

    def refresh_student_list(self):
        """Refresh the student list"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            for student in Student.get_all():
                values = [
                    student.get('roll_number', ''),
                    student.get('name', ''),
                    student.get('contact_number', ''),
                    student.get('email', ''),
                    student.get('gender', ''),
                    student.get('course_id', ''),
                    student.get('profile_picture_path', '')
                ]
                self.tree.insert('', 'end', values=values)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def on_tree_select(self, event):
        """Handle tree selection"""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0])['values']
        
        # Load data into form
        field_mapping = {
            0: 'roll_number',
            1: 'name', 
            2: 'contact_number',
            3: 'email',
            4: 'gender',
            5: 'course_id'
        }
        
        for idx, field_key in field_mapping.items():
            if idx < len(values) and field_key in self.entries:
                entry = self.entries[field_key]
                if hasattr(entry, 'delete'):
                    entry.delete(0, tk.END)
                    entry.insert(0, str(values[idx]) if values[idx] else '')
                elif hasattr(entry, 'set'):
                    entry.set(str(values[idx]) if values[idx] else '')
        
        # Handle profile picture
        if len(values) > 6 and values[6]:
            self.profile_pic_path.set(values[6])
            self.profile_pic_label.config(text=f"✅ {os.path.basename(values[6])}", foreground="green")
        else:
            self.profile_pic_path.set("")
            self.profile_pic_label.config(text="No file selected", foreground="gray")

    def search_students(self):
        """Search students"""
        query = self.search_var.get().strip().lower()
        if not query:
            self.refresh_student_list()
            return
            
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            for student in Student.get_all():
                # Check if query matches any field
                student_text = ' '.join([
                    str(student.get('roll_number', '')),
                    str(student.get('name', '')),
                    str(student.get('contact_number', '')),
                    str(student.get('email', '')),
                    str(student.get('gender', ''))
                ]).lower()
                
                if query in student_text:
                    values = [
                        student.get('roll_number', ''),
                        student.get('name', ''),
                        student.get('contact_number', ''),
                        student.get('email', ''),
                        student.get('gender', ''),
                        student.get('course_id', ''),
                        student.get('profile_picture_path', '')
                    ]
                    self.tree.insert('', 'end', values=values)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

# Simplified StudentManagementTab class for backward compatibility
class StudentManagementTab:
    def __init__(self, parent):
        self.parent_frame = parent
        self.student_frame = StudentManagementFrame(parent)
        
    def refresh_student_list(self):
        self.student_frame.refresh_student_list()
