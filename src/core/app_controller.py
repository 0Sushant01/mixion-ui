import tkinter as tk

import config
from src.core.database import init_database
from src.core.mqtt_client import MQTTClient
from src.core.pour_engine import PourEngine
from src.screens.custom_screen import CustomMixScreen
from src.screens.menu_screen import MenuScreen
from src.screens.processing_screen import ProcessingScreen
from src.screens.bottle_update_screen import BottleUpdateScreen


class MixionApp(tk.Tk):
    def __init__(self, video_path):
        super().__init__()
        self.title("Mixion UI")
        self.configure(bg="black")
        self.attributes("-fullscreen", True)

        self.video_path = video_path

        # Initialize core components
        self.database = init_database()
        self.mqtt_client = MQTTClient(
            broker=config.MQTT_BROKER,
            port=config.MQTT_PORT,
            device_id=config.DEVICE_ID,
            status_topic=config.TOPIC_STATUS
        )
        self.pour_engine = PourEngine(self.database, self.mqtt_client)
        
        # Try to connect to MQTT broker
        if self.mqtt_client.connect():
            print("✓ MQTT client connected")
        else:
            print("⚠ MQTT client not connected - commands will fail")

        self._container = tk.Frame(self, bg="black")
        self._container.pack(fill="both", expand=True)

        self._screens = {
            "menu": MenuScreen(self._container, self),
            "custom": CustomMixScreen(self._container, self),
            "processing": ProcessingScreen(self._container, self),
            "bottle_update": BottleUpdateScreen(self._container, self),
        }

        for screen in self._screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Start directly at menu (splash video was already played)
        self.show_screen("menu")
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def show_screen(self, name):
        screen = self._screens[name]
        if hasattr(screen, "refresh"):
            screen.refresh()
        screen.tkraise()

    def get_screen(self, name):
        return self._screens.get(name)

    def quit(self):
        """Clean shutdown"""
        print("Shutting down...")
        self.mqtt_client.disconnect()
        self.destroy()

    def run(self):
        self.mainloop()
