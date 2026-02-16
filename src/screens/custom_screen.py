import tkinter as tk
import threading

from src.core.database import init_database


class CustomMixScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFFFFF")
        self.controller = controller
        self.database = init_database()
        self.rows = []

        self._build_header()
        self._build_body()
        self._build_footer()

        self.refresh()

    def _build_header(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", padx=30, pady=(20, 10))

        title = tk.Label(
            header,
            text="CUSTOM MIX",
            fg="black",
            bg="#FFFFFF",
            font=("Arial", 26, "bold"),
        )
        title.pack(side="left")

        back_btn = tk.Button(
            header,
            text="BACK",
            command=self._on_back,
            bg="#2b313c",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=18,
            pady=8,
            relief="flat",
        )
        back_btn.pack(side="right")

    def _build_body(self):
        self.body = tk.Frame(self, bg="#FFFFFF")
        self.body.pack(fill="both", expand=True, padx=30, pady=(10, 10))

        self.empty_label = tk.Label(
            self.body,
            text="No bottles available",
            fg="gray40",
            bg="#FFFFFF",
            font=("Arial", 18, "bold"),
        )

        self.rows_frame = tk.Frame(self.body, bg="#FFFFFF")

    def _build_footer(self):
        footer = tk.Frame(self, bg="#FFFFFF")
        footer.pack(fill="x", padx=30, pady=(10, 20))

        back_btn = tk.Button(
            footer,
            text="BACK",
            command=self._on_back,
            bg="#2b313c",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=24,
            pady=10,
            relief="flat",
        )
        back_btn.pack(side="left")

        start_btn = tk.Button(
            footer,
            text="START POUR",
            command=self._on_start,
            bg="#1f6feb",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=24,
            pady=10,
            relief="flat",
        )
        start_btn.pack(side="right")

    def refresh(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        self.rows.clear()

        bottles = self.database.get_enabled_bottles()
        limits = self.database.get_limits_map()

        if not bottles:
            self.rows_frame.pack_forget()
            self.empty_label.pack(expand=True)
            return

        self.empty_label.pack_forget()
        self.rows_frame.pack(fill="both", expand=True)

        for bottle in bottles:
            limit = limits.get(bottle["id"], {"min_ml": 0, "max_ml": 150})
            self._add_row(bottle, limit["min_ml"], limit["max_ml"])

    def _add_row(self, bottle, min_ml, max_ml):
        row = tk.Frame(self.rows_frame, bg="#F8FAFC", highlightthickness=1, highlightbackground="#E2E8F0")
        row.pack(fill="x", pady=8)

        name_label = tk.Label(
            row,
            text=bottle["name"],
            fg="#1E293B",
            bg="#F8FAFC",
            font=("Arial", 14, "bold"),
            width=16,
            anchor="w",
        )
        name_label.pack(side="left", padx=16, pady=12)

        value_var = tk.IntVar(value=min_ml)
        scale = tk.Scale(
            row,
            from_=min_ml,
            to=max_ml,
            orient="horizontal",
            showvalue=False,
            variable=value_var,
            length=320,
            bg="#F8FAFC",
            troughcolor="#E2E8F0",
            activebackground="#2563EB",
            highlightthickness=0,
        )
        scale.pack(side="left", padx=10, pady=10)

        entry = tk.Entry(
            row,
            width=6,
            justify="center",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="black",
            insertbackground="black",
            relief="flat",
        )
        entry.pack(side="left", padx=10)
        entry.insert(0, str(min_ml))

        unit = tk.Label(
            row,
            text="ml",
            fg="#64748B",
            bg="#F8FAFC",
            font=("Arial", 12, "bold"),
        )
        unit.pack(side="left", padx=(0, 16))

        hint = tk.Label(
            row,
            text=f"{min_ml} - {max_ml} ml",
            fg="#94A3B8",
            bg="#F8FAFC",
            font=("Arial", 10),
        )
        hint.pack(side="right", padx=16)

        def on_scale(_value):
            entry.delete(0, tk.END)
            entry.insert(0, str(value_var.get()))

        def on_entry_change(_event=None):
            raw = entry.get().strip()
            try:
                value = int(raw)
            except ValueError:
                value = min_ml
            value = max(min_ml, min(max_ml, value))
            value_var.set(value)
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

        scale.configure(command=on_scale)
        entry.bind("<Return>", on_entry_change)
        entry.bind("<FocusOut>", on_entry_change)

        self.rows.append(
            {
                "bottle_id": bottle["id"],
                "name": bottle["name"],
                "var": value_var,
                "min_ml": min_ml,
                "max_ml": max_ml,
            }
        )

    def _on_start(self):
        """Handle custom mix start"""
        payload = {row["bottle_id"]: row["var"].get() for row in self.rows}
        print(f"Custom mix: {payload}")
        
        # Get pour engine from controller
        if not hasattr(self.controller, 'pour_engine'):
            self._show_error("System not ready. Please restart the application.")
            return
        
        self._send_dispense(lambda: self.controller.pour_engine.dispense_custom(payload))

    def _send_dispense(self, action):
        """Run dispense command without blocking UI"""
        def worker():
            success, message, msg_id, payload = action()

            def finish():
                if success:
                    print(f"Custom dispense successful: {message} (msg_id: {msg_id})")
                    self.controller.show_screen("processing")
                    screen = self.controller.get_screen("processing")
                    if screen:
                        relays = [job["relay"] for job in payload.get("jobs", [])]
                        screen.start_transaction(payload, msg_id, relays)
                else:
                    print(f"Custom dispense failed: {message}")
                    if payload:
                        self.controller.show_screen("processing")
                        screen = self.controller.get_screen("processing")
                        if screen:
                            screen.start_failure(message, payload)
                    else:
                        self._show_error(message)

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()
    
    def _show_error(self, message):
        """Display error popup"""
        popup = tk.Toplevel(self)
        popup.title("Error")
        popup.geometry("400x200")
        popup.configure(bg="#FFFFFF")
        
        label = tk.Label(
            popup,
            text=message,
            fg="black",
            bg="#FFFFFF",
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

    def _on_back(self):
        self.controller.show_screen("menu")
