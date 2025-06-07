import tkinter as tk
from ttkbootstrap import Style, ttk
from ttkbootstrap.tooltip import ToolTip
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
import os

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
        self.master.minsize(1024, 600)
        self.master.overrideredirect(False)  # Allow window controls for all platforms
        self.style = Style(theme="superhero")
        # Theme toggle
        self.theme_var = tk.StringVar(value="superhero")
        # Load images from resources directory
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")
        self.logo_img = load_image(os.path.join(resources_dir, "logo.png"), size=(64, 64))
        self.banner_img = load_image(os.path.join(resources_dir, "college_banner.png"), size=(800, 200))
        self.create_main_widgets()

    def create_main_widgets(self):
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill="both")
        # Theme switcher
        theme_frame = ttk.Frame(main_frame)
        theme_frame.pack(anchor="ne", padx=10, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side="left")
        theme_combo = ttk.Combobox(theme_frame, values=self.style.theme_names(), textvariable=self.theme_var, width=15)
        theme_combo.pack(side="left", padx=5)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        ToolTip(theme_combo, text="Switch between light/dark themes")
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, anchor="w", bootstyle="secondary")
        status_bar.pack(side="bottom", fill="x")
        # Notebook
        self.notebook = ttk.Notebook(main_frame)
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
            frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=text)
            tab_class(frame)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def change_theme(self, event=None):
        new_theme = self.theme_var.get()
        self.style.theme_use(new_theme)
        self.status_var.set(f"Theme changed to {new_theme}")

    def on_tab_change(self, event):
        tab = self.notebook.tab(self.notebook.select(), "text")
        self.status_var.set(f"Switched to {tab} tab")

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
