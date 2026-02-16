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

        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(fill="both", expand=True)

        self.video_frame.bind("<Button-1>", self.on_touch)
        self.bind("<Button-1>", self.on_touch)

        if MPV_AVAILABLE:
            self._init_mpv()
        else:
            self._show_error_message()

    def _init_mpv(self):
        try:
            # Get absolute path for video
            video_abs_path = os.path.abspath(self.video_path)
            
            # Create MPV player instance
            self.player = mpv.MPV(
                wid=str(self.video_frame.winfo_id()),
                loop='inf',
                vo='x11' if platform.system() == 'Linux' else 'gpu',
                keep_open='yes',
                input_default_bindings=False,
                input_vo_keyboard=False,
                osc=False
            )
            
            # Load video
            self.player.play(video_abs_path)
            
            print(f"MPV initialized: {self.video_path}")
        except Exception as e:
            print(f"Error initializing MPV: {e}")
            self._show_error_message()

    def _show_error_message(self):
        label = tk.Label(
            self.video_frame,
            text="Video playback unavailable\n\nInstall MPV and python-mpv\n\nTap to continue",
            fg="white",
            bg="black",
            font=("Arial", 16),
        )
        label.pack(expand=True)

    def start(self):
        if not self.player:
            return

        self.video_frame.update()
        
        try:
            # MPV starts playback automatically when initialized
            # Just ensure it's playing
            if hasattr(self.player, 'pause'):
                self.player.pause = False
            print("Video playback started")
        except Exception as e:
            print(f"Error starting playback: {e}")

    def stop(self):
        if not self.player:
            return
        
        try:
            self.player.terminate()
            print("Video playback stopped")
        except Exception as e:
            print(f"Error stopping playback: {e}")

    def on_touch(self, _event=None):
        self.controller.show_screen("menu")
