import tkinter as tk
import threading
import os
import customtkinter as ctk
from PIL import Image

import config
from src.screens.splash_screen import play_splash_video


class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=0)
        self.controller = controller
        self.database = controller.database
        self._drink_buttons = []
        self._status_poll_id = None
        self._status_request_id = None
        self._images = [] # Keep references to avoid garbage collection

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Content area expands

        # --- Header ---
        self.header = ctk.CTkFrame(self, fg_color="#FFFFFF", height=80, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        self.header.grid_columnconfigure(1, weight=1)  # Spacer

        # Title Section
        self.title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="MIXION",
            font=("Roboto", 32, "bold"),
            text_color="black"
        )
        self.title_label.pack(side="left")

        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="Select Your Drink",
            font=("Roboto", 16),
            text_color="gray40"
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

    def _load_drink_image(self, drink_id):
        """Load image from assets/drinks/{id}.[png|jpg] or return None"""
        if not hasattr(config, 'DRINK_IMAGES_DIR'):
             return None
             
        extensions = ['.png', '.jpg', '.jpeg']
        for ext in extensions:
            path = os.path.join(config.DRINK_IMAGES_DIR, f"{drink_id}{ext}")
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path)
                    # Resize to fit the card image area (approx 300x200 or similar)
                    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(250, 180))
                except Exception as e:
                    print(f"Error loading image for drink {drink_id}: {e}")
                    return None
        return None

    def _create_drink_card(self, drink, row, col):
        is_custom = drink["id"] == "custom"
        
        # Light theme colors
        card_color = "#F8FAFC" if not is_custom else "#F0FDF4"
        border_color = "#E2E8F0" if not is_custom else "#BBF7D0"
        text_color = "#1E293B"
        subtext_color = "#64748B"
        accent_color = "#3B82F6" if not is_custom else "#10B981"
        hover_color = "#2563EB" if not is_custom else "#059669"

        card = ctk.CTkFrame(
            self.content,
            fg_color=card_color,
            border_width=1,
            border_color=border_color,
            corner_radius=16
        )
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

        # Image / Icon Area
        # Try to load image
        drink_image = self._load_drink_image(drink["id"]) if not is_custom else None
        
        if drink_image:
            self._images.append(drink_image) # Keep reference
            img_label = ctk.CTkLabel(
                card,
                text="",
                image=drink_image,
                corner_radius=12
            )
            img_label.pack(fill="x", padx=0, pady=(0, 10))
            # Hack to round top corners? CTk doesn't support partial radius easily. 
            # We'll just stick to standard image for now.
        else:
            # Fallback to Icon
            icon_frame = ctk.CTkFrame(
                card,
                fg_color="#F1F5F9" if not is_custom else "#DCFCE7",
                height=140,
                corner_radius=12
            )
            icon_frame.pack(fill="x", padx=15, pady=15)
            icon_frame.pack_propagate(False)

            icon_text = "🍸" if not is_custom else "🧪"
            ctk.CTkLabel(
                icon_frame,
                text=icon_text,
                font=("Segoe UI Emoji", 56),
                text_color="#94A3B8" if not is_custom else "#10B981"
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Drink Name
        display_name = drink["name"] if not is_custom else "Design Your Own"
        ctk.CTkLabel(
            card,
            text=display_name,
            font=("Roboto", 20, "bold"),
            text_color=text_color,
            wraplength=220
        ).pack(fill="x", padx=15, pady=(5, 2))

        # Ingredients (Fetch from DB)
        ingredients_text = ""
        if not is_custom:
            try:
                recipes = self.database.get_recipes_for_drink(drink["id"])
                # recipes returned as list of dicts with 'bottle_name'
                ing_names = [r['bottle_name'] for r in recipes]
                ingredients_text = ", ".join(ing_names)
            except Exception as e:
                print(f"Error fetching recipes: {e}")
                ingredients_text = "Ingredients info unavailable"
        else:
            ingredients_text = "Mix your own custom drink"

        if ingredients_text:
             ctk.CTkLabel(
                card,
                text=ingredients_text,
                font=("Roboto", 13),
                text_color=subtext_color,
                wraplength=220,
                height=40 # Fixed height for alignment
            ).pack(fill="x", padx=15, pady=(0, 10))


        # Price (shifted down)
        price_text = " "
        if not is_custom and drink.get("price"):
            price_text = f"${drink['price']}"
        
        ctk.CTkLabel(
            card,
            text=price_text,
            font=("Roboto", 16, "bold"),
            text_color=text_color
        ).pack(fill="x", padx=15, pady=(0, 15))

        # Select Button
        btn_text = "Order Now" if not is_custom else "Start Mixing"
        command = (self._on_custom if is_custom else lambda d=drink: self._on_drink(d))
        
        btn = ctk.CTkButton(
            card,
            text=btn_text,
            command=command,
            fg_color=accent_color,
            hover_color=hover_color,
            text_color="white",
            font=("Roboto", 14, "bold"),
            height=44,
            corner_radius=10
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

