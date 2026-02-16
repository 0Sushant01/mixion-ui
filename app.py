import os

from src.core.app_controller import MixionApp
from src.core.database import init_database
from src.screens.splash_screen import play_splash_video
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def _resolve_video_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets", "video", "promo.mp4")


if __name__ == "__main__":
    init_database()
    
    # Play splash video BEFORE starting app
    # Video plays fullscreen, exits on click
    video_path = _resolve_video_path()
    play_splash_video(video_path)
    
    # After video exits, start the main app
    app = MixionApp(video_path=video_path)
    app.run()
