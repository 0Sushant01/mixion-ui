"""
Mixion Configuration
MQTT and application settings
"""

# MQTT Configuration
MQTT_BROKER = "192.168.0.67"  # Update with your broker IP
MQTT_PORT = 1883
DEVICE_ID = "esp32_1"

# MQTT Topics
TOPIC_COMMAND = f"mixion/command/{DEVICE_ID}"
TOPIC_STATUS = f"mixion/status/{DEVICE_ID}"

# Device status
DEVICE_STATUS_TIMEOUT_SEC = 6
STATUS_REQUEST_TOPIC = f"mixion/status/{DEVICE_ID}/get"
STATUS_REQUEST_INTERVAL_SEC = 2
STATUS_REQUEST_PAYLOAD = {"cmd": "status"}

# Dispense workflow
DISPENSE_TIMEOUT_SEC = 30

# Database Configuration
DATABASE_PATH = "database/mixion.db"

# UI Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FULLSCREEN = True

# Video Assets
SPLASH_VIDEO = "assets/video/promo.mp4"

# UI Colors (Modern Theme)
COLOR_PRIMARY = "#1a1a2e"
COLOR_SECONDARY = "#16213e"
COLOR_ACCENT = "#0f3460"
COLOR_HIGHLIGHT = "#e94560"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_SECONDARY = "#a0a0a0"

# Paths
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DRINK_IMAGES_DIR = os.path.join(ASSETS_DIR, "drinks")
