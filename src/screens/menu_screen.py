import tkinter as tk

from src.core.database import init_database


class MenuScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.database = init_database()

        header = tk.Frame(self, bg="black")
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="MENU",
            fg="white",
            bg="black",
            font=("Arial", 28, "bold"),
        )
        title.pack(side="left", padx=20, pady=20)

        exit_button = tk.Button(
            header,
            text="EXIT",
            fg="white",
            bg="#b00020",
            font=("Arial", 14, "bold"),
            command=self._on_exit,
            padx=18,
            pady=8,
        )
        exit_button.pack(side="right", padx=20, pady=20)

        self.content = tk.Frame(self, bg="black")
        self.content.pack(fill="both", expand=True, padx=30, pady=20)

        self.empty_label = tk.Label(
            self.content,
            text="No drinks available",
            fg="white",
            bg="black",
            font=("Arial", 20, "bold"),
        )

        self.grid_frame = tk.Frame(self.content, bg="black")

        self.refresh()

    def refresh(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        drinks = self.database.get_active_drinks()

        if not drinks:
            self.grid_frame.pack_forget()
            self.empty_label.pack(expand=True)
            return

        self.empty_label.pack_forget()
        self.grid_frame.pack(fill="both", expand=True)

        tiles = drinks + [{"id": "custom", "name": "CUSTOM MIX", "price": None}]

        max_columns = 3
        for col in range(max_columns):
            self.grid_frame.grid_columnconfigure(col, weight=1, uniform="menu")

        for idx, drink in enumerate(tiles):
            row = idx // max_columns
            col = idx % max_columns
            self.grid_frame.grid_rowconfigure(row, weight=1)

            if drink["id"] == "custom":
                text = "CUSTOM MIX"
                command = self._on_custom
                bg_color = "#2c3e50"
            else:
                price = drink.get("price")
                text = drink["name"]
                if price is not None:
                    text = f"{drink['name']}\n{price}"
                command = lambda d=drink: self._on_drink(d)
                bg_color = "#1f1f1f"

            button = tk.Button(
                self.grid_frame,
                text=text,
                command=command,
                fg="white",
                bg=bg_color,
                activebackground="#444444",
                activeforeground="white",
                font=("Arial", 18, "bold"),
                wraplength=240,
                relief="flat",
                padx=20,
                pady=20,
            )
            button.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

    def _on_drink(self, drink):
        print(f"Selected drink: {drink['name']} (ID: {drink['id']})")

    def _on_custom(self):
        print("custom")

    def _on_exit(self):
        self.controller.quit()
