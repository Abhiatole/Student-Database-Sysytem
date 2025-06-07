import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from app.db.database import get_db_connection
from app.utils.logger import log_delivery
from datetime import datetime
import csv
import tempfile
from app.utils.email_utils import EmailDialog, email_dialog_with_attachment
import os
import sys
from pdf2image import convert_from_path
from PIL import ImageTk, Image

class ReportsTab:
    def __init__(self, parent, master):
        self.master = master
        self.setup_reports_tab(parent)

    def setup_reports_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        controls_frame = ttk.LabelFrame(parent_frame, text="Generate & Export Reports", padding=15, bootstyle="info")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.columnconfigure(1, weight=1)
        ttk.Label(controls_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_type_combo = ttk.Combobox(controls_frame, values=["Full Student List", "Enrollment Report", "Payment History"])
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.report_type_combo.set("Full Student List")
        ttk.Button(controls_frame, text="Generate Report", command=self.generate_report, bootstyle="primary").grid(row=0, column=2, padx=10)
        output_frame = ttk.Frame(parent_frame)
        output_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.report_tree = ttk.Treeview(output_frame, show="headings", bootstyle="primary")
        self.report_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y = ttk.Scrollbar(output_frame, orient="vertical", command=self.report_tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.report_tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_x = ttk.Scrollbar(output_frame, orient="horizontal", command=self.report_tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.report_tree.configure(xscrollcommand=scrollbar_x.set)
        self.actions_frame = ttk.Frame(parent_frame)
        self.actions_frame.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.export_pdf_btn = ttk.Button(self.actions_frame, text="Export to PDF", command=self.export_report_pdf, state="disabled")
        self.export_pdf_btn.pack(side="left", padx=5)
        self.export_csv_btn = ttk.Button(self.actions_frame, text="Export to CSV", command=self.export_report_csv, state="disabled")
        self.export_csv_btn.pack(side="left", padx=5)
        self.share_email_btn = ttk.Button(self.actions_frame, text="Share via Email...", command=self.share_report_email, state="disabled")
        self.share_email_btn.pack(side="left", padx=5)

    def generate_report(self):
        report_type = self.report_type_combo.get()
        if not report_type:
            messagebox.showwarning("Selection Error", "Please select a report type.")
            return
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        self.report_tree["columns"] = []
        conn = get_db_connection()
        if report_type == "Full Student List":
            query = """
                SELECT s.roll_number as 'Roll No', s.name as 'Name', c.course_name as 'Course', \
                       ay.year_name as 'Year', f.faculty_name as 'Faculty', s.email as 'Email', \
                       s.contact_number as 'Contact', s.enrollment_date as 'Enroll Date'
                FROM students s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
                ORDER BY s.name;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif report_type == "Enrollment Report":
            query = """
                SELECT s.enrollment_date as 'Date', s.roll_number as 'Roll No', s.name as 'Name', \
                    c.course_name as 'Course', \
                    CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END AS 'Status'
                FROM students s JOIN courses c ON s.course_id = c.course_id
                ORDER BY s.enrollment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif report_type == "Payment History":
            query = """
                SELECT p.payment_date as 'Date', s.name as 'Student', p.amount_paid as 'Amount', \
                    p.payment_type as 'Type', p.receipt_number as 'Receipt#'
                FROM payments p JOIN students s ON p.student_id = s.student_id
                ORDER BY p.payment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        conn.close()
        if not self.current_report_data:
            messagebox.showinfo("No Data", "No data found for the selected report.")
            self.export_pdf_btn.config(state="disabled")
            self.export_csv_btn.config(state="disabled")
            self.share_email_btn.config(state="disabled")
            return
        headers = list(self.current_report_data[0].keys())
        self.report_tree["columns"] = headers
        for col in headers:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120, anchor='w')
        for row in self.current_report_data:
            self.report_tree.insert("", "end", values=list(row))
        self.export_pdf_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")
        self.share_email_btn.config(state="normal")

    def export_report_pdf(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        report_type = self.report_type_combo.get().replace(" ", "_")
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Save Report As")
        if not file_path:
            return
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            header = Paragraph(f"{report_type.replace('_', ' ').title()} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Title'])
            elements.append(header)
            elements.append(Spacer(1, 12))
            # Prepare data with Paragraphs for wrapping
            headers = list(self.current_report_data[0].keys())
            data = [headers]
            for row in self.current_report_data:
                data.append([Paragraph(str(cell), styles['Normal']) for cell in row])
            # Set column widths
            page_width = letter[0] - 2 * doc.leftMargin
            ncols = len(headers)
            col_width = max(page_width / ncols, 60)  # Minimum width for readability
            table = Table(data, colWidths=[col_width]*ncols, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8 if ncols > 6 else 10),
                ('FONTSIZE', (0, 0), (-1, -1), 7 if ncols > 6 else 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            messagebox.showinfo("Success", f"Report exported successfully as PDF:\n{file_path}")
            # Optionally open the PDF after export
            import sys, os
            try:
                if sys.platform == "win32":
                    os.startfile(file_path)
                elif sys.platform == "darwin":
                    os.system(f"open '{file_path}'")
                else:
                    os.system(f"xdg-open '{file_path}'")
            except Exception:
                pass
            # Log delivery with all required arguments
            log_delivery("PDF Report", file_path, "local", "file", "Success")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as PDF: {e}")

    def export_report_pdf_to_path(self, file_path):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        report_type = self.report_type_combo.get().replace(" ", "_")
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            header = Paragraph(f"{report_type.replace('_', ' ').title()} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Title'])
            elements.append(header)
            elements.append(Spacer(1, 12))
            # Prepare data with Paragraphs for wrapping
            headers = list(self.current_report_data[0].keys())
            data = [headers]
            for row in self.current_report_data:
                data.append([Paragraph(str(cell), styles['Normal']) for cell in row])
            # Set column widths
            page_width = letter[0] - 2 * doc.leftMargin
            ncols = len(headers)
            col_width = max(page_width / ncols, 60)  # Minimum width for readability
            table = Table(data, colWidths=[col_width]*ncols, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8 if ncols > 6 else 10),
                ('FONTSIZE', (0, 0), (-1, -1), 7 if ncols > 6 else 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            # Log delivery with all required arguments
            log_delivery("PDF Report", file_path, "local", "file", "Success")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as PDF: {e}")

    def export_report_csv(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        report_type = self.report_type_combo.get().replace(" ", "_")
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save Report As")
        if not file_path:
            return
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([f"{report_type} Report"])
                writer.writerow([])
                writer.writerow(list(self.current_report_data[0].keys()))
                for row in self.current_report_data:
                    writer.writerow(row)
            messagebox.showinfo("Success", f"Report exported successfully as CSV:\n{file_path}")
            log_delivery("CSV Report", file_path)
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as CSV: {e}")

    def share_report_email(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before sharing.")
            return
        # Export the report as a temporary PDF and attach it
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            self.export_report_pdf_to_path(tmp.name)
            email_dialog_with_attachment(self.master, tmp.name)

def preview_pdf(parent, pdf_path):
    try:
        # Convert first page of PDF to image
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if not images:
            raise Exception("No pages found in PDF.")
        img = images[0]
        # Resize for preview window
        img.thumbnail((800, 1000))
        preview_win = tk.Toplevel(parent)
        preview_win.title("PDF Preview")
        preview_win.geometry(f"{img.width}x{img.height+40}")
        tk.Label(preview_win, text="PDF Preview (first page)").pack()
        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(preview_win, image=tk_img)
        label.image = tk_img  # Keep reference
        label.pack()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Preview Error", f"Could not preview PDF: {e}")
