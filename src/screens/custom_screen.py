import customtkinter as ctk
import threading
class CustomMixScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white", corner_radius=0)
        self.controller = controller
        self.database = controller.database
        self.rows = []

        # Constants
        self.COLOR_SUCCESS = "#059669"
        self.COLOR_TEXT = "#111827"
        self.TITLE_FONT = ("Roboto", 32, "bold")
        self.BTN_FONT = ("Roboto", 16, "bold")

        # Layout
        self._build_header()
        self._build_body()
        self._build_footer()
        
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="white", height=80, corner_radius=0)
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(
            header, 
            text="Design Your Mix", 
            font=self.TITLE_FONT, 
            text_color=self.COLOR_TEXT
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="BACK",
            command=self._on_back,
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color="#64748B",
            font=self.BTN_FONT,
            width=100,
            height=44,
            corner_radius=22
        ).pack(side="right")

    def _build_body(self):
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=30, pady=10)

        self.empty_label = ctk.CTkLabel(
            self.body,
            text="No bottles available",
            font=("Roboto", 24, "bold"),
            text_color="gray"
        )

        self.rows_frame = ctk.CTkScrollableFrame(
            self.body, 
            fg_color="transparent",
            scrollbar_button_color="#E2E8F0"
        )

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="white", height=100, corner_radius=0)
        footer.pack(fill="x", padx=30, pady=20)

        ctk.CTkButton(
            footer,
            text="START POURING",
            command=self._on_start,
            fg_color=self.COLOR_SUCCESS,
            hover_color="#047857",
            text_color="white",
            font=("Roboto", 20, "bold"),
            height=60,
            corner_radius=30
        ).pack(fill="x")

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
            
            # Dynamic max limit capped at current available volume
            available_vol = bottle.get("current_volume_ml", 0.0)
            dynamic_max = min(limit["max_ml"], int(available_vol))
            
            # Disable ingredient entirely if no volume is left
            # OR if we can't even meet the minimum required ml limit
            if dynamic_max <= 0 or dynamic_max <= limit["min_ml"]:
                continue
                
            self._add_row(bottle, limit["min_ml"], dynamic_max)

    def _add_row(self, bottle, min_ml, max_ml):
        row = ctk.CTkFrame(self.rows_frame, fg_color="#F8FAFC", corner_radius=16, border_width=1, border_color="#E2E8F0")
        row.pack(fill="x", pady=10)

        # Name
        ctk.CTkLabel(
            row,
            text=bottle["name"],
            font=("Roboto", 18, "bold"),
            text_color=self.COLOR_TEXT,
            width=150,
            anchor="w"
        ).pack(side="left", padx=20, pady=20)

        # Slider Logic
        value_var = threading.local() # Using int var in CTk is tricky with threads sometimes, just use normal var
        # Actually CTkSlider uses fluid float. We need a way to track it.
        # Let's use a class attribute or dictionary to store current value for this row.
        
        # We'll use the dictionary 'row_data' to store state
        row_data = {
            "bottle_id": bottle["id"],
            "value": min_ml,
            "min": min_ml,
            "max": max_ml
        }

        def update_val(val):
            val = int(val)
            row_data["value"] = val
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, str(val))
            # entry.configure(state="disabled") # Keep editable?

        slider = ctk.CTkSlider(
            row,
            from_=min_ml,
            to=max_ml,
            number_of_steps=(max_ml-min_ml),
            command=update_val,
            height=20,
            progress_color=self.COLOR_SUCCESS,
            button_color=self.COLOR_SUCCESS,
            button_hover_color="#047857"
        )
        slider.set(min_ml)
        slider.pack(side="left", fill="x", expand=True, padx=20)

        # Value Entry/Display
        entry = ctk.CTkEntry(
            row,
            width=60,
            font=("Roboto", 18, "bold"),
            justify="center",
            corner_radius=10
        )
        entry.insert(0, str(min_ml))
        entry.pack(side="left", padx=(0, 10))
        
        def on_entry(event):
            try:
                val = int(entry.get())
                val = max(min_ml, min(max_ml, val))
                slider.set(val)
                row_data["value"] = val
            except:
                pass
        
        entry.bind("<Return>", on_entry)
        entry.bind("<FocusOut>", on_entry)

        ctk.CTkLabel(
            row,
            text="ml",
            font=("Roboto", 16),
            text_color="gray"
        ).pack(side="left", padx=(0, 20))

        self.rows.append(row_data)

    def _on_start(self):
        payload = {r["bottle_id"]: r["value"] for r in self.rows if r["value"] > 0}
        if not payload:
             self._show_error("Please select at least one ingredient.")
             return
             
        if not hasattr(self.controller, 'pour_engine'):
            self._show_error("System error: Pour engine missing.")
            return
            
        self._send_dispense(lambda: self.controller.pour_engine.dispense_custom(payload))

    def _send_dispense(self, action):
         # ... Reuse worker logic ...
        def worker():
            success, message, msg_id, payload = action()
            def finish():
                if success:
                    print(f"Custom dispense successful: {message}")
                    self.controller.show_screen("processing")
                    screen = self.controller.get_screen("processing")
                    if screen:
                        relays = [job["relay"] for job in payload.get("jobs", [])]
                        screen.start_transaction(payload, msg_id, relays, drink_name="Custom Mix")
                else:
                    self._show_error(message)
            self.after(0, finish)
        threading.Thread(target=worker, daemon=True).start()

    def _show_error(self, message):
        # reuse logic from MenuScreen ideally, but for now duplicate concise version
        popup = ctk.CTkToplevel(self)
        popup.title("Info")
        popup.geometry("400x200")
        popup.transient(self)
        
        ctk.CTkLabel(popup, text=message, font=("Roboto", 16), wraplength=350).pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy, width=100).pack(pady=20)

    def _on_back(self):
        self.controller.show_screen("menu")
