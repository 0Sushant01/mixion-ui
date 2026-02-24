import tkinter as tk
import threading
import os
import customtkinter as ctk
from PIL import Image

import config
from src.screens.splash_screen import play_splash_video


class MenuScreen(ctk.CTkFrame):
    _image_cache = {}  # Class-level cache to persist across instances

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.controller = controller
        self.database = controller.database
        self._drink_buttons = []
        self._status_poll_id = None
        self._status_request_id = None
        
        # --- Inactivity Timer (Idle Timeout) ---
        self._idle_timer_id = None
        self._idle_timeout_ms = 60000  # 60 seconds

        # --- Constants for Kiosk UI ---
        self.HEADER_HEIGHT = 100
        self.TITLE_FONT = ("Roboto", 48, "bold")
        self.SUBTITLE_FONT = ("Roboto", 24)
        self.CARD_TITLE_FONT = ("Roboto", 24, "bold")
        self.CARD_PRICE_FONT = ("Roboto", 22, "bold")
        self.CARD_INGR_FONT = ("Roboto", 16)
        self.BTN_FONT = ("Roboto", 18, "bold")
        
        self.COLOR_PRIMARY = "#2563EB"    # Deep Blue
        self.COLOR_SUCCESS = "#059669"    # Emerald Green
        self.COLOR_DANGER = "#DC2626"     # Red
        self.COLOR_TEXT = "#111827"       # Almost Black
        self.COLOR_TEXT_SUB = "#6B7280"   # Gray

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header
        self._build_header()

        # 2. Content Grid
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#E2E8F0",
            scrollbar_button_hover_color="#CBD5E1"
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        
        # Grid Configuration: 3 Columns, responsive
        self.content.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        self.empty_label = ctk.CTkLabel(
            self,
            text="No drinks available",
            font=("Roboto", 32, "bold"),
            text_color=self.COLOR_TEXT_SUB
        )

        self.refresh()
        self._schedule_status_poll()
        self._schedule_status_request()

        self._reset_inactivity_timer()
        
        # Bind events to reset timer on interaction
        self.bind("<Button-1>", lambda e: self._reset_inactivity_timer())
        self.bind("<Key>", lambda e: self._reset_inactivity_timer())
        # Also bind to the content area
        self.content.bind("<Button-1>", lambda e: self._reset_inactivity_timer())

    def _reset_inactivity_timer(self):
        """Reset the 60s idle timer"""
        if self._idle_timer_id:
            self.after_cancel(self._idle_timer_id)
        self._idle_timer_id = self.after(self._idle_timeout_ms, self._on_idle_timeout)

    def _on_idle_timeout(self):
        """Called when no activity for 60s"""
        print("Menu idle timeout reached - returning to splash")
        self._on_splash()

    def _build_header(self):
        self.header = ctk.CTkFrame(
            self, 
            fg_color="white", 
            height=self.HEADER_HEIGHT, 
            corner_radius=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False) # Fixed height

        # Inner Container for margins
        container = ctk.CTkFrame(self.header, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40)

        # Left: Brand
        brand_frame = ctk.CTkFrame(container, fg_color="transparent")
        brand_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            brand_frame,
            text="MIXION",
            font=self.TITLE_FONT,
            text_color=self.COLOR_TEXT
        ).pack(side="left", anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="Touch to Order",
            font=self.SUBTITLE_FONT,
            text_color=self.COLOR_TEXT_SUB
        ).pack(side="left", padx=(20, 0), pady=(12, 0)) # Align baseline approx

        # Right: Status & Admin
        status_frame = ctk.CTkFrame(container, fg_color="transparent")
        status_frame.pack(side="right", fill="y")

        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="● CONNECTING",
            font=("Roboto", 16, "bold"),
            text_color="#F59E0B",
            anchor="e"
        )
        self.status_indicator.pack(side="left", padx=(0, 30))

        # Admin controls (subtle)
        self.splash_btn = ctk.CTkButton(
            status_frame,
            text="Admin",
            command=self._on_splash,
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color="#64748B",
            width=80,
            height=40,
            font=("Roboto", 14),
            corner_radius=20
        )
        self.splash_btn.pack(side="left", padx=(0, 10))

        self.exit_btn = ctk.CTkButton(
            status_frame,
            text="✕",
            command=self._on_exit,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color=self.COLOR_DANGER,
            width=50,
            height=40,
            font=("Roboto", 18, "bold"),
            corner_radius=20
        )
        self.exit_btn.pack(side="left")

    def refresh(self):
        self._reset_inactivity_timer()
        for widget in self.content.winfo_children():
            widget.destroy()
        self._drink_buttons.clear()
        # No need to clear cache here

        drinks = self.database.get_active_drinks()
        
        if not drinks:
            self.content.grid_forget()
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        self.empty_label.place_forget()
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)

        # Combine drinks and Custom option
        tiles = drinks + [{"id": "custom", "name": "Design Your Own", "price": None}]

        for idx, drink in enumerate(tiles):
            row = idx // 3
            col = idx % 3
            self._create_kiosk_card(drink, row, col)

    def _create_kiosk_card(self, drink, row, col):
        is_custom = drink["id"] == "custom"
        
        # Colors
        bg_color = "white" if not is_custom else "#ECFDF5" # Mint hint for custom
        border_color = "#E5E7EB" if not is_custom else "#10B981"
        btn_color = self.COLOR_PRIMARY if not is_custom else self.COLOR_SUCCESS
        btn_hover = "#1D4ED8" if not is_custom else "#047857" # Darker shades

        # Card Container
        card = ctk.CTkFrame(
            self.content,
            fg_color=bg_color,
            border_width=2,
            border_color=border_color,
            corner_radius=24
        )
        card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

        # 1. Image Area (Large)
        img_h = 220
        drink_image = self._load_drink_image(drink["id"]) if not is_custom else None
        
        if drink_image:
            # Image Container for centering/cropping visuals
            img_container = ctk.CTkLabel(
                card,
                text="",
                image=drink_image,
                corner_radius=20
            ) 
            img_container.pack(fill="x", padx=4, pady=(4, 10))
            # Note: CTk image rounding clips corners visually if image has alpha or matches bg
        else:
            # Placeholder Icon
            icon_frame = ctk.CTkFrame(
                card,
                fg_color="#F3F4F6" if not is_custom else "#D1FAE5",
                height=img_h,
                corner_radius=20
            )
            icon_frame.pack(fill="x", padx=4, pady=(4, 15))
            icon_frame.pack_propagate(False)

            icon = "🍸" if not is_custom else "✨"
            ctk.CTkLabel(
                icon_frame,
                text=icon,
                font=("Segoe UI Emoji", 80),
                text_color="#9CA3AF" if not is_custom else "#10B981"
            ).place(relx=0.5, rely=0.5, anchor="center")

        # 2. Text Content
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=24, pady=(5, 20))

        # Title
        ctk.CTkLabel(
            text_frame,
            text=drink["name"],
            font=self.CARD_TITLE_FONT,
            text_color=self.COLOR_TEXT,
            wraplength=280,
            justify="left",
            anchor="w"
        ).pack(fill="x")

        # Ingredients / Approx Info
        info_text = ""
        if not is_custom:
            try:
                recipes = self.database.get_recipes_for_drink(drink["id"])
                ing_names = [r['bottle_name'] for r in recipes]
                info_text = ", ".join(ing_names) if ing_names else "Ingredients unavailable"
            except:
                info_text = "Standard Mix"
        else:
            info_text = "Create your perfect blend from available ingredients."

        ctk.CTkLabel(
            text_frame,
            text=info_text,
            font=self.CARD_INGR_FONT,
            text_color=self.COLOR_TEXT_SUB,
            wraplength=280,
            justify="left",
            anchor="w",
            height=40 # Force 2 lines height approx
        ).pack(fill="x", pady=(8, 15))

        # Price & Action Row
        action_row = ctk.CTkFrame(text_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=(5, 0))

        if not is_custom:
            price_val = f"${drink.get('price', 0)}"
            ctk.CTkLabel(
                action_row,
                text=price_val,
                font=self.CARD_PRICE_FONT,
                text_color=self.COLOR_SUCCESS
            ).pack(side="left")

        # Button
        btn_text = "ORDER" if not is_custom else "START"
        command = (self._on_custom if is_custom else lambda d=drink: self._on_drink(d))

        btn = ctk.CTkButton(
            action_row,
            text=btn_text,
            command=command,
            fg_color=btn_color,
            hover_color=btn_hover,
            font=self.BTN_FONT,
            height=56, # Tall touch target
            corner_radius=28,
            width=140 if not is_custom else 280 # Full width for custom if no price
        )
        btn.pack(side="right" if not is_custom else "top", fill="x" if is_custom else "none")
        self._drink_buttons.append(btn)

    def _load_drink_image(self, drink_id):
        if drink_id in self._image_cache:
            return self._image_cache[drink_id]

        if not hasattr(config, 'DRINK_IMAGES_DIR'): return None
        extensions = ['.png', '.jpg', '.jpeg']
        for ext in extensions:
            path = os.path.join(config.DRINK_IMAGES_DIR, f"{drink_id}{ext}")
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path)
                    # Kiosk resizing: larger!
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(320, 240))
                    self._image_cache[drink_id] = ctk_img
                    return ctk_img
                except Exception as e:
                    print(f"Error loading image {drink_id}: {e}")
        return None

    # --- Event Handlers (Logic remains mostly same) ---
    def _on_drink(self, drink):
        if not self._is_device_online():
            self._show_error("Machine Offline", "Please check device connection.")
            return
        
        # Add visual feedback here if needed (e.g. disabled loading state)
        if not hasattr(self.controller, 'pour_engine'):
             self._show_error("System Error", "Pour engine not initialized.")
             return
        
        self._reset_inactivity_timer()
        self._send_dispense(lambda: self.controller.pour_engine.dispense_drink(drink['id']))

    def _on_custom(self):
        if not self._is_device_online():
            self._show_error("Machine Offline", "Please check device connection.")
            return
        self._reset_inactivity_timer()
        self.controller.show_screen("custom")

    def _on_exit(self):
        # Cleanup
        if self._idle_timer_id: self.after_cancel(self._idle_timer_id)
        if self._status_poll_id: self.after_cancel(self._status_poll_id)
        if self._status_request_id: self.after_cancel(self._status_request_id)
        self.controller.quit()

    def _on_splash(self):
        video_path = getattr(self.controller, "video_path", None)
        if video_path: play_splash_video(video_path)

    def _show_error(self, title, message):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("500x300")
        popup.transient(self)
        popup.grab_set()
        popup.configure(fg_color="white")
        
        # Center
        popup.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 250
        y = self.winfo_screenheight() // 2 - 150
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            popup, 
            text="⚠️ " + title, 
            font=("Roboto", 24, "bold"), 
            text_color=self.COLOR_DANGER
        ).pack(pady=(40, 20))
        
        ctk.CTkLabel(
            popup, 
            text=message, 
            font=("Roboto", 18), 
            text_color=self.COLOR_TEXT,
            wraplength=400
        ).pack(pady=10)
        
        ctk.CTkButton(
            popup, 
            text="Dismiss", 
            command=popup.destroy,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="black",
            height=50,
            width=150,
            font=("Roboto", 16, "bold"),
            corner_radius=25
        ).pack(pady=30)

    # --- Workflow Helpers ---
    def _send_dispense(self, action):
        def worker():
            success, message, msg_id, payload = action()
            def finish():
                if success:
                    print(f"Dispense successful: {message}")
                    self.controller.show_screen("processing")
                    screen = self.controller.get_screen("processing")
                    # Pass details...
                    if screen and payload:
                         relays = [job["relay"] for job in payload.get("jobs", [])]
                         screen.start_transaction(payload, msg_id, relays, drink_name=drink['name'])
                else:
                    self._show_error("Dispense Failed", message)
            self.after(0, finish)
        threading.Thread(target=worker, daemon=True).start()

    # --- Status Helpers ---
    def _schedule_status_poll(self):
        if self._status_poll_id: self.after_cancel(self._status_poll_id)
        self._update_device_status()

    def _schedule_status_request(self):
        if self._status_request_id: self.after_cancel(self._status_request_id)
        self._send_status_request()

    def _is_device_online(self):
        client = getattr(self.controller, "mqtt_client", None)
        return client.is_device_online(config.DEVICE_STATUS_TIMEOUT_SEC) if client else False

    def _update_device_status(self):
        client = getattr(self.controller, "mqtt_client", None)
        status = client.get_device_status(config.DEVICE_STATUS_TIMEOUT_SEC) if client else "connecting"

        if status == "online":
            self.status_indicator.configure(text="● ONLINE", text_color=self.COLOR_SUCCESS)
            state = "normal"
        elif status == "offline":
            self.status_indicator.configure(text="● OFFLINE", text_color=self.COLOR_DANGER)
            state = "disabled"
        else:
            self.status_indicator.configure(text="● CONNECTING", text_color="#F59E0B")
            state = "disabled"

        for btn in self._drink_buttons:
            # Maybe don't disable UI completely, just show toast on click?
            # User requirement: "Instant response". Disabling looks dead.
            # But let's stick to functional requirement "Keep functionality same" for now, just visual upgrade.
            try: btn.configure(state=state)
            except: pass

        self._status_poll_id = self.after(1000, self._update_device_status)

    def _send_status_request(self):
        if not self._is_device_online():
            client = getattr(self.controller, "mqtt_client", None)
            if client: client.publish_status_request(config.STATUS_REQUEST_TOPIC, config.STATUS_REQUEST_PAYLOAD)
        
        interval = int(config.STATUS_REQUEST_INTERVAL_SEC * 1000)
        self._status_request_id = self.after(interval, self._send_status_request)

