import tkinter as tk
import threading

class ToastManager:
    @staticmethod
    def show(title, message, duration=1500):
        try:
            ToastWindow(title, message, duration)
        except:
            pass

class ToastWindow:
    def __init__(self, title, message, duration):
        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg="#1e1e1e", highlightthickness=1, highlightbackground="#00ff00")
        
        # Position: Top Right, slightly down
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"300x60+{screen_w - 320}+50")
        
        # Content
        tk.Label(self.root, text=title, fg="#00ff00", bg="#1e1e1e", font=("Consolas", 10, "bold"), anchor="w").pack(fill="x", padx=10, pady=(5,0))
        tk.Label(self.root, text=message, fg="white", bg="#1e1e1e", font=("Consolas", 9), anchor="w").pack(fill="x", padx=10, pady=(0,5))
        
        # Auto-Destruct
        self.root.after(duration, self.root.destroy)

def toast(title: str, message: str):
    ToastManager.show(title, message)
