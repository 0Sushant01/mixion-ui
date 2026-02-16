import tkinter as tk
import threading
import customtkinter as ctk
from PIL import Image

import config
from src.screens.splash_screen import play_splash_video


class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#0b0f14", corner_radius=0)
        self.controller = controller
        self.database = controller.database
        self._drink_buttons = []
        self._status_poll_id = None
        self._status_request_id = None

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Content area expands

        # --- Header ---
        self.header = ctk.CTkFrame(self, fg_color="#0b0f14", height=80, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        self.header.grid_columnconfigure(1, weight=1)  # Spacer

        # Title Section
        self.title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="MIXION",
            font=("Roboto", 32, "bold"),
            text_color="white"
        )
        self.title_label.pack(side="left")

        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="Select Your Drink",
            font=("Roboto", 16),
            text_color="#9aa4b2"
        )
        self.subtitle_label.pack(side="left", padx=(15, 0), pady=(8, 0))

        # Right Side Controls
        self.controls_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.controls_frame.grid(row=0, column=2, sticky="e")

        self.status_indicator = ctk.CTkLabel(
            self.controls_frame,
            text="● CONNECTING",
            font=("Roboto", 14, "bold"),
            text_color="#f59e0b"
        )
        self.status_indicator.pack(side="left", padx=(0, 20))

        self.splash_btn = ctk.CTkButton(
            self.controls_frame,
            text="SPLASH",
            command=self._on_splash,
            fg_color="#334155",
            hover_color="#475569",
            text_color="white",
            font=("Roboto", 12, "bold"),
            width=100,
            height=36,
            corner_radius=8
        )
        self.splash_btn.pack(side="left", padx=(0, 10))

        self.exit_btn = ctk.CTkButton(
            self.controls_frame,
            text="EXIT",
            command=self._on_exit,
            fg_color="#b00020",
            hover_color="#cf6679",
            text_color="white",
            font=("Roboto", 12, "bold"),
            width=80,
            height=36,
            corner_radius=8
        )
        self.exit_btn.pack(side="left")

        # --- Content Area ---
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Grid Configuration for Content
        self.content.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        self.empty_label = ctk.CTkLabel(
            self,
            text="No drinks available",
            font=("Roboto", 24, "bold"),
            text_color="#64748b"
        )

        self.refresh()
        self._schedule_status_poll()
        self._schedule_status_request()

    def refresh(self):
        # Clear existing widgets in content
        for widget in self.content.winfo_children():
            widget.destroy()

        self._drink_buttons.clear()

        drinks = self.database.get_active_drinks()
        
        # If no drinks, show empty message
        if not drinks:
            self.content.grid_forget()
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        self.empty_label.place_forget()
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        tiles = drinks + [{"id": "custom", "name": "CUSTOM MIX", "price": None}]

        # Create cards
        for idx, drink in enumerate(tiles):
            row = idx // 3
            col = idx % 3
            self._create_drink_card(drink, row, col)

    def _create_drink_card(self, drink, row, col):
        is_custom = drink["id"] == "custom"
        
        card_color = "#161b22" if not is_custom else "#0f291e" # Darker green hint for custom
        border_color = "#2b313c" if not is_custom else "#10b981"
        accent_color = "#3b82f6" if not is_custom else "#10b981"
        hover_color = "#2563eb" if not is_custom else "#059669"

        card = ctk.CTkFrame(
            self.content,
            fg_color=card_color,
            border_width=1,
            border_color=border_color,
            corner_radius=15
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Image / Icon Placeholder
        icon_frame = ctk.CTkFrame(
            card,
            fg_color="#0d1117",
            height=120,
            corner_radius=10
        )
        icon_frame.pack(fill="x", padx=15, pady=15)
        icon_frame.pack_propagate(False)

        icon_text = "🍸" if not is_custom else "🧪"
        ctk.CTkLabel(
            icon_frame,
            text=icon_text,
            font=("Segoe UI Emoji", 48), # Use system emoji font if possible, or fallback
            text_color="#4b5563"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Drink Name
        display_name = drink["name"] if not is_custom else "Design Your Own"
        ctk.CTkLabel(
            card,
            text=display_name,
            font=("Roboto", 18, "bold"),
            text_color="white",
            wraplength=200
        ).pack(fill="x", padx=15, pady=(0, 5))

        # Price
        price_text = " "
        if not is_custom and drink.get("price"):
            price_text = f"${drink['price']}"
        
        ctk.CTkLabel(
            card,
            text=price_text,
            font=("Roboto", 14),
            text_color="#9aa4b2"
        ).pack(fill="x", padx=15, pady=(0, 15))

        # Select Button
        btn_text = "SELECT" if not is_custom else "START MIXING"
        command = (self._on_custom if is_custom else lambda d=drink: self._on_drink(d))
        
        btn = ctk.CTkButton(
            card,
            text=btn_text,
            command=command,
            fg_color=accent_color,
            hover_color=hover_color,
            text_color="white",
            font=("Roboto", 14, "bold"),
            height=40,
            corner_radius=8
        )
        btn.pack(fill="x", padx=15, pady=(0, 20))
        
        self._drink_buttons.append(btn)

    def _on_drink(self, drink):
        if not self._is_device_online():
            self._show_error("Machine Offline", "Please wait for the device to connect.")
            return

        print(f"Selected drink: {drink['name']} (ID: {drink['id']})")
        
        if not hasattr(self.controller, 'pour_engine'):
            self._show_error("System Error", "Pour engine not initialized.")
            return
        
        self._send_dispense(lambda: self.controller.pour_engine.dispense_drink(drink['id']))

    def _show_error(self, title, message):
        # Using a Toplevel specific for CTk if possible, or standard CTk approach
        # Since we don't have CTkMessagebox, we'll make a custom one
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x200")
        popup.transient(self) # Make it modal-like
        popup.grab_set()
        
        # Center popup on screen (approx)
        popup.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 200
        y = self.winfo_screenheight() // 2 - 100
        popup.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            popup,
            text=title,
            font=("Roboto", 18, "bold"),
            text_color="#ef4444"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            popup,
            text=message,
            font=("Roboto", 14),
            wraplength=350
        ).pack(pady=10)
        
        ctk.CTkButton(
            popup,
            text="OK",
            command=popup.destroy,
            fg_color="#334155",
            hover_color="#475569",
            width=100
        ).pack(pady=20)

    def _on_custom(self):
        if not self._is_device_online():
            self._show_error("Machine Offline", "Please wait for connection.")
            return
        self.controller.show_screen("custom")

    def _on_exit(self):
        if self._status_poll_id:
            self.after_cancel(self._status_poll_id)
            self._status_poll_id = None
        if self._status_request_id:
            self.after_cancel(self._status_request_id)
            self._status_request_id = None
        self.controller.quit()

    def _on_splash(self):
        video_path = getattr(self.controller, "video_path", None)
        if not video_path:
            self._show_error("Configuration Error", "Splash video path not found.")
            return
        play_splash_video(video_path)

    def _send_dispense(self, action):
        def worker():
            success, message, msg_id, payload = action()
            def finish():
                if success:
                    print(f"Dispense successful: {message}")
                    self.controller.show_screen("processing")
                    screen = self.controller.get_screen("processing")
                    if screen:
                        relays = [job["relay"] for job in payload.get("jobs", [])]
                        screen.start_transaction(payload, msg_id, relays)
                else:
                    print(f"Dispense failed: {message}")
                    if payload:
                        self.controller.show_screen("processing")
                        screen = self.controller.get_screen("processing")
                        if screen:
                            screen.start_failure(message, payload)
                    else:
                        self._show_error("Dispense Failed", message)
            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _schedule_status_poll(self):
        if self._status_poll_id:
            self.after_cancel(self._status_poll_id)
        self._update_device_status()

    def _schedule_status_request(self):
        if self._status_request_id:
            self.after_cancel(self._status_request_id)
        self._send_status_request()

    def _is_device_online(self):
        mqtt_client = getattr(self.controller, "mqtt_client", None)
        if not mqtt_client:
            return False
        return mqtt_client.is_device_online(config.DEVICE_STATUS_TIMEOUT_SEC)

    def _update_device_status(self):
        mqtt_client = getattr(self.controller, "mqtt_client", None)
        status = "connecting"
        if mqtt_client:
            status = mqtt_client.get_device_status(config.DEVICE_STATUS_TIMEOUT_SEC)

        if status == "online":
            self.status_indicator.configure(text="● ONLINE", text_color="#22c55e")
            state = "normal"
        elif status == "offline":
            self.status_indicator.configure(text="● OFFLINE", text_color="#ef4444")
            state = "disabled"
        else:
            self.status_indicator.configure(text="● CONNECTING", text_color="#f59e0b")
            state = "disabled"

        for button in self._drink_buttons:
            button.configure(state=state)

        self._status_poll_id = self.after(1000, self._update_device_status)

    def _send_status_request(self):
        online = self._is_device_online()
        if online:
            # Check again later
            pass 
        else:
            mqtt_client = getattr(self.controller, "mqtt_client", None)
            if mqtt_client:
                mqtt_client.publish_status_request(
                    config.STATUS_REQUEST_TOPIC,
                    config.STATUS_REQUEST_PAYLOAD
                )

        interval_ms = int(config.STATUS_REQUEST_INTERVAL_SEC * 1000)
        self._status_request_id = self.after(interval_ms, self._send_status_request)

