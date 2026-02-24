import json
import time
import customtkinter as ctk
import config

class ProcessingScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white", corner_radius=0)
        self.controller = controller

        self.current_msg_id = None
        self.expected_relays = set()
        self.completed_relays = set()
        self._timeout_id = None
        self._status_listener = None
        self._is_finished = False
        self._auto_redirect_id = None
        
        # Center Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.4, anchor="center")
        
        self.message_label = ctk.CTkLabel(
            self.content,
            text="Preparing your drink",
            font=("Roboto", 40, "bold"),
            text_color="#1E293B"
        )
        self.message_label.pack(pady=(0, 20))
        
        self.dots_label = ctk.CTkLabel(
            self.content,
            text="",
            font=("Roboto", 60, "bold"),
            text_color="#3B82F6"
        )
        self.dots_label.pack()
        
        self.status_label = ctk.CTkLabel(
            self.content,
            text="",
            font=("Roboto", 20),
            text_color="#64748B"
        )
        self.status_label.pack(pady=(20, 0))

        # Back Button (Always Visible)
        self.back_btn = ctk.CTkButton(
            self,
            text="< MENU",
            command=self._on_return,
            fg_color="#F1F5F9",
            text_color="#64748B",
            hover_color="#E2E8F0",
            font=("Roboto", 14, "bold"),
            width=100,
            height=40,
            corner_radius=20
        )
        self.back_btn.place(x=30, y=30)

        # Log area (Visible Debug Console)
        self.log_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_frame.pack(side="bottom", fill="both", expand=True, padx=40, pady=(0, 10))
        
        ctk.CTkLabel(
            self.log_frame, 
            text="COMMUNICATION LOG", 
            font=("Roboto", 12, "bold"), 
            text_color="#94A3B8",
            anchor="w"
        ).pack(fill="x", pady=(10, 5))

        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            height=150,
            fg_color="#1E293B",      # Dark terminal background
            text_color="#38BDF8",    # Light Blue text for generic info
            font=("Consolas", 14),
            corner_radius=12,
            border_width=0
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

        # Bottom Menu Button Footer
        footer = ctk.CTkFrame(self, fg_color="white", height=70, corner_radius=0)
        footer.pack(side="bottom", fill="x", padx=0, pady=0)
        
        ctk.CTkButton(
            footer,
            text="BACK TO MENU",
            command=self._on_return,
            fg_color="#2563EB",
            text_color="white",
            hover_color="#1D4ED8",
            font=("Roboto", 16, "bold"),
            width=200,
            height=50,
            corner_radius=25
        ).pack(pady=10)

        # Return Button (Initially Hidden)
        self.return_button = ctk.CTkButton(
            self.content,
            text="DONE",
            command=self._on_return,
            fg_color=config.COLOR_SUCCESS if hasattr(config, 'COLOR_SUCCESS') else "#10B981",
            hover_color="#059669",
            font=("Roboto", 20, "bold"),
            height=60,
            width=220,
            corner_radius=30
        )
        
        # Success Overlay Canvas (for animations)
        self.overlay = tk.Canvas(
            self,
            bg="white",
            highlightthickness=0,
            borderwidth=0
        )
        # Keep hidden initially
        
        self.animation_running = False
        self.dot_count = 0
        self.animation_id = None
    
    def start_animation(self):
        self.animation_running = True
        self.dot_count = 0
        self.return_button.pack_forget()
        self._animate()
    
    def stop_animation(self):
        self.animation_running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
    
    def _animate(self):
        if not self.animation_running: return
        dots = "." * (self.dot_count + 1)
        self.dots_label.configure(text=dots)
        self.dot_count = (self.dot_count + 1) % 3
        self.animation_id = self.after(500, self._animate)
    
    def show_complete(self):
        self._is_finished = True
        self.stop_animation()
        
        # UI Updates
        self.message_label.configure(text="Drink Ready!", text_color="#10B981")
        self.dots_label.configure(text="✓", text_color="#10B981")
        self.status_label.configure(text="Please enjoy your drink. Returning to menu soon...")
        self.return_button.pack(pady=(40, 0))
        
        # Trigger Success Animation
        self._play_success_animation()
        
        # Auto-redirect after 3 seconds
        self._auto_redirect_id = self.after(3500, self._on_return)

    def _play_success_animation(self):
        """Play a celebratory pulse animation"""
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.overlay.delete("all")
        
        # Draw background burst or pulse? 
        # Let's do a simple expanding circle pulse
        cx = self.winfo_width() // 2
        cy = self.winfo_height() // 2
        
        def pulse(radius, alpha):
            if not self._is_finished or radius > 1000: 
                self.overlay.place_forget()
                return
            
            self.overlay.delete("pulse")
            # Draw circle (simulating transparency with color blending since tk canvas has limited alpha)
            # We'll use a few shades of green
            colors = ["#D1FAE5", "#A7F3D0", "#6EE7B7", "#34D399", "#10B981"]
            color_idx = min(int(radius / 200), len(colors)-1)
            
            self.overlay.create_oval(
                cx - radius, cy - radius, 
                cx + radius, cy + radius, 
                fill="", outline=colors[color_idx], width=5, tags="pulse"
            )
            
            self.after(20, lambda: pulse(radius + 25, alpha))

        pulse(50, 255)
    
    def show_error(self, error_message):
        self._is_finished = True
        self.stop_animation()
        self.message_label.configure(text="Error", text_color="#DC2626")
        self.dots_label.configure(text="✗")
        self.status_label.configure(text=error_message)
        self.return_button.configure(fg_color="#DC2626", hover_color="#B91C1C")
        self.return_button.pack(pady=(40, 0))
    
    def reset(self):
        self.message_label.configure(text="Preparing your drink", text_color="#1E293B")
        self.dots_label.configure(text="")
        self.status_label.configure(text="")
        self.return_button.pack_forget()
        self.return_button.configure(fg_color="#2563EB", hover_color="#1D4ED8") 
        self.dot_count = 0
        self.current_msg_id = None
        self.expected_relays.clear()
        self.completed_relays.clear()
        self._is_finished = False
        if self._auto_redirect_id:
            self.after_cancel(self._auto_redirect_id)
            self._auto_redirect_id = None
        self.overlay.place_forget()
        self._detach_listener()
    
    def _on_return(self):
        self.controller.show_screen("menu")

    def refresh(self):
        self.reset()
        self.start_animation()

    # --- Communication Logic ---
    def start_transaction(self, payload, msg_id, relays):
        self.reset()
        self.start_animation()
        self.current_msg_id = msg_id
        self.expected_relays = set(relays)
        self.completed_relays = set()
        
        self._log_event("TX", "DISPENSE_COMMAND", json.dumps(payload, indent=2))
        self._attach_listener()
        self._start_timeout()

    def start_failure(self, message, payload=None):
        self.reset()
        if payload: self._log_event("TX", "DISPENSE_COMMAND", json.dumps(payload, indent=2))
        self._log_event("ERR", "DISPENSE_FAILED", message)
        self.show_error(message)

    def _log_event(self, direction, event_type, content):
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] {direction} | {event_type}"
        full_msg = f"{prefix}\n{content}\n" + "-"*40
        self._append_log(full_msg)

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _attach_listener(self):
        client = getattr(self.controller, "mqtt_client", None)
        if not client: return
        self._status_listener = lambda data: self.after(0, lambda: self._handle_status(data))
        client.add_status_listener(self._status_listener)

    def _detach_listener(self):
        client = getattr(self.controller, "mqtt_client", None)
        if client and self._status_listener:
            client.remove_status_listener(self._status_listener)
            self._status_listener = None

    def _handle_status(self, data):
        if self._is_finished: return
        # Log RAW received data first
        self._log_event("RX", "MQTT_MESSAGE", json.dumps(data, indent=None)) 
        
        msg_id, status = str(data.get("msg_id", "")), str(data.get("status", "")).lower()
        if msg_id != self.current_msg_id: return
        
        relay = data.get("relay")
        if status in ("error", "failed"):
            self.show_error("Device Error")
            return
            
        if relay is not None and status == "completed":
            self.completed_relays.add(int(relay))
            if self.completed_relays.issuperset(self.expected_relays):
                self.show_complete()
                self._stop_timeout()

    def _start_timeout(self):
        self._stop_timeout()
        self._deadline = time.time() + config.DISPENSE_TIMEOUT_SEC
        self._timeout_id = self.after(500, self._check_timeout)

    def _stop_timeout(self):
        if self._timeout_id:
            self.after_cancel(self._timeout_id)
            self._timeout_id = None

    def _check_timeout(self):
        if self._is_finished: return
        if time.time() >= self._deadline:
            self.show_error("Operation Timed Out")
        else:
            self._timeout_id = self.after(500, self._check_timeout)
