import os

from src.core.app_controller import MixionApp


def _resolve_video_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets", "video", "promo.mp4")


if __name__ == "__main__":
    app = MixionApp(video_path=_resolve_video_path())
    app.run()
