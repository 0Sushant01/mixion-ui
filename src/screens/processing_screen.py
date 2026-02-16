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

        # Log area (hidden / subtle)
        self.log_text = ctk.CTkTextbox(
            self,
            height=100,
            fg_color="#F1F5F9",
            text_color="#334155",
            font=("Consolas", 12),
            corner_radius=10
        )
        self.log_text.pack(side="bottom", fill="x", padx=60, pady=20)
        self.log_text.configure(state="disabled")

        # Return Button
        self.return_button = ctk.CTkButton(
            self.content,
            text="RETURN TO MENU",
            command=self._on_return,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=("Roboto", 18, "bold"),
            height=60,
            width=200,
            corner_radius=30
        )
        
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
        self.message_label.configure(text="Drink Ready!", text_color="#10B981")
        self.dots_label.configure(text="✓")
        self.status_label.configure(text="Please enjoy your drink.")
        self.return_button.pack(pady=(40, 0))
    
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
        self.return_button.configure(fg_color="#2563EB", hover_color="#1D4ED8") # Reset color
        self.dot_count = 0
        self.current_msg_id = None
        self.expected_relays.clear()
        self.completed_relays.clear()
        self._is_finished = False
        self._clear_log()
        self._stop_timeout()
        self._detach_listener()
    
    def _on_return(self):
        self.controller.show_screen("menu")

    def refresh(self):
        self.reset()
        self.start_animation()

    # --- Communication Logic (same as before) ---
    def start_transaction(self, payload, msg_id, relays):
        self.reset()
        self.start_animation()
        self.current_msg_id = msg_id
        self.expected_relays = set(relays)
        self.completed_relays = set()
        self._append_log(f"SENT: {json.dumps(payload)}")
        self._attach_listener()
        self._start_timeout()

    def start_failure(self, message, payload=None):
        self.reset()
        if payload: self._append_log(f"SENT: {json.dumps(payload)}")
        self._append_log(f"ERROR: {message}")
        self.show_error(message)

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
