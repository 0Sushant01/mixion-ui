import os

from src.core.app_controller import MixionApp
from src.core.database import init_database
from src.screens.splash_screen import play_splash_video
import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


def ensure_setup():
    """Ensure dependencies are installed and database is migrated"""
    print("Checking environment setup...")
    import subprocess
    import sys
    
    # 1. Check/Install dependencies
    try:
        import customtkinter
        import paho.mqtt
        import mpv
    except ImportError:
        print("Missing dependencies. Installing from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ Dependencies installed successfully")
        except Exception as e:
            print(f"⚠ Failed to install dependencies: {e}")

    # 2. Initialize/Migrate Database
    try:
        from src.core.database import init_database
        init_database()
        print("✓ Database initialized and migrated")
    except Exception as e:
        print(f"⚠ Database initialization failed: {e}")


def _resolve_video_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets", "video", "promo.mp4")


if __name__ == "__main__":
    import time
    ensure_setup()
    
    video_path = _resolve_video_path()
    
    # 1. Start splash video in background (non-blocking)
    print("Pre-loading app components while video plays...")
    video_data = play_splash_video(video_path, blocking=False)
    
    # 2. Initialize the main app (this takes time: DB, MQTT, Screen building)
    # This now runs WHILE the video is playing
    app = MixionApp(video_path=video_path)
    
    # 3. Auto-terminate splash video before showing the app so it doesn't freeze the Pi
    if video_data:
        process, temp_conf = video_data
        try:
            # The app has finished loading its UI components, so we can forcefully close the video
            process.terminate()
        except Exception as e:
            print(f"Error terminating splash: {e}")
        finally:
            # Cleanup temp conf file
            if temp_conf and os.path.exists(temp_conf):
                try: os.remove(temp_conf)
                except: pass
    
    # 4. Start the main app loop
    print("Handoff to main UI...")
    app.run()
