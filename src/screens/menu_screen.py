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

        exit_button = tk.Button(
            self,
            text="EXIT",
            fg="white",
            bg="red",
            font=("Arial", 16, "bold"),
            command=self._on_exit,
            padx=20,
            pady=10,
        )
        exit_button.place(relx=0.95, rely=0.05, anchor="ne")

    def _on_exit(self):
        self.controller.quit()
