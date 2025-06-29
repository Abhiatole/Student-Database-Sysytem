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
from app.gui.login import LoginWindow
from app.gui.students import BinTab
from app.gui.students import ensure_deleted_column
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
        self.master.main_app_instance = self  # Add this line
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
        logo_path = os.path.join(resources_dir, "logo.png")
        banner_path = os.path.join(resources_dir, "college_banner.png")
        self.logo_img = load_image(logo_path, size=(64, 64))
        self.banner_img = load_image(banner_path, size=(800, 200))
        self.dashboard_tab_instance = None  # Add this line
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
            "🏠 Home": lambda f: self._init_dashboard_tab(f),
            "🎓 Student Management": StudentManagementTab,
            "📊 Reporting & Export": lambda f: ReportsTab(f, self.master),
            "📈 Analytics & Insights": lambda f: AnalyticsTab(f, self.style),
            "💳 ID Card Generation": IDCardTab,
            "🧾 Receipt Generation": ReceiptTab,
            "💬 Communications": CommunicationsTab,
            "Marks Entry": MarksTab,
            "🗑️ Bin": BinTab,
        }
        for text, tab_class in tabs.items():
            frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=text)
            try:
                tab_class(frame)
            except Exception as e:
                print(f"Error initializing tab '{text}': {e}")
                import traceback
                traceback.print_exc()
                ttk.Label(frame, text=f"Failed to load tab: {e}", foreground="red").pack()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def _init_dashboard_tab(self, frame):
        self.dashboard_tab_instance = DashboardTab(frame, self.style, self.logo_img)

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
        ensure_deleted_column()  # <-- Add this line
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
