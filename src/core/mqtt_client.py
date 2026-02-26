"""
MQTT Client for ESP32 Communication
Handles publishing dispense commands to ESP32
"""

import json
import time
import uuid
import paho.mqtt.client as mqtt
from threading import Lock


class MQTTClient:
    """MQTT client for sending commands to ESP32"""
    
    def __init__(self, broker, port, device_id, status_topic=None):
        self.broker = broker
        self.port = port
        self.device_id = device_id
        self.status_topic = status_topic or f"mixion/status/{device_id}"
        self.client = None
        self.connected = False
        self.lock = Lock()
        self.last_alive_at = 0.0
        self.last_status_payload = None
        self.status_listeners = []
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=f"mixion_ui_{uuid.uuid4().hex[:8]}")
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            self.client.connect_async(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            print(f"Connected to MQTT broker at {self.broker}:{self.port}")
            if self.status_topic:
                client.subscribe(self.status_topic, qos=1)
                print(f"Subscribed to status topic: {self.status_topic}")
        else:
            self.connected = False
            print(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        if rc != 0:
            print(f"Unexpected disconnection from MQTT broker: {rc}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        if self.status_topic and msg.topic == self.status_topic:
            payload = msg.payload.decode("utf-8", errors="ignore").strip()
            print(f"Status response received on {msg.topic}: {payload}")
            self.last_status_payload = payload
            data = None
            try:
                data = json.loads(payload)
            except Exception:
                data = None

            if data is not None:
                self._update_last_alive_from_data(data)
                self._notify_status_listeners(data)
            else:
                self._update_last_alive(payload)

    def _update_last_alive(self, payload):
        """Update last alive timestamp if payload indicates device is alive"""
        try:
            if payload:
                lower = payload.lower()
                if lower == "alive" or lower == "online":
                    self.last_alive_at = time.time()
                    return
        except Exception:
            pass

    def _update_last_alive_from_data(self, data):
        try:
            status = str(data.get("status", "")).lower()
            if status in ("alive", "online"):
                self.last_alive_at = time.time()
        except Exception:
            pass

    def _notify_status_listeners(self, data):
        for listener in list(self.status_listeners):
            try:
                listener(data)
            except Exception:
                pass

    def add_status_listener(self, listener):
        if listener not in self.status_listeners:
            self.status_listeners.append(listener)

    def remove_status_listener(self, listener):
        if listener in self.status_listeners:
            self.status_listeners.remove(listener)
    
    def publish_dispense_command(self, jobs):
        """
        Publish dispense command to ESP32
        
        Args:
            jobs: List of dict with 'relay' and 'duration_sec' keys
                  Example: [{"relay": 1, "duration_sec": 5}, {"relay": 2, "duration_sec": 7}]
        
        Returns:
            tuple: (success: bool, msg_id: str or None, payload: dict or None)
        """
        msg_id = str(uuid.uuid4())
        
        payload = {
            "cmd": "dispense_parallel",
            "device_id": self.device_id,
            "jobs": jobs,
            "msg_id": msg_id
        }

        if not self.connected:
            print("Not connected to MQTT broker")
            return False, msg_id, payload
        
        topic = f"mixion/command/{self.device_id}"
        
        try:
            with self.lock:
                result = self.client.publish(topic, json.dumps(payload), qos=1)
                result.wait_for_publish(timeout=5.0)
            
            if not result.is_published():
                print(f"Warning: Dispense command publish timed out or failed.")
                return False, None, payload

            print(f"Published dispense command: {payload}")
            return True, msg_id, payload
            
        except Exception as e:
            print(f"Failed to publish MQTT message: {e}")
            return False, None, payload

    def publish_status_request(self, topic, payload):
        """Publish a status request to ESP32"""
        if not self.connected:
            return False

        try:
            payload_json = json.dumps(payload)
            with self.lock:
                result = self.client.publish(topic, payload_json, qos=1)
                # WARNING: Do NOT use result.wait_for_publish() here!
                # Since this function is called periodically on the main Tkinter thread,
                # if the MQTT broker drops packets, wait_for_publish blocks the UI completely
                # and causes the Raspberry Pi screen to "freeze" or "lag" over time.
            print(f"Status request sent on {topic}: {payload_json}")
            return True
        except Exception as e:
            print(f"Failed to publish status request: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("Disconnected from MQTT broker")
    
    def is_connected(self):
        """Check if connected to broker"""
        return self.connected

    def is_device_online(self, timeout_sec):
        """Check if device reported alive within timeout window"""
        if self.last_alive_at <= 0:
            return False
        return (time.time() - self.last_alive_at) <= timeout_sec

    def get_device_status(self, timeout_sec):
        """Return device status string: connecting, online, or offline"""
        if not self.connected:
            return "connecting"
        if self.last_alive_at <= 0:
            return "connecting"
        if (time.time() - self.last_alive_at) <= timeout_sec:
            return "online"
        return "offline"
