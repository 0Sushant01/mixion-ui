import os

from src.core.app_controller import MixionApp
from src.core.database import init_database
from src.screens.splash_screen import play_splash_video
import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


def _resolve_video_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets", "video", "promo.mp4")


if __name__ == "__main__":
    import time
    
    video_path = _resolve_video_path()
    
    # 1. Start splash video in background (non-blocking)
    print("Pre-loading app components while video plays...")
    video_data = play_splash_video(video_path, blocking=False)
    
    # 2. Initialize the main app (this takes time: DB, MQTT, Screen building)
    # This now runs WHILE the video is playing
    app = MixionApp(video_path=video_path)
    
    # 3. Wait for video to finish or be dismissed before showing the app
    if video_data:
        process, temp_conf = video_data
        try:
            # Simple poll loop to wait for video dismissal
            while process.poll() is None:
                time.sleep(0.1)
        except KeyboardInterrupt:
            process.terminate()
        finally:
            # Cleanup temp conf file
            if temp_conf and os.path.exists(temp_conf):
                try: os.remove(temp_conf)
                except: pass
    
    # 4. Start the main app loop
    print("Handoff to main UI...")
    app.run()
