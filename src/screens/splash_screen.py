import platform
import tkinter as tk
import os
import subprocess
import shutil

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
        self.mpv_process = None
        
        # Check if mpv command-line tool is available
        self.mpv_cli_available = shutil.which("mpv") is not None
        
        # Simple instruction screen
        self.instruction_label = tk.Label(
            self,
            text="TAP SCREEN TO CONTINUE",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="black",
            cursor="hand2"
        )
        self.instruction_label.pack(expand=True)
        
        # Bind click to continue
        self.bind("<Button-1>", self.on_touch)
        self.instruction_label.bind("<Button-1>", self.on_touch)
        self.bind("<space>", self.on_touch)
        self.bind("<Return>", self.on_touch)

    def start(self):
        """Called when screen is shown"""
        print("Splash screen displayed")
        self._animate_label()
        
        # IMPORTANT: Video should be played BEFORE app starts
        # See play_splash_video() function below
    
    def _animate_label(self):
        """Pulse animation for instruction label"""
        try:
            current_fg = self.instruction_label.cget("fg")
            new_fg = "#AAAAAA" if current_fg == "white" else "white"
            self.instruction_label.config(fg=new_fg)
            self.after(700, self._animate_label)
        except:
            pass

    def stop(self):
        """Stop any video playback"""
        if self.mpv_process:
            try:
                self.mpv_process.terminate()
                print("Video playback stopped")
            except:
                pass

    def on_touch(self, _event=None):
        """Handle touch/click/keyboard event"""
        print("Splash screen touched - navigating to menu")
        self.stop()
        self.controller.show_screen("menu")


def play_splash_video(video_path):
    """
    Play splash video in fullscreen using MPV with runtime touch-to-exit.
    This runs BEFORE the tkinter app starts.
    
    Uses runtime MPV configuration (no system files modified):
    - Touch/click anywhere exits the video
    - Behavior applies ONLY to splash playback
    - Other MPV usage remains unaffected
    """
    video_abs_path = os.path.abspath(video_path)
    
    if not os.path.exists(video_abs_path):
        print(f"Video file not found: {video_abs_path}")
        return
    
    # Check if mpv is available
    if not shutil.which("mpv"):
        print("MPV command-line tool not found")
        print("Install with: sudo apt-get install mpv")
        return
    
    print(f"Playing splash video: {video_abs_path}")
    print("Touch anywhere to continue...")
    
    try:
        # Run MPV with runtime input configuration
        # --input-default-bindings=no: Disable all default bindings
        # --input-conf=/dev/null: Ignore any persistent config files
        # --input-cmdlist: Define touch-to-quit for this session ONLY
        subprocess.run([
            "mpv",
            "--fullscreen",
            "--loop=inf",
            "--no-osd-bar",
            "--quiet",
            "--input-default-bindings=no",
            "--input-conf=/dev/null",
            "--input-cmdlist=MOUSE_BTN0 quit",
            video_abs_path
        ])
        print("Video playback finished")
    except Exception as e:
        print(f"Error playing video: {e}")
