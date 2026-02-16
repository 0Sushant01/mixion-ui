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
        
        # Create clickable bar at bottom (doesn't cover video)
        # This bar is LARGE and easy to tap
        self.touch_bar = tk.Frame(self, bg="#000000", cursor="hand2")
        self.touch_bar.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)
        
        # Add instruction text in the bar
        self.instruction_label = tk.Label(
            self.touch_bar,
            text="⬆  TAP HERE TO CONTINUE  ⬆",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#000000",
            cursor="hand2"
        )
        self.instruction_label.pack(expand=True)
        
        # Bind click events to bar and label
        self.touch_bar.bind("<Button-1>", self.on_touch)
        self.instruction_label.bind("<Button-1>", self.on_touch)
        self.bind("<Button-1>", self.on_touch)
        
        # Add keyboard shortcuts
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
            text="Video playback unavailable\n\nInstall MPV and python-mpv",
            font=("Arial", 16),
            fill="white",
            justify="center"
        )
        # Touch bar at bottom is still clickable even without video

    def start(self):
        """Called when screen is shown"""
        # Update canvas size
        self.canvas.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        print(f"Canvas size: {width}x{height}")
        
        # Make sure touch bar is on top and visible
        self.touch_bar.lift()
        
        if not self.player:
            return
        
        try:
            # MPV should already be playing, just ensure it's not paused
            if hasattr(self.player, 'pause'):
                self.player.pause = False
            print("Video playback started/resumed")
            print("Video visible in top 80%, clickable bar at bottom 20%")
            
            # Animate the instruction label to draw attention
            self._animate_label()
        except Exception as e:
            print(f"Error starting playback: {e}")
    
    def _animate_label(self):
        """Pulse animation for instruction label"""
        try:
            current_fg = self.instruction_label.cget("fg")
            # Toggle between white and light gray
            new_fg = "#AAAAAA" if current_fg == "white" else "white"
            self.instruction_label.config(fg=new_fg)
            
            # Repeat animation every 700ms
            self.after(700, self._animate_label)
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
