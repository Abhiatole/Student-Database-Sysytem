import tkinter as tk
from ttkbootstrap import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.db.database import get_db_connection
from datetime import datetime

# Main dashboard logic and widgets

class DashboardTab:
    def __init__(self, parent, style, logo_img):
        self.style = style
        self.logo_img = logo_img
        self.setup_home_tab(parent)

    def setup_home_tab(self, parent_frame):
        self.parent_frame = parent_frame
        parent_frame.rowconfigure(0, weight=1)
        parent_frame.columnconfigure(0, weight=1)
        self.header_frame = ttk.Frame(parent_frame)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=10)
        if self.logo_img:
            ttk.Label(self.header_frame, image=self.logo_img).pack(side="left", padx=10)
        self.title_frame = ttk.Frame(self.header_frame)
        self.title_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(self.title_frame, text="Welcome to the Dashboard", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(anchor='w')
        ttk.Label(self.title_frame, text="Your central hub for student data management and insights.", font=("Helvetica", 12)).pack(anchor='w')
        self.content_frame = ttk.Frame(parent_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        self.stats_frame = ttk.Frame(self.content_frame, padding=10)
        self.stats_frame.grid(row=0, column=0, sticky="ns", padx=10)
        ttk.Label(self.stats_frame, text="Quick Statistics", font=("Helvetica", 14, "bold"), bootstyle="info").pack(pady=(0, 10), anchor='w')
        self.stat_cards = []
        self.chart_frame = ttk.LabelFrame(self.content_frame, text="Analytics Snapshot", padding=15, bootstyle="info")
        self.chart_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        self.footer_label = ttk.Label(parent_frame, text="@developed by Rushikesh Atole and Team", font=("Helvetica", 10, "italic"), bootstyle="secondary")
        self.footer_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.refresh_stats()

    def refresh_stats(self):
        # Clear previous stat cards and chart
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.stats_frame, text="Quick Statistics", font=("Helvetica", 14, "bold"), bootstyle="info").pack(pady=(0, 10), anchor='w')
        from app.db.database import get_db_connection
        conn = get_db_connection()
        total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        active_courses = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        total_revenue = conn.execute("SELECT SUM(amount_paid) FROM payments").fetchone()[0] or 0
        conn.close()
        self._create_stat_card(self.stats_frame, "Total Students", f"{total_students}", "primary")
        self._create_stat_card(self.stats_frame, "Active Courses", f"{active_courses}", "success")
        self._create_stat_card(self.stats_frame, "Total Revenue (INR)", f"{total_revenue:,.2f}", "warning")
        self.create_faculty_pie_chart(self.chart_frame)

    def _create_stat_card(self, parent, title, value, bootstyle):
        card = ttk.Frame(parent, padding=15, bootstyle=bootstyle)
        card.pack(fill="x", pady=5)
        ttk.Label(card, text=title, font=("Helvetica", 11, "bold"), bootstyle=f"inverse-{bootstyle}").pack(anchor='w')
        ttk.Label(card, text=value, font=("Helvetica", 20, "bold"), bootstyle=f"inverse-{bootstyle}").pack(anchor='w')

    def create_faculty_pie_chart(self, parent_frame):
        try:
            conn = get_db_connection()
            query = """
                SELECT f.faculty_name, COUNT(s.student_id)
                FROM faculties f
                LEFT JOIN courses c ON f.faculty_id = c.faculty_id
                LEFT JOIN students s ON c.course_id = s.course_id
                GROUP BY f.faculty_name
                HAVING COUNT(s.student_id) > 0;
            """
            data = conn.execute(query).fetchall()
            conn.close()
            labels = [row['faculty_name'] for row in data]
            sizes = [row[1] for row in data]
            if not labels:
                ttk.Label(parent_frame, text="No student data to display chart.").pack()
                return
            fig = Figure(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor(self.style.colors.bg)
            ax = fig.add_subplot(111)
            ax.set_title("Student Distribution by Faculty", color=self.style.colors.fg)
            wedges, texts, autotexts = ax.pie(
                sizes, autopct='%1.1f%%', startangle=90,
                textprops=dict(color=self.style.colors.fg)
            )
            ax.axis('equal')
            ax.legend(wedges, labels, title="Faculties", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                      facecolor=self.style.colors.light,
                      labelcolor=self.style.colors.fg)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        except Exception as e:
            ttk.Label(parent_frame, text=f"Could not load chart: {e}").pack()
