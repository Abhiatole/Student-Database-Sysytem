import tkinter as tk
from ttkbootstrap import Style, ttk
from app.gui.dashboard import DashboardTab
from app.gui.students import StudentManagementTab
from app.gui.reports import ReportsTab
from app.gui.analytics import AnalyticsTab
from app.gui.id_card import IDCardTab
from app.gui.payments import ReceiptTab
from app.gui.communications import CommunicationsTab
from app.gui.marks import MarksTab
from app.db.database import init_db
from app.utils.image_utils import load_image
from app.gui.login import LoginWindow
from app.gui.register import RegisterWindow

def add_window_controls(root):
    control_frame = ttk.Frame(root)
    control_frame.place(relx=1.0, rely=0.0, anchor="ne")
    btn_min = ttk.Button(control_frame, text="_", width=2, command=root.iconify, bootstyle="secondary")
    btn_min.pack(side="left", padx=1)
    btn_max = ttk.Button(control_frame, text="□", width=2, command=lambda: root.state('zoomed'), bootstyle="secondary")
    btn_max.pack(side="left", padx=1)
    btn_close = ttk.Button(control_frame, text="✕", width=2, command=root.destroy, bootstyle="danger")
    btn_close.pack(side="left", padx=1)

class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.deiconify()
        self.master.title("Student Database Management System")
        self.master.geometry("1366x768")
        self.master.overrideredirect(True)
        self.style = Style(theme="superhero")
        # Load images
        self.logo_img = load_image("logo.png", size=(64, 64))
        self.banner_img = load_image("college_banner.png", size=(800, 200))
        self.create_main_widgets()

    def create_main_widgets(self):
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill="both")
        self.notebook = tk.ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        tabs = {
            "🏠 Home": lambda f: DashboardTab(f, self.style, self.logo_img),
            "🎓 Student Management": StudentManagementTab,
            "📊 Reporting & Export": lambda f: ReportsTab(f, self.master),
            "📈 Analytics & Insights": lambda f: AnalyticsTab(f, self.style),
            "💳 ID Card Generation": IDCardTab,
            "🧾 Receipt Generation": ReceiptTab,
            "💬 Communications": CommunicationsTab,
            "Marks Entry": MarksTab,
        }
        for text, tab_class in tabs.items():
            frame = tk.ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=text)
            tab_class(frame)

def main():
    try:
        init_db()
    except Exception as e:
        tk.messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
        exit(1)
    root = tk.Tk()
    # Show login window before main app
    login_window = LoginWindow(root)
    add_window_controls(root)  # Add window controls
    root.mainloop()

if __name__ == "__main__":
    main()
