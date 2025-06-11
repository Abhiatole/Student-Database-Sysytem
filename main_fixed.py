import tkinter as tk
from ttkbootstrap import Style, ttk
from ttkbootstrap.tooltip import ToolTip
from app.gui.dashboard import DashboardTab
from app.gui.students import StudentManagementTab
from app.gui.analytics import AnalyticsTab
from app.gui.id_card import IDCardTab
from app.gui.payments import ReceiptTab
from app.gui.communications import CommunicationsTab
from app.gui.marks import MarksTab
from app.db.database import init_db
from app.utils.image_utils import load_image
from app.gui.login import LoginWindow
from app.gui.students import ensure_deleted_column
import os

def add_window_controls(root):
    """Add window controls for better user experience"""
    pass

class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.main_app_instance = self
        self.master.deiconify()
        self.master.title("Student Database Management System")
        self.master.geometry("1366x768")
        self.master.minsize(1024, 600)
        self.master.overrideredirect(False)
        self.style = Style(theme="superhero")
        self.theme_var = tk.StringVar(value="superhero")
        
        # Load images from resources directory
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")
        logo_path = os.path.join(resources_dir, "logo.png")
        banner_path = os.path.join(resources_dir, "college_banner.png")
        self.logo_img = load_image(logo_path, size=(64, 64))
        self.banner_img = load_image(banner_path, size=(800, 200))
        self.dashboard_tab_instance = None
        self.create_main_widgets()

    def create_main_widgets(self):
        """Create the main application widgets"""
        add_window_controls(self.master)
        
        # Main container
        main_container = ttk.Frame(self.master)
        main_container.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, bootstyle="primary")        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        tabs = {
            "🏠 Home": lambda f: self._init_dashboard_tab(f),
            "🎓 Student Management": StudentManagementTab,
            "📈 Analytics & Insights": lambda f: AnalyticsTab(f, self.style),
            "💳 ID Card Generation": IDCardTab,
            "🧾 Receipt Generation": ReceiptTab,
            "💬 Communications": CommunicationsTab,
            "Marks Entry": MarksTab,
        }
        
        for text, tab_class in tabs.items():
            frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=text)
            try:
                tab_class(frame)
                print(f"Successfully initialized tab: {text}")
            except Exception as e:
                print(f"Error initializing tab '{text}': {e}")
                import traceback
                traceback.print_exc()
                ttk.Label(frame, text=f"Failed to load tab: {e}", foreground="red").pack()
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def _init_dashboard_tab(self, frame):
        """Initialize the dashboard tab"""
        try:
            self.dashboard_tab_instance = DashboardTab(frame, self.master)
        except Exception as e:
            print(f"Error initializing dashboard: {e}")
            ttk.Label(frame, text=f"Dashboard unavailable: {e}", foreground="red").pack()

    def on_tab_change(self, event):
        """Handle tab change events"""
        try:
            selected_tab = event.widget.tab('current')['text']
            if selected_tab == "🏠 Home" and self.dashboard_tab_instance:
                if hasattr(self.dashboard_tab_instance, 'refresh_dashboard'):
                    self.dashboard_tab_instance.refresh_dashboard()
        except Exception as e:
            print(f"Error handling tab change: {e}")

def main():
    """Main entry point"""
    try:
        # Initialize database
        init_db()
        ensure_deleted_column()
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide initially
        
        # Check if login is required
        if os.path.exists("login_required.flag"):
            login_window = LoginWindow(root)
            root.wait_window(login_window.window)
            
            if not login_window.login_successful:
                root.destroy()
                return
        
        # Create main application
        app = MainApplication(root)
        
        # Start the main loop
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        if 'root' in locals():
            root.destroy()

if __name__ == "__main__":
    main()
