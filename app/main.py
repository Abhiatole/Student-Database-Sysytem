import tkinter as tk
from app.gui.login import LoginWindow
from app.db.database import init_db
from app.db.seed import seed_defaults

def main():
    init_db()
    seed_defaults()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
