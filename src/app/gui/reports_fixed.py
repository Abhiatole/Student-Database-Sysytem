import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from app.db.database import get_db_connection
from datetime import datetime
import csv
import tempfile
import os

class ReportsTab:
    def __init__(self, parent, master):
        self.master = master
        self.current_report_data = []
        self.setup_reports_tab(parent)

    def setup_reports_tab(self, parent_frame):
        # Configure main layout
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        
        # Header section
        header_frame = ttk.Frame(parent_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="📊 Reports & Analytics Dashboard", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(side="left")
        
        # Controls section
        controls_frame = ttk.LabelFrame(parent_frame, text="🔧 Report Configuration", 
                                       padding=20, bootstyle="info")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        controls_frame.columnconfigure(1, weight=1)
        
        # Report type selection
        ttk.Label(controls_frame, text="📋 Report Type:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.report_type_combo = ttk.Combobox(controls_frame, 
                                            values=["📊 Full Student List", 
                                                   "📈 Enrollment Report", 
                                                   "💰 Payment History"],
                                            font=("Segoe UI", 10),
                                            state="readonly")
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.report_type_combo.set("📊 Full Student List")
        
        # Generate button
        self.generate_btn = ttk.Button(controls_frame, text="🔄 Generate Report", 
                                      command=self.generate_report, 
                                      bootstyle="primary-solid",
                                      width=15)
        self.generate_btn.grid(row=0, column=2, padx=20, pady=5)
        
        # Main content area
        content_frame = ttk.Frame(parent_frame)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Data table
        self.setup_data_table(content_frame)
        
        # Export buttons
        export_frame = ttk.Frame(parent_frame)
        export_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        self.export_pdf_btn = ttk.Button(export_frame, text="📄 Export to PDF", 
                                        command=self.export_report_pdf,
                                        bootstyle="primary-solid",
                                        state="disabled")
        self.export_pdf_btn.pack(side="left", padx=5)
        
        self.export_csv_btn = ttk.Button(export_frame, text="📊 Export to CSV", 
                                        command=self.export_report_csv,
                                        bootstyle="success-solid",
                                        state="disabled")
        self.export_csv_btn.pack(side="left", padx=5)

    def setup_data_table(self, parent):
        """Setup the data table"""
        # Create treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.report_tree = ttk.Treeview(tree_frame, show="headings", 
                                       bootstyle="primary",
                                       selectmode="extended")
        self.report_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", 
                                   command=self.report_tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.report_tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", 
                                   command=self.report_tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.report_tree.configure(xscrollcommand=scrollbar_x.set)

    def generate_report(self):
        report_type = self.report_type_combo.get()
        if not report_type:
            messagebox.showwarning("Selection Error", "Please select a report type.")
            return
        
        # Clear existing data
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        self.report_tree["columns"] = []
        
        conn = get_db_connection()
        
        # Remove emoji prefixes for SQL queries
        clean_report_type = report_type.replace("📊 ", "").replace("📈 ", "").replace("💰 ", "")
        
        if clean_report_type == "Full Student List":
            query = """
                SELECT s.roll_number as 'Roll No', s.name as 'Name', 
                       s.email as 'Email', s.contact_number as 'Contact', 
                       s.enrollment_date as 'Enroll Date'
                FROM students s
                ORDER BY s.name;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif clean_report_type == "Enrollment Report":
            query = """
                SELECT s.enrollment_date as 'Date', s.roll_number as 'Roll No', 
                       s.name as 'Name',
                       CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END AS 'Status'
                FROM students s 
                ORDER BY s.enrollment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif clean_report_type == "Payment History":
            query = """
                SELECT p.payment_date as 'Date', s.name as 'Student', 
                       p.amount_paid as 'Amount', p.payment_type as 'Type'
                FROM payments p 
                JOIN students s ON p.student_id = s.student_id
                ORDER BY p.payment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        
        conn.close()
        
        if not self.current_report_data:
            messagebox.showinfo("No Data", "No data found for the selected report.")
            self.disable_export_buttons()
            return
        
        headers = list(self.current_report_data[0].keys())
        self.report_tree["columns"] = headers
        
        for col in headers:
            self.report_tree.heading(col, text=col, anchor="w")
            self.report_tree.column(col, width=120, anchor='w')
        
        for row in self.current_report_data:
            self.report_tree.insert("", "end", values=list(row))
        
        # Enable export buttons
        self.enable_export_buttons()

    def enable_export_buttons(self):
        """Enable all export buttons"""
        self.export_pdf_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")

    def disable_export_buttons(self):
        """Disable all export buttons"""
        self.export_pdf_btn.config(state="disabled")
        self.export_csv_btn.config(state="disabled")

    def export_report_pdf(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        
        report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace(" ", "_")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")], 
            title="Save Report As",
            initialfile=f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not file_path:
            return
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Header
            header = Paragraph(f"{report_type.replace('_', ' ').title()}", styles['Title'])
            elements.append(header)
            elements.append(Spacer(1, 20))
            
            # Prepare data
            headers = list(self.current_report_data[0].keys())
            data = [headers]
            
            for row in self.current_report_data:
                data.append(list(row))
            
            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            messagebox.showinfo("Export Successful", f"Report exported successfully!\nSaved to: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as PDF: {e}")

    def export_report_csv(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        
        report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace(" ", "_")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")], 
            title="Save Report As",
            initialfile=f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Column headers
                headers = list(self.current_report_data[0].keys())
                writer.writerow(headers)
                
                # Data rows
                for row in self.current_report_data:
                    writer.writerow(list(row))
            
            messagebox.showinfo("Export Successful", f"Report exported successfully!\nSaved to: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as CSV: {e}")
