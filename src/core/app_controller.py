import tkinter as tk

from src.screens.menu_screen import MenuScreen
from src.screens.splash_screen import SplashScreen


class MixionApp(tk.Tk):
    def __init__(self, video_path):
        super().__init__()
        self.title("Mixion UI")
        self.configure(bg="black")
        self.attributes("-fullscreen", True)

        self._container = tk.Frame(self, bg="black")
        self._container.pack(fill="both", expand=True)

        self._screens = {
            "splash": SplashScreen(self._container, self, video_path=video_path),
            "menu": MenuScreen(self._container, self),
        }

        for screen in self._screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_screen("splash")

    def show_screen(self, name):
        if name == "menu":
            self._screens["splash"].stop()
        if name == "splash":
            self._screens["splash"].start()
        self._screens[name].tkraise()

    def run(self):
        self.mainloop()
