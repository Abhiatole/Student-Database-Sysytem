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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from collections import Counter

class ReportsTab:
    def __init__(self, parent, master):
        self.master = master
        self.current_report_data = []
        self.setup_reports_tab(parent)

    def setup_reports_tab(self, parent_frame):
        # Configure main layout
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        
        # Header section with title and description
        header_frame = ttk.Frame(parent_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Title with icon
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="📊 Reports & Analytics Dashboard", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(side="left")
        
        subtitle_label = ttk.Label(header_frame, text="Generate comprehensive reports and export data in multiple formats",
                                  font=("Segoe UI", 10), foreground="gray")
        subtitle_label.grid(row=1, column=0, columnspan=2, sticky="w")
        
        # Controls section with enhanced styling
        controls_frame = ttk.LabelFrame(parent_frame, text="🔧 Report Configuration", 
                                       padding=20, bootstyle="info")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        controls_frame.columnconfigure(1, weight=1)
        
        # Report type selection with icons
        ttk.Label(controls_frame, text="📋 Report Type:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.report_type_combo = ttk.Combobox(controls_frame, 
                                            values=["📊 Full Student List", 
                                                   "📈 Enrollment Report", 
                                                   "💰 Payment History",
                                                   "📚 Course Statistics",
                                                   "📅 Monthly Summary"],
                                            font=("Segoe UI", 10),
                                            state="readonly")
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.report_type_combo.set("📊 Full Student List")
        
        # Date range selection
        ttk.Label(controls_frame, text="📅 Date Range:", 
                 font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        date_frame = ttk.Frame(controls_frame)
        date_frame.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.date_from = ttk.DateEntry(date_frame, bootstyle="info")
        self.date_from.pack(side="left", padx=(0, 5))
        
        ttk.Label(date_frame, text="to").pack(side="left", padx=5)
        
        self.date_to = ttk.DateEntry(date_frame, bootstyle="info")
        self.date_to.pack(side="left", padx=(5, 0))
        
        # Action buttons with icons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=0, column=2, rowspan=2, padx=20, pady=5)
        
        self.generate_btn = ttk.Button(buttons_frame, text="🔄 Generate Report", 
                                      command=self.generate_report, 
                                      bootstyle="primary-solid",
                                      width=15)
        self.generate_btn.pack(pady=2)
        
        self.preview_btn = ttk.Button(buttons_frame, text="👁️ Quick Preview", 
                                     command=self.show_quick_preview, 
                                     bootstyle="info-outline",
                                     width=15,
                                     state="disabled")
        self.preview_btn.pack(pady=2)
        
        # Statistics cards
        stats_frame = ttk.Frame(parent_frame)
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        self.create_stats_cards(stats_frame)
        
        # Main content area with tabs
        content_frame = ttk.Frame(parent_frame)
        content_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(content_frame, bootstyle="primary")
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Data table tab
        self.setup_data_tab()
        
        # Charts tab
        self.setup_charts_tab()
        
        # Export tab
        self.setup_export_tab()

    def create_stats_cards(self, parent):
        """Create attractive statistics cards"""
        parent.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Total Students Card
        total_card = ttk.LabelFrame(parent, text="👥 Total Students", 
                                   bootstyle="success", padding=10)
        total_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.total_students_label = ttk.Label(total_card, text="0", 
                                            font=("Segoe UI", 20, "bold"),
                                            foreground="#28a745")
        self.total_students_label.pack()
        
        # Active Enrollments Card
        active_card = ttk.LabelFrame(parent, text="✅ Active Enrollments", 
                                    bootstyle="info", padding=10)
        active_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.active_enrollments_label = ttk.Label(active_card, text="0", 
                                                font=("Segoe UI", 20, "bold"),
                                                foreground="#17a2b8")
        self.active_enrollments_label.pack()
        
        # Total Revenue Card
        revenue_card = ttk.LabelFrame(parent, text="💰 Total Revenue", 
                                     bootstyle="warning", padding=10)
        revenue_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.total_revenue_label = ttk.Label(revenue_card, text="₹0", 
                                           font=("Segoe UI", 20, "bold"),
                                           foreground="#ffc107")
        self.total_revenue_label.pack()
        
        # Recent Payments Card
        recent_card = ttk.LabelFrame(parent, text="📅 This Month", 
                                    bootstyle="secondary", padding=10)
        recent_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        self.recent_payments_label = ttk.Label(recent_card, text="0", 
                                             font=("Segoe UI", 20, "bold"),
                                             foreground="#6c757d")
        self.recent_payments_label.pack()
        
        # Update stats
        self.update_statistics()

    def setup_data_tab(self):
        """Setup the data table tab"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📋 Data Table")
        
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Create treeview with modern styling
        tree_frame = ttk.Frame(data_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Search frame
        search_frame = ttk.Frame(tree_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_data)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               font=("Segoe UI", 10))
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        clear_btn = ttk.Button(search_frame, text="❌", command=self.clear_search,
                              bootstyle="danger-outline", width=3)
        clear_btn.grid(row=0, column=2)
        
        # Treeview
        self.report_tree = ttk.Treeview(tree_frame, show="headings", 
                                       bootstyle="primary",
                                       selectmode="extended")
        self.report_tree.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", 
                                   command=self.report_tree.yview)
        scrollbar_y.grid(row=1, column=1, sticky="ns")
        self.report_tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", 
                                   command=self.report_tree.xview)
        scrollbar_x.grid(row=2, column=0, sticky="ew")
        self.report_tree.configure(xscrollcommand=scrollbar_x.set)
        
        # Row count label
        self.row_count_label = ttk.Label(tree_frame, text="No data loaded", 
                                        font=("Segoe UI", 9),
                                        foreground="gray")
        self.row_count_label.grid(row=3, column=0, sticky="w", pady=(5, 0))

    def setup_charts_tab(self):
        """Setup the charts visualization tab"""
        charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(charts_frame, text="📊 Charts")
        
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)
        
        # Chart controls
        chart_controls = ttk.Frame(charts_frame)
        chart_controls.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Label(chart_controls, text="📈 Chart Type:", 
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
        
        self.chart_type_combo = ttk.Combobox(chart_controls, 
                                           values=["Bar Chart", "Pie Chart", "Line Chart", "Histogram"],
                                           state="readonly")
        self.chart_type_combo.pack(side="left", padx=5)
        self.chart_type_combo.set("Bar Chart")
        
        ttk.Button(chart_controls, text="🔄 Generate Chart", 
                  command=self.generate_chart,
                  bootstyle="primary").pack(side="left", padx=10)
        
        # Chart canvas
        self.chart_frame = ttk.Frame(charts_frame)
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def setup_export_tab(self):
        """Setup the export options tab"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📤 Export")
        
        export_frame.columnconfigure(0, weight=1)
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="📁 Export Options", 
                                     padding=20, bootstyle="info")
        options_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        options_frame.columnconfigure((0, 1), weight=1)
        
        # PDF Export
        pdf_frame = ttk.LabelFrame(options_frame, text="📄 PDF Export", 
                                 padding=15, bootstyle="primary")
        pdf_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=10)
        
        ttk.Label(pdf_frame, text="Export as professionally formatted PDF document").pack(anchor="w")
        
        self.export_pdf_btn = ttk.Button(pdf_frame, text="📄 Export to PDF", 
                                        command=self.export_report_pdf,
                                        bootstyle="primary-solid",
                                        state="disabled")
        self.export_pdf_btn.pack(pady=(10, 0), fill="x")
          # CSV Export
        csv_frame = ttk.LabelFrame(options_frame, text="📊 CSV Export", 
                                 padding=15, bootstyle="success")
        csv_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=10)
        
        ttk.Label(csv_frame, text="Export as comma-separated values for spreadsheets").pack(anchor="w")
        
        self.export_csv_btn = ttk.Button(csv_frame, text="📊 Export to CSV", 
                                        command=self.export_report_csv,
                                        bootstyle="success-solid",
                                        state="disabled")
        self.export_csv_btn.pack(pady=(10, 0), fill="x")
        
        # Email sharing
        email_frame = ttk.LabelFrame(export_frame, text="📧 Share via Email", 
                                   padding=20, bootstyle="warning")
        email_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        ttk.Label(email_frame, text="Share reports directly via email with attachments").pack(anchor="w")
        
        self.share_email_btn = ttk.Button(email_frame, text="📧 Share via Email", 
                                         command=self.share_report_email,
                                         bootstyle="warning-solid",
                                         state="disabled")
        self.share_email_btn.pack(pady=(10, 0), fill="x")
        
        # Print preview
        preview_frame = ttk.LabelFrame(export_frame, text="🖨️ Print Preview", 
                                     padding=20, bootstyle="secondary")
        preview_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        ttk.Label(preview_frame, text="Preview how the report will look when printed").pack(anchor="w")
        
        self.preview_print_btn = ttk.Button(preview_frame, text="🖨️ Print Preview", 
                                           command=self.show_print_preview,
                                           bootstyle="secondary-solid",
                                           state="disabled")
        self.preview_print_btn.pack(pady=(10, 0), fill="x")

    def update_statistics(self):
            """Update the statistics cards with current data"""
            try:
                conn = get_db_connection()
            
                # Total students
                total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                self.total_students_label.config(text=str(total_students))
                
                # Active enrollments
                active_enrollments = conn.execute(
                    "SELECT COUNT(*) FROM students WHERE enrollment_status = 1"
                ).fetchone()[0]
                self.active_enrollments_label.config(text=str(active_enrollments))
                
                # Total revenue
                total_revenue = conn.execute(
                    "SELECT COALESCE(SUM(amount_paid), 0) FROM payments"
                ).fetchone()[0]
                self.total_revenue_label.config(text=f"₹{total_revenue:,.2f}")
                
                # Recent payments (this month)
                recent_payments = conn.execute(
                    """SELECT COUNT(*) FROM payments 
                       WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')"""
                ).fetchone()[0]
                self.recent_payments_label.config(text=str(recent_payments))
                
                conn.close()
            except Exception as e:
                print(f"Error updating statistics: {e}")

    def clear_search(self):
        """Clear the search filter"""
        self.search_var.set("")

    def filter_data(self, *args):
        """Filter the data table based on search term"""
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            return
        
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Filter and display data
        filtered_count = 0
        for row in self.current_report_data:
            row_text = ' '.join(str(value).lower() for value in row)
            if search_term in row_text:
                self.report_tree.insert("", "end", values=list(row))
                filtered_count += 1
        
        # Update row count
        total_count = len(self.current_report_data)
        if search_term:
            self.row_count_label.config(text=f"Showing {filtered_count} of {total_count} records")
        else:
            self.row_count_label.config(text=f"Total records: {total_count}")

    def show_quick_preview(self):
        """Show a quick preview of the current report"""
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first.")
            return
        
        preview_window = tk.Toplevel(self.master)
        preview_window.title("📋 Quick Preview")
        preview_window.geometry("800x600")
        preview_window.configure(bg='white')
        
        # Header
        header_frame = ttk.Frame(preview_window)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "")
        ttk.Label(header_frame, text=f"Preview: {report_type}", 
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(header_frame, text=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        
        # Summary
        summary_frame = ttk.LabelFrame(preview_window, text="📊 Summary", padding=10)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        total_records = len(self.current_report_data)
        headers = list(self.current_report_data[0].keys()) if self.current_report_data else []
        
        ttk.Label(summary_frame, text=f"Total Records: {total_records}").pack(anchor="w")
        ttk.Label(summary_frame, text=f"Columns: {len(headers)}").pack(anchor="w")
        
        # Sample data
        sample_frame = ttk.LabelFrame(preview_window, text="📋 Sample Data (First 5 Records)", padding=10)
        sample_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create a text widget for sample data
        text_widget = tk.Text(sample_frame, wrap="none", font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True)
        
        # Add headers
        if headers:
            header_line = " | ".join(f"{header:<15}" for header in headers)
            text_widget.insert("end", header_line + "\n")
            text_widget.insert("end", "-" * len(header_line) + "\n")
            
            # Add sample rows (first 5)
            for i, row in enumerate(self.current_report_data[:5]):
                row_line = " | ".join(f"{str(value):<15}" for value in row)
                text_widget.insert("end", row_line + "\n")
        
        text_widget.config(state="disabled")

    def generate_chart(self):
        """Generate charts based on current data"""
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first.")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        chart_type = self.chart_type_combo.get()
        report_type = self.report_type_combo.get()
        
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('white')
            
            if "Payment History" in report_type:
                self.create_payment_chart(ax, chart_type)
            elif "Enrollment Report" in report_type:
                self.create_enrollment_chart(ax, chart_type)
            elif "Course Statistics" in report_type:
                self.create_course_chart(ax, chart_type)
            else:
                self.create_general_chart(ax, chart_type)
            
            # Embed chart in tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Error generating chart: {e}")

    def create_payment_chart(self, ax, chart_type):
        """Create payment-related charts"""
        conn = get_db_connection()
        data = conn.execute("""
            SELECT strftime('%Y-%m', payment_date) as month, SUM(amount_paid) as total
            FROM payments 
            GROUP BY strftime('%Y-%m', payment_date)
            ORDER BY month
        """).fetchall()
        conn.close()
        
        if not data:
            ax.text(0.5, 0.5, 'No payment data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return
        
        months = [row[0] for row in data]
        amounts = [row[1] for row in data]
        
        if chart_type == "Bar Chart":
            bars = ax.bar(months, amounts, color='#17a2b8', alpha=0.7)
            ax.set_title('Monthly Payment Revenue', fontsize=14, fontweight='bold')
            ax.set_ylabel('Amount (₹)')
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₹{amount:,.0f}', ha='center', va='bottom')
        
        elif chart_type == "Line Chart":
            ax.plot(months, amounts, marker='o', linewidth=2, markersize=6, color='#17a2b8')
            ax.fill_between(months, amounts, alpha=0.3, color='#17a2b8')
            ax.set_title('Payment Trend Over Time', fontsize=14, fontweight='bold')
            ax.set_ylabel('Amount (₹)')
        
        plt.xticks(rotation=45)
        plt.tight_layout()

    def create_enrollment_chart(self, ax, chart_type):
        """Create enrollment-related charts"""
        conn = get_db_connection()
        data = conn.execute("""
            SELECT c.course_name, COUNT(s.student_id) as count
            FROM courses c
            LEFT JOIN students s ON c.course_id = s.course_id AND s.enrollment_status = 1
            GROUP BY c.course_id, c.course_name
            ORDER BY count DESC
        """).fetchall()
        conn.close()
        
        if not data:
            ax.text(0.5, 0.5, 'No enrollment data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return
        
        courses = [row[0] for row in data]
        counts = [row[1] for row in data]
        
        if chart_type == "Bar Chart":
            bars = ax.bar(courses, counts, color='#28a745', alpha=0.7)
            ax.set_title('Enrollment by Course', fontsize=14, fontweight='bold')
            ax.set_ylabel('Number of Students')
            
            # Add value labels
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       str(count), ha='center', va='bottom')
        
        elif chart_type == "Pie Chart":
            colors = plt.cm.Set3(range(len(courses)))
            wedges, texts, autotexts = ax.pie(counts, labels=courses, autopct='%1.1f%%', 
                                            colors=colors, startangle=90)
            ax.set_title('Course Distribution', fontsize=14, fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()

    def create_course_chart(self, ax, chart_type):
        """Create course statistics charts"""
        # This would be implemented based on course data structure
        ax.text(0.5, 0.5, 'Course statistics chart\n(Implementation pending)', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=14)

    def create_general_chart(self, ax, chart_type):
        """Create general charts for student data"""
        conn = get_db_connection()
        data = conn.execute("""
            SELECT strftime('%Y-%m', enrollment_date) as month, COUNT(*) as count
            FROM students 
            GROUP BY strftime('%Y-%m', enrollment_date)
            ORDER BY month
        """).fetchall()
        conn.close()
        
        if not data:
            ax.text(0.5, 0.5, 'No student data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return
        
        months = [row[0] for row in data]
        counts = [row[1] for row in data]
        
        if chart_type == "Bar Chart":
            bars = ax.bar(months, counts, color='#ffc107', alpha=0.7)
            ax.set_title('Student Enrollments by Month', fontsize=14, fontweight='bold')
            ax.set_ylabel('Number of Students')
            
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       str(count), ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()

    def show_print_preview(self):
        """Show print preview of the report"""
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first.")
            return
        
        # Create a temporary PDF and show preview
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            self.export_report_pdf_to_path(tmp.name)
            preview_pdf(self.master, tmp.name)
            
            # Clean up temp file after preview
            def cleanup():
                try:
                    os.unlink(tmp.name)
                except:
                    pass
            
            self.master.after(5000, cleanup)  # Clean up after 5 seconds

    def generate_report(self):
        report_type = self.report_type_combo.get()
        if not report_type:
            messagebox.showwarning("Selection Error", "Please select a report type.")
            return
        
        # Clear existing data
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        self.report_tree["columns"] = []
        
        # Clear search
        self.search_var.set("")
        
        conn = get_db_connection()
        
        # Remove emoji prefixes for SQL queries
        clean_report_type = report_type.replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace("📚 ", "").replace("📅 ", "")
        
        if clean_report_type == "Full Student List":
            query = """
                SELECT s.roll_number as 'Roll No', s.name as 'Name', c.course_name as 'Course', 
                       ay.year_name as 'Year', f.faculty_name as 'Faculty', s.email as 'Email', 
                       s.contact_number as 'Contact', s.enrollment_date as 'Enroll Date'
                FROM students s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN academic_years ay ON s.academic_year_id = ay.year_id
                LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
                ORDER BY s.name;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif clean_report_type == "Enrollment Report":
            query = """
                SELECT s.enrollment_date as 'Date', s.roll_number as 'Roll No', s.name as 'Name', 
                    c.course_name as 'Course', 
                    CASE WHEN s.enrollment_status = 1 THEN 'Active' ELSE 'Inactive' END AS 'Status'
                FROM students s JOIN courses c ON s.course_id = c.course_id
                ORDER BY s.enrollment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif clean_report_type == "Payment History":
            query = """
                SELECT p.payment_date as 'Date', s.name as 'Student', p.amount_paid as 'Amount', 
                    p.payment_type as 'Type', p.receipt_number as 'Receipt#'
                FROM payments p JOIN students s ON p.student_id = s.student_id
                ORDER BY p.payment_date DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif clean_report_type == "Course Statistics":
            query = """
                SELECT c.course_name as 'Course', f.faculty_name as 'Faculty',
                       COUNT(s.student_id) as 'Enrolled Students',
                       COALESCE(SUM(p.amount_paid), 0) as 'Total Revenue'
                FROM courses c
                LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
                LEFT JOIN students s ON c.course_id = s.course_id
                LEFT JOIN payments p ON s.student_id = p.student_id
                GROUP BY c.course_id, c.course_name, f.faculty_name
                ORDER BY COUNT(s.student_id) DESC;
            """
            self.current_report_data = conn.execute(query).fetchall()
        elif clean_report_type == "Monthly Summary":
            query = """
                SELECT strftime('%Y-%m', s.enrollment_date) as 'Month',
                       COUNT(s.student_id) as 'New Enrollments',
                       COALESCE(SUM(p.amount_paid), 0) as 'Revenue'
                FROM students s
                LEFT JOIN payments p ON s.student_id = p.student_id 
                    AND strftime('%Y-%m', p.payment_date) = strftime('%Y-%m', s.enrollment_date)
                GROUP BY strftime('%Y-%m', s.enrollment_date)
                ORDER BY Month DESC;
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
        
        # Update UI elements
        self.enable_export_buttons()
        self.update_statistics()
        self.row_count_label.config(text=f"Total records: {len(self.current_report_data)}")
          # Switch to data tab
        self.notebook.select(0)    def enable_export_buttons(self):
        """Enable all export buttons"""
        self.export_pdf_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")
        self.share_email_btn.config(state="normal")
        self.preview_btn.config(state="normal")
        self.preview_print_btn.config(state="normal")

    def disable_export_buttons(self):
        """Disable all export buttons"""
        self.export_pdf_btn.config(state="disabled")
        self.export_csv_btn.config(state="disabled")
        self.share_email_btn.config(state="disabled")
        self.preview_btn.config(state="disabled")
        self.preview_print_btn.config(state="disabled")

    def export_report_pdf(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        
        report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace("📚 ", "").replace("📅 ", "").replace(" ", "_")
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
            
            # Enhanced header with styling
            title_style = styles['Title']
            title_style.fontSize = 18
            title_style.spaceAfter = 12
            
            header = Paragraph(f"{report_type.replace('_', ' ').title()}", title_style)
            elements.append(header)
                
                # Subtitle with generation info
                subtitle_style = styles['Normal']
                subtitle_style.fontSize = 10
                subtitle_style.textColor = colors.grey
                
                subtitle = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(self.current_report_data)}", subtitle_style)
                elements.append(subtitle)
                elements.append(Spacer(1, 20))
                
                # Prepare data with enhanced styling
                headers = list(self.current_report_data[0].keys())
                data = [headers]
                
                for row in self.current_report_data:
                    data.append([Paragraph(str(cell), styles['Normal']) for cell in row])
                
                # Enhanced table styling
                page_width = letter[0] - 2 * doc.leftMargin
                ncols = len(headers)
                col_width = max(page_width / ncols, 60)
                
                table = Table(data, colWidths=[col_width]*ncols, repeatRows=1)
                table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    
                    # Body styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ]))
                
                elements.append(table)
                
                # Footer
                elements.append(Spacer(1, 20))
                footer_style = styles['Normal']
                footer_style.fontSize = 8
                footer_style.textColor = colors.grey
                footer_style.alignment = 1  # Center alignment
                
                footer = Paragraph("Generated by Student Database Management System", footer_style)
                elements.append(footer)
                
                doc.build(elements)
                
                # Success message with option to open
                result = messagebox.askyesno("Export Successful", 
                                           f"Report exported successfully as PDF:\n{file_path}\n\nWould you like to open the file?")
                
                if result:
                    try:
                        if sys.platform == "win32":
                            os.startfile(file_path)
                        elif sys.platform == "darwin":
                            os.system(f"open '{file_path}'")
                        else:
                            os.system(f"xdg-open '{file_path}'")
                    except Exception:
                        pass
                  log_delivery("PDF Report", file_path, "local", "file", "Success")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting report as PDF: {e}")

    def export_report_csv(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        
        report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace("📚 ", "").replace("📅 ", "").replace(" ", "_")
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
                
                # Header information
                writer.writerow([f"{report_type.replace('_', ' ').title()} Report"])
                writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([f"Total Records: {len(self.current_report_data)}"])
                writer.writerow([])  # Empty row
                
                # Column headers
                headers = list(self.current_report_data[0].keys())
                writer.writerow(headers)
                
                # Data rows
                for row in self.current_report_data:
                    writer.writerow(list(row))
            
            # Success message with option to open
            result = messagebox.askyesno("Export Successful", 
                                       f"Report exported successfully as CSV:\n{file_path}\n\nWould you like to open the file?")
            
            if result:
                try:
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    elif sys.platform == "darwin":
                        os.system(f"open '{file_path}'")
                    else:
                        os.system(f"xdg-open '{file_path}'")
                except Exception:
                    pass
            
            log_delivery("CSV Report", file_path, "local", "file", "Success")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as CSV: {e}")

    def share_report_email(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before sharing.")
            return
        
        # Show progress
        progress_window = tk.Toplevel(self.master)
        progress_window.title("Preparing Email...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        
        ttk.Label(progress_window, text="Generating PDF for email attachment...").pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        def prepare_email():
            try:
                # Export the report as a temporary PDF
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    self.export_report_pdf_to_path(tmp.name)
                    
                    progress_window.destroy()
                    email_dialog_with_attachment(self.master, tmp.name)
                    
                    # Clean up temp file after some time
                    def cleanup():
                        try:
                            os.unlink(tmp.name)
                        except:
                            pass
                    
                    self.master.after(10000, cleanup)  # Clean up after 10 seconds
                    
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Email Error", f"Error preparing email: {e}")
        # Run email preparation in a separate thread to prevent UI freezing
        self.master.after(500, prepare_email)

    def export_report_pdf_to_path(self, file_path):
            """Export report to a specific path (used for email sharing)"""
            if not hasattr(self, 'current_report_data') or not self.current_report_data:
                raise Exception("No data available for export")
            
            report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace("📚 ", "").replace("📅 ", "").replace(" ", "_")
            
            try:
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                # Enhanced header
                title_style = styles['Title']
                title_style.fontSize = 18
                title_style.spaceAfter = 12
                
                header = Paragraph(f"{report_type.replace('_', ' ').title()}", title_style)
                elements.append(header)
                
                # Subtitle
                subtitle_style = styles['Normal']
                subtitle_style.fontSize = 10
                subtitle_style.textColor = colors.grey
                
                subtitle = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(self.current_report_data)}", subtitle_style)
                elements.append(subtitle)
                elements.append(Spacer(1, 20))
                
                # Prepare data
                headers = list(self.current_report_data[0].keys())
                data = [headers]
                
                for row in self.current_report_data:
                    data.append([Paragraph(str(cell), styles['Normal']) for cell in row])
                
                # Table styling
                page_width = letter[0] - 2 * doc.leftMargin
                ncols = len(headers)
                col_width = max(page_width / ncols, 60)
                
                table = Table(data, colWidths=[col_width]*ncols, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ]))
                
                elements.append(table)
                
                # Footer
                elements.append(Spacer(1, 20))
                footer_style = styles['Normal']
                footer_style.fontSize = 8
                footer_style.textColor = colors.grey
                footer_style.alignment = 1
                
                footer = Paragraph("Generated by Student Database Management System", footer_style)
                elements.append(footer)
                
                doc.build(elements)
                log_delivery("PDF Report", file_path, "local", "file", "Success")
                  except Exception as e:
                raise Exception(f"Error generating PDF: {e}")

    def export_report_csv(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before exporting.")
            return
        
        report_type = self.report_type_combo.get().replace("📊 ", "").replace("📈 ", "").replace("💰 ", "").replace("📚 ", "").replace("📅 ", "").replace(" ", "_")
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
                
                # Header information
                writer.writerow([f"{report_type.replace('_', ' ').title()} Report"])
                writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([f"Total Records: {len(self.current_report_data)}"])
                writer.writerow([])  # Empty row
                
                # Column headers
                headers = list(self.current_report_data[0].keys())
                writer.writerow(headers)
                
                # Data rows
                for row in self.current_report_data:
                    writer.writerow(list(row))
            
            # Success message with option to open
            result = messagebox.askyesno("Export Successful", 
                                       f"Report exported successfully as CSV:\n{file_path}\n\nWould you like to open the file?")
            
            if result:
                try:
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    elif sys.platform == "darwin":
                        os.system(f"open '{file_path}'")
                    else:
                        os.system(f"xdg-open '{file_path}'")
                except Exception:
                    pass
            
            log_delivery("CSV Report", file_path, "local", "file", "Success")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report as CSV: {e}")

    def share_report_email(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("No Data", "Generate a report first before sharing.")
            return
        
        # Show progress
        progress_window = tk.Toplevel(self.master)
        progress_window.title("Preparing Email...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        
        ttk.Label(progress_window, text="Generating PDF for email attachment...").pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        def prepare_email():
            try:
                # Export the report as a temporary PDF
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    self.export_report_pdf_to_path(tmp.name)
                    
                    progress_window.destroy()
                    email_dialog_with_attachment(self.master, tmp.name)
                    
                    # Clean up temp file after some time
                    def cleanup():
                        try:
                            os.unlink(tmp.name)
                        except:
                            pass
                    
                    self.master.after(10000, cleanup)  # Clean up after 10 seconds
                    
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Email Error", f"Error preparing email: {e}")
        
        # Run email preparation in a separate thread to prevent UI freezing
        self.master.after(500, prepare_email)

def preview_pdf(parent, pdf_path):
    """Enhanced PDF preview with better UI"""
    try:
        # Convert first page of PDF to image
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
        if not images:
            raise Exception("No pages found in PDF.")
        
        img = images[0]
        # Resize for preview window with better quality
        img.thumbnail((900, 1200), Image.Resampling.LANCZOS)
        
        preview_win = tk.Toplevel(parent)
        preview_win.title("📄 PDF Preview")
        preview_win.geometry(f"{img.width + 40}x{img.height + 80}")
        preview_win.configure(bg='white')
        
        # Header frame
        header_frame = ttk.Frame(preview_win)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(header_frame, text="📄 PDF Preview (First Page)", 
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        
        ttk.Button(header_frame, text="❌ Close", 
                  command=preview_win.destroy,
                  bootstyle="danger-outline").pack(side="right")
        
        # Image frame with border
        img_frame = ttk.Frame(preview_win, relief="solid", borderwidth=1)
        img_frame.pack(padx=10, pady=10)
        
        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(img_frame, image=tk_img, bg='white')
        label.image = tk_img  # Keep reference
        label.pack()
        
        # Center the window
        preview_win.transient(parent)
        preview_win.grab_set()
        
    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not preview PDF: {e}")
