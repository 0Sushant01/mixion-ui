import platform
import tkinter as tk

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("Warning: python-vlc not installed. Video playback disabled.")


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

        if VLC_AVAILABLE:
            self._init_vlc()
        else:
            self._show_error_message()

    def _init_vlc(self):
        try:
            self.instance = vlc.Instance('--no-xlib --avcodec-hw=none --no-hw-decoding')
            self.player = self.instance.media_player_new()
            
            media = self.instance.media_new(self.video_path)
            media.add_option('input-repeat=65535')
            
            self.player.set_media(media)
            self.player.audio_set_volume(100)
            
            print(f"VLC initialized: {self.video_path}")
        except Exception as e:
            print(f"Error initializing VLC: {e}")
            self._show_error_message()

    def _show_error_message(self):
        label = tk.Label(
            self.video_frame,
            text="Video playback unavailable\n\nInstall VLC and python-vlc\n\nTap to continue",
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
            if platform.system() == "Windows":
                self.player.set_hwnd(self.video_frame.winfo_id())
            elif platform.system() == "Linux":
                self.player.set_xwindow(self.video_frame.winfo_id())
            elif platform.system() == "Darwin":
                self.player.set_nsobject(self.video_frame.winfo_id())
            
            self.player.play()
            print("Video playback started")
        except Exception as e:
            print(f"Error starting playback: {e}")

    def stop(self):
        if not self.player:
            return
        
        try:
            self.player.stop()
            print("Video playback stopped")
        except Exception as e:
            print(f"Error stopping playback: {e}")

    def on_touch(self, _event=None):
        self.controller.show_screen("menu")
