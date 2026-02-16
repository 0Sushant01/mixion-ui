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

        # Create full-screen clickable canvas overlay
        self.canvas = tk.Canvas(
            self,
            bg="black",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Add tap instruction text
        self.tap_text = self.canvas.create_text(
            400, 450,  # Will be repositioned in start()
            text="⬆ TAP ANYWHERE TO CONTINUE ⬆",
            font=("Arial", 18, "bold"),
            fill="white"
        )
        
        # Bind click events to entire canvas (makes whole screen clickable)
        self.canvas.bind("<Button-1>", self.on_touch)
        self.bind("<Button-1>", self.on_touch)

        if MPV_AVAILABLE:
            self._init_mpv()
        else:
            self._show_error_message()

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
            400, 300,  # Will be repositioned in start()
            text="Video playback unavailable\n\nInstall MPV and python-mpv\n\nTap to continue",
            font=("Arial", 16),
            fill="white",
            justify="center"
        )

    def start(self):
        """Called when screen is shown"""
        # Update canvas and reposition text to center
        self.canvas.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        print(f"Canvas size: {width}x{height}")
        
        # Reposition tap text to bottom center
        if hasattr(self, 'tap_text'):
            self.canvas.coords(self.tap_text, width // 2, height - 50)
        
        if not self.player:
            return
        
        try:
            # MPV should already be playing, just ensure it's not paused
            if hasattr(self.player, 'pause'):
                self.player.pause = False
            print("Video playback started/resumed")
            
            # Start text animation
            self._animate_tap_label()
        except Exception as e:
            print(f"Error starting playback: {e}")
    
    def _animate_tap_label(self):
        """Pulse animation for tap label"""
        try:
            # Toggle between white and gray
            current_color = self.canvas.itemcget(self.tap_text, "fill")
            new_color = "#CCCCCC" if current_color == "white" else "white"
            self.canvas.itemconfig(self.tap_text, fill=new_color)
            
            # Repeat animation every 500ms
            self.after(500, self._animate_tap_label)
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
        print("Splash screen touched - navigating to menu")
        self.stop()
        self.controller.show_screen("menu")
