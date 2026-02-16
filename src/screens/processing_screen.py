"""
Processing Screen
Displays while drink is being prepared
"""

import json
import time
import tkinter as tk

import config


class ProcessingScreen(tk.Frame):
    """Screen shown while drink is being dispensed"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFFFFF")
        self.controller = controller

        self.current_msg_id = None
        self.expected_relays = set()
        self.completed_relays = set()
        self._timeout_id = None
        self._status_listener = None
        self._is_finished = False
        
        # Main content
        content = tk.Frame(self, bg="#FFFFFF")
        content.place(relx=0.5, rely=0.45, anchor="center")
        
        # Animated dots will be added to this
        self.message_label = tk.Label(
            content,
            text="Preparing your drink",
            fg="#1E293B",
            bg="#FFFFFF",
            font=("Arial", 32, "bold")
        )
        self.message_label.pack(pady=(0, 30))
        
        # Dots for animation
        self.dots_label = tk.Label(
            content,
            text="",
            fg="#3B82F6",
            bg="#FFFFFF",
            font=("Arial", 32, "bold")
        )
        self.dots_label.pack()
        
        # Status message (optional)
        self.status_label = tk.Label(
            content,
            text="",
            fg="#64748B",
            bg="#FFFFFF",
            font=("Arial", 16)
        )
        self.status_label.pack(pady=(10, 0))

        # Log area
        self.log_frame = tk.Frame(self, bg="#FFFFFF")
        self.log_frame.pack(fill="both", expand=True, padx=60, pady=(20, 20))

        self.log_text = tk.Text(
            self.log_frame,
            height=8,
            bg="#F1F5F9",
            fg="#334155",
            insertbackground="#334155",
            font=("Consolas", 11),
            relief="flat",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")
        
        # Return button (hidden by default, shown after pour completes)
        self.return_button = tk.Button(
            content,
            text="RETURN TO MENU",
            command=self._on_return,
            bg="#1f6feb",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=15,
            relief="flat",
            cursor="hand2"
        )

        self.menu_button = tk.Button(
            self,
            text="MENU",
            command=self._on_menu,
            bg="#334155",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=24,
            pady=10,
            relief="flat"
        )
        self.menu_button.pack(side="bottom", pady=(0, 20))
        
        # Animation state
        self.animation_running = False
        self.dot_count = 0
        self.animation_id = None
    
    def start_animation(self):
        """Start the loading animation"""
        self.animation_running = True
        self.dot_count = 0
        self.return_button.pack_forget()
        self._animate()
    
    def stop_animation(self):
        """Stop the loading animation"""
        self.animation_running = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
    
    def _animate(self):
        """Animate the dots"""
        if not self.animation_running:
            return
        
        dots = "." * (self.dot_count + 1)
        self.dots_label.config(text=dots)
        
        self.dot_count = (self.dot_count + 1) % 3
        
        self.animation_id = self.after(500, self._animate)
    
    def set_status(self, message):
        """Update the status message"""
        self.status_label.config(text=message)
    
    def show_complete(self):
        """Show completion state"""
        self._is_finished = True
        self.stop_animation()
        self.message_label.config(text="Your drink is ready!", fg="#22c55e")
        self.dots_label.config(text="✓")
        self.status_label.config(text="Enjoy!")
        self.return_button.pack(pady=(30, 0))
    
    def show_error(self, error_message):
        """Show error state"""
        self._is_finished = True
        self.stop_animation()
        self.message_label.config(text="Something went wrong", fg="#ef4444")
        self.dots_label.config(text="✗")
        self.status_label.config(text=error_message)
        self.return_button.pack(pady=(30, 0))
    
    def reset(self):
        """Reset to initial state"""
        self.message_label.config(text="Preparing your drink", fg="#1E293B")
        self.dots_label.config(text="")
        self.status_label.config(text="")
        self.return_button.pack_forget()
        self.dot_count = 0
        self.current_msg_id = None
        self.expected_relays.clear()
        self.completed_relays.clear()
        self._is_finished = False
        self._clear_log()
        self._stop_timeout()
        self._detach_listener()
    
    def _on_return(self):
        """Return to menu"""
        self.controller.show_screen("menu")

    def _on_menu(self):
        self.reset()
        self.controller.show_screen("menu")
    
    def refresh(self):
        """Called when screen is shown"""
        self.reset()
        self.start_animation()

    def start_transaction(self, payload, msg_id, relays):
        self.reset()
        self.start_animation()

        self.current_msg_id = msg_id
        self.expected_relays = set(relays)
        self.completed_relays = set()

        self._append_log("SENT:")
        self._append_log(json.dumps(payload, indent=2))

        self._attach_listener()
        self._start_timeout()

    def start_failure(self, message, payload=None):
        self.reset()
        if payload:
            self._append_log("SENT:")
            self._append_log(json.dumps(payload, indent=2))
        self._append_log("RECEIVED:")
        self._append_log(message)
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
        mqtt_client = getattr(self.controller, "mqtt_client", None)
        if not mqtt_client:
            return

        def listener(data):
            self.after(0, lambda: self._handle_status(data))

        self._status_listener = listener
        mqtt_client.add_status_listener(listener)

    def _detach_listener(self):
        mqtt_client = getattr(self.controller, "mqtt_client", None)
        if not mqtt_client or not self._status_listener:
            return
        mqtt_client.remove_status_listener(self._status_listener)
        self._status_listener = None

    def _handle_status(self, data):
        if self._is_finished:
            return

        msg_id = str(data.get("msg_id", ""))
        if not msg_id or msg_id != self.current_msg_id:
            return

        status = str(data.get("status", "")).lower()
        relay = data.get("relay")

        if status in ("error", "failed"):
            self._append_log("RECEIVED:")
            self._append_log(f"error: {data}")
            self.show_error("Device reported an error")
            return

        if status:
            self._append_log("RECEIVED:")
            if relay is not None:
                self._append_log(f"relay {relay} {status}")
            else:
                self._append_log(status)

        if status == "completed" and relay is not None:
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
        if self._is_finished:
            return
        if time.time() >= self._deadline:
            self._append_log("RECEIVED:")
            self._append_log("timeout waiting for completion")
            self.show_error("Timeout waiting for device")
            return
        self._timeout_id = self.after(500, self._check_timeout)
