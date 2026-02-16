import json
import threading
import time
import tkinter as tk

import paho.mqtt.client as mqtt

BROKER = "192.168.0.67"
PORT = 1883
DEVICE_ID = "esp32_1"
TOPIC_STATUS = f"mixion/status/{DEVICE_ID}"
TIMEOUT_SEC = 6
RECONNECT_DELAY_SEC = 2

STATUS_CONNECTING = "CONNECTING"
STATUS_ONLINE = "ONLINE"
STATUS_OFFLINE = "OFFLINE"

COLOR_CONNECTING = "#f59e0b"
COLOR_ONLINE = "#22c55e"
COLOR_OFFLINE = "#ef4444"
BG_DARK = "#0b0f14"


class DeviceMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mixion Device Monitor")
        self.geometry("420x240")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        self.last_seen = 0.0
        self.connected = False
        self.status = STATUS_CONNECTING

        self.label = tk.Label(
            self,
            text="CONNECTING...",
            font=("Arial", 28, "bold"),
            fg=COLOR_CONNECTING,
            bg=BG_DARK,
        )
        self.label.pack(expand=True)

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        threading.Thread(target=self._mqtt_loop, daemon=True).start()
        self._update_status_loop()

    def _mqtt_loop(self):
        while True:
            try:
                self.client.connect(BROKER, PORT, keepalive=60)
                self.client.loop_forever()
            except Exception as exc:
                print(f"MQTT connection error: {exc}")
            time.sleep(RECONNECT_DELAY_SEC)

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.connected = True
            print("Connected to broker")
            client.subscribe(TOPIC_STATUS, qos=1)
        else:
            self.connected = False
            print(f"Connection failed: {reason_code}")

    def _on_disconnect(self, client, userdata, reason_code, properties=None):
        self.connected = False
        print(f"Disconnected: {reason_code}")

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            if str(data.get("status", "")).lower() == "alive":
                self.last_seen = time.time()
        except Exception:
            pass

    def _update_status_loop(self):
        now = time.time()
        if self.last_seen <= 0:
            self._set_status(STATUS_CONNECTING)
        elif now - self.last_seen <= TIMEOUT_SEC:
            self._set_status(STATUS_ONLINE)
        else:
            self._set_status(STATUS_OFFLINE)

        self.after(1000, self._update_status_loop)

    def _set_status(self, status):
        if self.status == status:
            return

        self.status = status
        if status == STATUS_ONLINE:
            color = COLOR_ONLINE
        elif status == STATUS_OFFLINE:
            color = COLOR_OFFLINE
        else:
            color = COLOR_CONNECTING

        self.label.config(text=f"{status}...", fg=color)
        self.configure(bg=BG_DARK)
        self.label.configure(bg=BG_DARK)


if __name__ == "__main__":
    app = DeviceMonitorApp()
    app.mainloop()
