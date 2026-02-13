import tkinter as tk

import cv2
from PIL import Image, ImageTk

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False


class SplashScreen(tk.Frame):
    def __init__(self, parent, controller, video_path):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.video_path = video_path
        self.cap = None
        self.vlc_player = None
        self.vlc_instance = None
        self.running = False
        self.after_id = None
        self.frame_delay_ms = 33
        
        self._init_vlc_audio()

        self.label = tk.Label(self, bg="black")
        self.label.pack(fill="both", expand=True)

        self.label.bind("<Button-1>", self.on_touch)
        self.bind("<Button-1>", self.on_touch)

    def _init_vlc_audio(self):
        if not VLC_AVAILABLE:
            print("Warning: python-vlc not available, audio playback disabled")
            return
        try:
            self.vlc_instance = vlc.Instance('--no-xlib')
            self.vlc_player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(self.video_path)
            self.vlc_player.set_media(media)
            self.vlc_player.audio_set_volume(100)
            print("VLC audio initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize VLC audio: {e}")
            self.vlc_player = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.cap = cv2.VideoCapture(self.video_path)
        self._set_frame_delay()
        self._start_audio()
        self._update_frame()

    def _start_audio(self):
        if self.vlc_player is None:
            return
        try:
            self.vlc_player.play()
        except Exception as e:
            print(f"Warning: Could not start audio playback: {e}")

    def stop(self):
        self.running = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self._stop_audio()
        self.label.configure(image="")
        self.label.image = None

    def _stop_audio(self):
        if self.vlc_player is None:
            return
        try:
            self.vlc_player.stop()
        except Exception:
            pass

    def on_touch(self, _event=None):
        self.controller.show_screen("menu")

    def _set_frame_delay(self):
        if self.cap is None:
            return
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps and fps > 0:
            self.frame_delay_ms = max(15, int(1000 / fps))

    def _update_frame(self):
        if not self.running or self.cap is None:
            return

        success, frame = self.cap.read()
        if not success:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if self.vlc_player:
                try:
                    self.vlc_player.stop()
                    self.vlc_player.play()
                except Exception:
                    pass
            success, frame = self.cap.read()

        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            frame = cv2.resize(frame, (screen_w, screen_h), interpolation=cv2.INTER_AREA)
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image)
            self.label.configure(image=photo)
            self.label.image = photo

        self.after_id = self.after(self.frame_delay_ms, self._update_frame)
