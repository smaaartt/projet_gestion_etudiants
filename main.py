import tkinter as tk
from views.auth_view import LoginApp

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
