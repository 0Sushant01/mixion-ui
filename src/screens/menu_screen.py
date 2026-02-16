import tkinter as tk

from src.core.database import init_database


class MenuScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0b0f14")
        self.controller = controller
        self.database = init_database()

        header = tk.Frame(self, bg="#0b0f14")
        header.pack(fill="x", padx=30, pady=(20, 10))

        title = tk.Label(
            header,
            text="MIXION",
            fg="white",
            bg="#0b0f14",
            font=("Arial", 28, "bold"),
        )
        title.pack(side="left")

        subtitle = tk.Label(
            header,
            text="Select Your Drink",
            fg="#9aa4b2",
            bg="#0b0f14",
            font=("Arial", 14),
        )
        subtitle.pack(side="left", padx=16, pady=(6, 0))

        exit_button = tk.Button(
            header,
            text="EXIT",
            fg="white",
            bg="#b00020",
            font=("Arial", 12, "bold"),
            command=self._on_exit,
            padx=18,
            pady=8,
            relief="flat",
        )
        exit_button.pack(side="right")

        self.content = tk.Frame(self, bg="#0b0f14")
        self.content.pack(fill="both", expand=True, padx=30, pady=20)

        self.empty_label = tk.Label(
            self.content,
            text="No drinks available",
            fg="white",
            bg="#0b0f14",
            font=("Arial", 20, "bold"),
        )

        self.grid_frame = tk.Frame(self.content, bg="#0b0f14")
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

            card = self._build_card(self.grid_frame, drink)
            card.grid(row=row, column=col, padx=14, pady=14, sticky="nsew")

    def _build_card(self, parent, drink):
        is_custom = drink["id"] == "custom"
        card_bg = "#161b22" if not is_custom else "#1e2a3a"
        accent = "#3b82f6" if not is_custom else "#22c55e"

        card = tk.Frame(
            parent,
            bg=card_bg,
            highlightthickness=1,
            highlightbackground="#2b313c",
        )

        image_slot = tk.Frame(card, bg="#0f131a", height=90)
        image_slot.pack(fill="x", padx=16, pady=(16, 10))
        image_slot.pack_propagate(False)

        image_text = "IMAGE" if not is_custom else "MIX"
        tk.Label(
            image_slot,
            text=image_text,
            fg="#4b5563",
            bg="#0f131a",
            font=("Arial", 12, "bold"),
        ).pack(expand=True)

        name = drink["name"]
        if is_custom:
            name = "CUSTOM MIX"

        name_label = tk.Label(
            card,
            text=name,
            fg="white",
            bg=card_bg,
            font=("Arial", 16, "bold"),
            wraplength=220,
            justify="center",
        )
        name_label.pack(fill="x", padx=16)

        price_value = drink.get("price")
        price_text = ""
        if price_value is not None and not is_custom:
            price_text = f"Price: {price_value}"

        price_label = tk.Label(
            card,
            text=price_text,
            fg="#9aa4b2",
            bg=card_bg,
            font=("Arial", 12),
        )
        price_label.pack(pady=(6, 12))

        button = tk.Button(
            card,
            text="SELECT" if not is_custom else "OPEN",
            command=(self._on_custom if is_custom else lambda d=drink: self._on_drink(d)),
            fg="white",
            bg=accent,
            activebackground="#2563eb",
            activeforeground="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=20,
            pady=8,
        )
        button.pack(pady=(0, 16))

        def on_enter(_event):
            card.configure(highlightbackground=accent)

        def on_leave(_event):
            card.configure(highlightbackground="#2b313c")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for widget in (image_slot, name_label, price_label, button):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return card

    def _on_drink(self, drink):
        """Handle drink selection"""
        print(f"Selected drink: {drink['name']} (ID: {drink['id']})")
        
        # Get pour engine from controller
        if not hasattr(self.controller, 'pour_engine'):
            self._show_error("System not ready. Please restart the application.")
            return
        
        # Dispense the drink
        success, message, msg_id = self.controller.pour_engine.dispense_drink(drink['id'])
        
        if success:
            print(f"Dispense successful: {message} (msg_id: {msg_id})")
            # Navigate to processing screen
            self.controller.show_screen("processing")
        else:
            print(f"Dispense failed: {message}")
            self._show_error(message)
    
    def _show_error(self, message):
        """Display error popup"""
        popup = tk.Toplevel(self)
        popup.title("Error")
        popup.geometry("400x200")
        popup.configure(bg="#1a1a2e")
        
        label = tk.Label(
            popup,
            text=message,
            fg="white",
            bg="#1a1a2e",
            font=("Arial", 14),
            wraplength=350
        )
        label.pack(expand=True, pady=20)
        
        button = tk.Button(
            popup,
            text="OK",
            command=popup.destroy,
            bg="#e94560",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief="flat"
        )
        button.pack(pady=10)

    def _on_custom(self):
        self.controller.show_screen("custom")

    def _on_exit(self):
        self.controller.quit()
