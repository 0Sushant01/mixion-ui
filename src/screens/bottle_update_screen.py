import customtkinter as ctk
import tkinter as tk

class BottleUpdateScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.controller = controller
        self.database = controller.database

        self.COLOR_PRIMARY = "#111827"
        self.COLOR_SUCCESS = "#059669"
        self.COLOR_DANGER = "#DC2626"
        self.COLOR_TEXT = "#0F172A"
        self.COLOR_TEXT_SUB = "#64748B"

        self.entries = {}

        # Header
        self.header = ctk.CTkFrame(self, fg_color="white", height=100, corner_radius=0)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        ctk.CTkLabel(
            self.header,
            text="Update Bottle Volumes",
            font=("Helvetica", 36, "bold"),
            text_color=self.COLOR_TEXT
        ).pack(side="left", padx=40, pady=20)

        # Back Button
        self.back_btn = ctk.CTkButton(
            self.header,
            text="Back to Menu",
            command=self._go_back,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="#111827",
            font=("Helvetica", 16, "bold"),
            width=140, height=45, corner_radius=22
        )
        self.back_btn.pack(side="right", padx=40)

        # Content Frame
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Footer Frame
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        self.footer_frame.pack(fill="x", padx=40, pady=(0, 20))
        self.footer_frame.pack_propagate(False)

        self.save_btn = ctk.CTkButton(
            self.footer_frame,
            text="SAVE CHANGES",
            command=self._save_volumes,
            fg_color=self.COLOR_SUCCESS,
            hover_color="#047857",
            font=("Helvetica", 18, "bold"),
            width=200, height=50, corner_radius=25
        )
        self.save_btn.pack(side="right")

        self.error_label = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=("Helvetica", 16),
            text_color=self.COLOR_DANGER
        )
        self.error_label.pack(side="left", padx=20)

    def refresh(self):
        """Called each time the screen is shown."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.entries.clear()
        self.error_label.configure(text="", text_color=self.COLOR_DANGER)

        bottles = self.database.get_all_bottles()
        if not bottles:
            ctk.CTkLabel(self.content_frame, text="No bottles configured.", font=("Helvetica", 24)).pack(pady=40)
            self.save_btn.configure(state="disabled")
            return

        self.save_btn.configure(state="normal")

        # Headers for rows
        header_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 10))
        header_row.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(header_row, text="Bottle", font=("Helvetica", 18, "bold"), text_color=self.COLOR_TEXT_SUB).grid(row=0, column=0, sticky="w", padx=20)
        ctk.CTkLabel(header_row, text="Current Volume (ml)", font=("Helvetica", 18, "bold"), text_color=self.COLOR_TEXT_SUB).grid(row=0, column=1, padx=20)
        ctk.CTkLabel(header_row, text="Capacity (ml)", font=("Helvetica", 18, "bold"), text_color=self.COLOR_TEXT_SUB).grid(row=0, column=2, sticky="e", padx=20)

        for bottle in bottles:
            row_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
            row_frame.pack(fill="x", pady=5)
            row_frame.grid_columnconfigure((0, 1, 2), weight=1)

            # Name
            ctk.CTkLabel(
                row_frame, 
                text=f"Position {bottle['position']}: {bottle['name']}", 
                font=("Helvetica", 20, "bold"),
                text_color=self.COLOR_TEXT
            ).grid(row=0, column=0, sticky="w", padx=20, pady=20)

            # Current Volume Input
            vol_var = tk.StringVar(value=str(bottle.get("current_volume_ml", 0.0)))
            entry = ctk.CTkEntry(
                row_frame,
                textvariable=vol_var,
                font=("Helvetica", 18),
                width=150,
                justify="center"
            )
            entry.grid(row=0, column=1, padx=20, pady=20)

            # Store max capacity and var for validation
            capacity = bottle.get("capacity_ml", 1000.0)
            self.entries[bottle["id"]] = {"var": vol_var, "capacity": capacity, "name": bottle["name"]}

            # Capacity Display
            ctk.CTkLabel(
                row_frame, 
                text=f"/ {capacity} ml", 
                font=("Helvetica", 18),
                text_color=self.COLOR_TEXT_SUB
            ).grid(row=0, column=2, sticky="e", padx=20, pady=20)

    def _save_volumes(self):
        updates = {}
        for bottle_id, data in self.entries.items():
            val_str = data["var"].get().strip()
            
            # Validation
            try:
                val = float(val_str)
            except ValueError:
                self.error_label.configure(text=f"Invalid number for {data['name']}", text_color=self.COLOR_DANGER)
                return

            if val < 0:
                self.error_label.configure(text=f"Volume cannot be negative for {data['name']}", text_color=self.COLOR_DANGER)
                return
            
            if val > data["capacity"]:
                self.error_label.configure(text=f"Volume exceeds capacity for {data['name']}", text_color=self.COLOR_DANGER)
                return
            
            updates[bottle_id] = val

        # Save to DB
        try:
            for bottle_id, val in updates.items():
                self.database.set_volume(bottle_id, val)
            self.error_label.configure(text="✓ Volumes updated successfully!", text_color=self.COLOR_SUCCESS)
            # clear error toast after 3 seconds
            self.after(3000, lambda: self.error_label.configure(text=""))
        except Exception as e:
            self.error_label.configure(text=f"Database error: {e}", text_color=self.COLOR_DANGER)

    def _go_back(self):
        self.controller.show_screen("menu")

