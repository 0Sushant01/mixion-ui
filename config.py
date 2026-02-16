"""
Mixion Configuration
MQTT and application settings
"""

# MQTT Configuration
MQTT_BROKER = "192.168.1.100"  # Update with your broker IP
MQTT_PORT = 1883
DEVICE_ID = "esp32_1"

# MQTT Topics
TOPIC_COMMAND = f"mixion/command/{DEVICE_ID}"
TOPIC_STATUS = f"mixion/status/{DEVICE_ID}"

# Device status
DEVICE_STATUS_TIMEOUT_SEC = 6

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
