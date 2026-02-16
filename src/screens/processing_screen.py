"""
Processing Screen
Displays while drink is being prepared
"""

import tkinter as tk


class ProcessingScreen(tk.Frame):
    """Screen shown while drink is being dispensed"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0e27")
        self.controller = controller
        
        # Main content
        content = tk.Frame(self, bg="#0a0e27")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Animated dots will be added to this
        self.message_label = tk.Label(
            content,
            text="Preparing your drink",
            fg="#ffffff",
            bg="#0a0e27",
            font=("Arial", 32, "bold")
        )
        self.message_label.pack(pady=(0, 30))
        
        # Dots for animation
        self.dots_label = tk.Label(
            content,
            text="",
            fg="#3b82f6",
            bg="#0a0e27",
            font=("Arial", 32, "bold")
        )
        self.dots_label.pack()
        
        # Status message (optional)
        self.status_label = tk.Label(
            content,
            text="",
            fg="#9aa4b2",
            bg="#0a0e27",
            font=("Arial", 16)
        )
        self.status_label.pack(pady=(20, 0))
        
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
        self.stop_animation()
        self.message_label.config(text="Your drink is ready!", fg="#22c55e")
        self.dots_label.config(text="✓")
        self.status_label.config(text="Enjoy!")
        self.return_button.pack(pady=(30, 0))
    
    def show_error(self, error_message):
        """Show error state"""
        self.stop_animation()
        self.message_label.config(text="Something went wrong", fg="#ef4444")
        self.dots_label.config(text="✗")
        self.status_label.config(text=error_message)
        self.return_button.pack(pady=(30, 0))
    
    def reset(self):
        """Reset to initial state"""
        self.message_label.config(text="Preparing your drink", fg="#ffffff")
        self.dots_label.config(text="")
        self.status_label.config(text="")
        self.return_button.pack_forget()
        self.dot_count = 0
    
    def _on_return(self):
        """Return to menu"""
        self.controller.show_screen("menu")
    
    def refresh(self):
        """Called when screen is shown"""
        self.reset()
        self.start_animation()
