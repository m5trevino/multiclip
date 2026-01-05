import tkinter as tk

class HudWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)  # No borders
        self.window.attributes('-topmost', True) # Always on top
        self.window.attributes('-alpha', 0.85)   # Slight transparency
        self.window.geometry("250x130+50+50")    # Size + Position
        self.window.configure(bg="#1e1e1e")

        # Drag logic
        self.window.bind('<Button-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.do_move)

        # Labels
        self.title = tk.Label(self.window, text=":: SEQUENCE HUD ::", bg="#1e1e1e", fg="#00ff00", font=("Consolas", 8))
        self.title.pack(pady=2)

        # The "Reel"
        self.slots_labels = []
        for i in range(3):
            lbl = tk.Label(self.window, text="---", bg="#1e1e1e", fg="white", font=("Consolas", 10), anchor="w")
            lbl.pack(fill="x", padx=5)
            self.slots_labels.append(lbl)

        self.x = 0
        self.y = 0

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def update_view(self, current_idx: int, slots: dict):
        # Logic: Show Current, Next, and Next+1
        # current_idx is 1-based (1-10)
        
        indices_to_show = [current_idx, (current_idx % 10) + 1, ((current_idx + 1) % 10) + 1]
        
        for i, slot_num in enumerate(indices_to_show):
            text = slots.get(slot_num, "")
            display_text = text[:25] + "..." if len(text) > 25 else text or "<EMPTY>"
            
            label = self.slots_labels[i]
            
            if i == 0: # The "Live" Chamber
                label.config(text=f"[{slot_num}] >> {display_text}", fg="#00ff00", font=("Consolas", 11, "bold"))
            else: # On Deck
                label.config(text=f"[{slot_num}]    {display_text}", fg="#888888", font=("Consolas", 10))
