import platform
import tkinter as tk
import os

try:
    import mpv
    MPV_AVAILABLE = True
except (ImportError, OSError) as e:
    MPV_AVAILABLE = False
    if isinstance(e, OSError):
        print("Warning: libmpv not found. Install MPV media player on your system.")
        print("  Raspberry Pi/Ubuntu: sudo apt-get install mpv libmpv-dev")
        print("  Then reinstall: pip install python-mpv")
    else:
        print("Warning: python-mpv not installed. Video playback disabled.")


class SplashScreen(tk.Frame):
    def __init__(self, parent, controller, video_path):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.video_path = video_path
        self.player = None
        self.instance = None

        # Create full-screen canvas for video
        self.canvas = tk.Canvas(
            self,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        if MPV_AVAILABLE:
            self._init_mpv()
        else:
            self._show_error_message()
        
        # Create clickable button overlay AFTER video (so it's on top)
        # This button will be visible and always clickable, even over video
        self.skip_button = tk.Button(
            self,
            text="TAP TO CONTINUE ➜",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#333333",
            activebackground="#555555",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.on_touch,
            padx=40,
            pady=15,
            borderwidth=2,
            highlightbackground="white",
            highlightthickness=2
        )
        # Place button at bottom center, on top of everything
        self.skip_button.place(relx=0.5, rely=0.92, anchor="center")
        
        # Also bind click to the frame itself (backup)
        self.bind("<Button-1>", self.on_touch)
        
        # Add keyboard shortcut for testing
        self.bind("<space>", self.on_touch)
        self.bind("<Return>", self.on_touch)

    def _init_mpv(self):
        try:
            # Get absolute path for video
            video_abs_path = os.path.abspath(self.video_path)
            
            if not os.path.exists(video_abs_path):
                print(f"Warning: Video file not found: {video_abs_path}")
                self._show_error_message()
                return
            
            # Wait for canvas to be displayed before embedding
            self.canvas.update_idletasks()
            
            # Get canvas window ID for embedding
            canvas_wid = self.canvas.winfo_id()
            
            print(f"Initializing MPV with canvas wid: {canvas_wid}")
            
            # Create MPV player instance with canvas embedding
            self.player = mpv.MPV(
                wid=str(canvas_wid),
                loop='inf',
                vo='x11' if platform.system() == 'Linux' else 'gpu',
                keep_open='yes',
                input_default_bindings=False,
                input_vo_keyboard=False,
                osc=False,
                quiet=True
            )
            
            # Load and play video
            self.player.play(video_abs_path)
            
            print(f"MPV initialized: {video_abs_path}")
            print("Video should now be playing in background")
            
        except Exception as e:
            print(f"Error initializing MPV: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_message()

    def _show_error_message(self):
        # Clear canvas and show error message
        self.canvas.delete("all")
        self.canvas.create_text(
            400, 300,
            text="Video playback unavailable\n\nInstall MPV and python-mpv\n\nClick button below to continue",
            font=("Arial", 16),
            fill="white",
            justify="center"
        )
        # Button is still clickable even without video

    def start(self):
        """Called when screen is shown"""
        # Update canvas size
        self.canvas.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        print(f"Canvas size: {width}x{height}")
        
        # Make sure button is on top and visible
        self.skip_button.lift()
        
        if not self.player:
            return
        
        try:
            # MPV should already be playing, just ensure it's not paused
            if hasattr(self.player, 'pause'):
                self.player.pause = False
            print("Video playback started/resumed")
            
            # Animate the button to draw attention
            self._animate_button()
        except Exception as e:
            print(f"Error starting playback: {e}")
    
    def _animate_button(self):
        """Pulse animation for skip button"""
        try:
            current_bg = self.skip_button.cget("bg")
            # Toggle between dark gray and slightly lighter gray
            new_bg = "#444444" if current_bg == "#333333" else "#333333"
            self.skip_button.config(bg=new_bg)
            
            # Repeat animation every 600ms
            self.after(600, self._animate_button)
        except:
            pass

    def stop(self):
        if not self.player:
            return
        
        try:
            self.player.terminate()
            print("Video playback stopped")
        except Exception as e:
            print(f"Error stopping playback: {e}")

    def on_touch(self, _event=None):
        """Handle touch/click/keyboard event"""
        print("Splash screen touched - navigating to menu")
        self.stop()
        self.controller.show_screen("menu")
