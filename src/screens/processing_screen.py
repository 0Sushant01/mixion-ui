import json
import time
import tkinter as tk
import customtkinter as ctk
import config

class ProcessingScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.controller = controller

        self.current_msg_id = None
        self.expected_relays = set()
        self.completed_relays = set()
        self._timeout_id = None
        self._status_listener = None
        self._is_finished = False
        self._auto_redirect_id = None
        self.current_transaction_id = None
        self._current_payload = None
        
        # --- Constants for Premium UI ---
        self.COLOR_BG = "#F8FAFC"
        self.COLOR_SUCCESS = "#10B981"
        self.COLOR_PRIMARY = "#3B82F6"
        self.COLOR_TEXT = "#1E293B"
        self.COLOR_TEXT_SUB = "#64748B"
        
        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Center Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Content Frame
        self.content = ctk.CTkFrame(self.container, fg_color="white", corner_radius=32, border_width=2, border_color="#E2E8F0")
        self.content.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.7, relheight=0.6)
        
        # Animated Canvas for Progress
        self.canvas = tk.Canvas(
            self.content,
            bg="white",
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack(pady=(40, 20), expand=True, fill="both")
        
        self.message_label = ctk.CTkLabel(
            self.content,
            text="Preparing your drink",
            font=("Roboto", 48, "bold"),
            text_color=self.COLOR_TEXT
        )
        self.message_label.pack(pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.content,
            text="Dispensing ingredients...",
            font=("Roboto", 24),
            text_color=self.COLOR_TEXT_SUB
        )
        self.status_label.pack(pady=(0, 40))

        # Bottom Menu Button (Shows on finish or error)
        self.done_btn = ctk.CTkButton(
            self.content,
            text="RETURN TO MENU",
            command=self._on_return,
            fg_color=self.COLOR_PRIMARY,
            hover_color="#2563EB",
            font=("Roboto", 24, "bold"),
            height=70,
            width=300,
            corner_radius=35
        )
        # Hidden initially
        
        # Log area (Subtle toggle-able? No, let's keep it clean but accessible)
        self.log_visible = False
        self.log_btn = ctk.CTkButton(
            self,
            text="Show Logs",
            command=self._toggle_logs,
            fg_color="transparent",
            text_color=self.COLOR_TEXT_SUB,
            hover_color="#F1F5F9",
            width=100,
            font=("Roboto", 12)
        )
        self.log_btn.place(x=20, y=self.winfo_screenheight() - 40 if self.winfo_screenheight() > 0 else 700)

        self.log_text = ctk.CTkTextbox(
            self,
            height=120,
            fg_color="#1E293B",
            text_color="#38BDF8",
            font=("Consolas", 12),
            corner_radius=12
        )
        # Hidden initially
        
        self.animation_running = False
        self.animation_angle = 0
        self.animation_id = None
    
    def _toggle_logs(self):
        self.log_visible = not self.log_visible
        if self.log_visible:
            self.log_text.place(relx=0.05, rely=0.8, relwidth=0.9)
            self.log_btn.configure(text="Hide Logs")
        else:
            self.log_text.place_forget()
            self.log_btn.configure(text="Show Logs")

    def start_animation(self):
        self._is_finished = False
        self.animation_running = True
        self.animation_angle = 0
        self.done_btn.pack_forget()
        self._draw_frame()
    
    def stop_animation(self):
        self.animation_running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
    
    def _draw_frame(self):
        if not self.animation_running: return
        
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w < 10 or h < 10: # Not laid out yet
            self.after(100, self._draw_frame)
            return

        cx, cy = w // 2, h // 2
        r = 80
        
        # Draw base circle
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#E2E8F0", width=8)
        
        # Draw rotating arc
        extent = 90
        self.canvas.create_arc(
            cx-r, cy-r, cx+r, cy+r, 
            start=self.animation_angle, 
            extent=extent, 
            outline=self.COLOR_PRIMARY, 
            width=8, 
            style="arc"
        )
        
        self.animation_angle = (self.animation_angle + 10) % 360
        self.animation_id = self.after(30, self._draw_frame)
    
    def show_complete(self):
        self._is_finished = True
        self.stop_animation()
        
        # UI Updates
        self.message_label.configure(text="Perfect Pour!", text_color=self.COLOR_SUCCESS)
        self.status_label.configure(text="Your drink is ready. Enjoy!")
        
        # Draw checkmark on canvas
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Animated Checkmark
        self._draw_checkmark(cx, cy, 80)
        
        self.done_btn.pack(pady=(20, 0))
        
        # Auto-redirect after 4 seconds
        self._auto_redirect_id = self.after(4000, self._on_return)
        
        # Database Update
        if self.current_transaction_id:
            self.controller.database.update_transaction_status(self.current_transaction_id, "completed")

    def _draw_checkmark(self, cx, cy, size):
        # Draw green circle
        self.canvas.create_oval(cx-size, cy-size, cx+size, cy+size, fill=self.COLOR_SUCCESS, outline="")
        
        # Draw white checkmark
        # Coordinates relative to center
        # Point 1: -size*0.4, cy+size*0.1
        # Point 2: -size*0.1, cy+size*0.4
        # Point 3: size*0.5, cy-size*0.3
        self.canvas.create_line(
            cx - (size * 0.4), cy + (size * 0.1),
            cx - (size * 0.1), cy + (size * 0.4),
            cx + (size * 0.5), cy - (size * 0.3),
            fill="white", width=12, capstyle="round", joinstyle="round"
        )

    def show_error(self, error_message):
        self._is_finished = True
        self.stop_animation()
        self.message_label.configure(text="System Error", text_color="#DC2626")
        self.status_label.configure(text=error_message)
        
        # Draw error icon
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        size = 80
        
        self.canvas.create_oval(cx-size, cy-size, cx+size, cy+size, fill="#DC2626", outline="")
        self.canvas.create_line(cx-30, cy-30, cx+30, cy+30, fill="white", width=12, capstyle="round")
        self.canvas.create_line(cx+30, cy-30, cx-30, cy+30, fill="white", width=12, capstyle="round")
        
        self.done_btn.configure(fg_color="#DC2626", hover_color="#B91C1C")
        self.done_btn.pack(pady=(20, 0))

        # Database Update
        if self.current_transaction_id:
            self.controller.database.update_transaction_status(self.current_transaction_id, f"failed: {error_message}")
            self.controller.database.add_transaction_log(self.current_transaction_id, "ERR", "DISPENSE_ERROR", error_message)
    
    def reset(self):
        self.stop_animation()
        self.message_label.configure(text="Preparing your drink", text_color=self.COLOR_TEXT)
        self.status_label.configure(text="Dispensing ingredients...")
        self.done_btn.pack_forget()
        self.done_btn.configure(fg_color=self.COLOR_PRIMARY, hover_color="#2563EB")
        
        if self._auto_redirect_id:
            self.after_cancel(self._auto_redirect_id)
            self._auto_redirect_id = None
            
        self.current_msg_id = None
        self.expected_relays.clear()
        self.completed_relays.clear()
        self._is_finished = False
        self._clear_log()
        self._stop_timeout()
        self._detach_listener()
    
    def _on_return(self):
        if self._auto_redirect_id:
            self.after_cancel(self._auto_redirect_id)
            self._auto_redirect_id = None
        self.current_transaction_id = None
        self._current_payload = None
        # self.overlay.place_forget() # This line was in the diff but 'overlay' is not defined in this class.
        self.controller.show_screen("menu")

    def refresh(self):
        self.reset()
        self.start_animation()

    # --- Communication Logic ---
    def start_transaction(self, payload, msg_id, relays, drink_name=None):
        self.reset()
        self.start_animation()
        self.current_msg_id = msg_id
        self._current_payload = payload
        self.expected_relays = set(relays)
        self.completed_relays = set()
        
        # Database Start
        try:
            name = drink_name or "Unknown Drink"
            self.current_transaction_id = self.controller.database.start_transaction(name, msg_id)
        except Exception as e:
            print(f"Error starting DB transaction: {e}")
            self.current_transaction_id = None

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
        
        # Persistent DB Logging
        if self.current_transaction_id:
            try:
                self.controller.database.add_transaction_log(
                    self.current_transaction_id,
                    direction,
                    event_type,
                    content
                )
            except Exception as e:
                print(f"Failed to log to DB: {e}")

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
        self._log_event("RX", "MQTT_MESSAGE", json.dumps(data, indent=None)) 
        
        msg_id, status = str(data.get("msg_id", "")), str(data.get("status", "")).lower()
        if msg_id != self.current_msg_id: return
        
        relay = data.get("relay")
        if status in ("error", "failed"):
            self.show_error("Hardware Error Reported")
            return
            
        if relay is not None and status == "completed":
            relay_int = int(relay)
            self.completed_relays.add(relay_int)
            
            # Find amount dispensed for this bottle (removed from payload)
            amount = 0
            if self._current_payload:
                for job in self._current_payload.get("jobs", []):
                    if job.get("relay") == relay_int:
                        amount = job.get("amount_ml", 0) # Kept fallback in case it's passed differently
                        break
            
            # DB Logging: Record bottle completion
            if self.current_transaction_id:
                try:
                    self.controller.database.add_transaction_item(
                        self.current_transaction_id,
                        relay_int,
                        amount,
                        "completed"
                    )
                except Exception as e:
                    print(f"Error logging bottle completion: {e}")

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
            self.show_error("Dispense Timeout - Check Device")
        else:
            self._timeout_id = self.after(500, self._check_timeout)
