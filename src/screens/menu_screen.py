import tkinter as tk


class MenuScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        label = tk.Label(
            self,
            text="MENU PAGE",
            fg="white",
            bg="black",
            font=("Arial", 36, "bold"),
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
