import tkinter as tk
from ttkbootstrap import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.db.database import get_db_connection

# Analytics and charting logic

class AnalyticsTab:
    def __init__(self, parent, style):
        self.style = style
        self.setup_analytics_tab(parent)

    def setup_analytics_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Analytics & Insights", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=10)
        try:
            conn = get_db_connection()
            query = """
                SELECT c.course_name, COUNT(s.student_id) as student_count
                FROM courses c
                LEFT JOIN students s ON c.course_id = s.course_id
                GROUP BY c.course_name
            """
            data = conn.execute(query).fetchall()
            conn.close()
            labels = [row['course_name'] for row in data]
            values = [row['student_count'] for row in data]
            if not labels:
                ttk.Label(parent_frame, text="No data to display chart.").pack()
                return
            fig = Figure(figsize=(6, 4), dpi=100)
            fig.patch.set_facecolor(self.style.colors.bg)
            ax = fig.add_subplot(111)
            ax.bar(labels, values, color=self.style.colors.primary)
            ax.set_title("Students per Course", color=self.style.colors.fg)
            ax.set_ylabel("Number of Students")
            ax.set_xlabel("Course")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        except Exception as e:
            ttk.Label(parent_frame, text=f"Could not load chart: {e}").pack()
