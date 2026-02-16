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
    
    def __init__(self, broker, port, device_id):
        self.broker = broker
        self.port = port
        self.device_id = device_id
        self.client = None
        self.connected = False
        self.lock = Lock()
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=f"mixion_ui_{uuid.uuid4().hex[:8]}")
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            # Wait a moment for connection
            time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            print(f"Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            self.connected = False
            print(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        if rc != 0:
            print(f"Unexpected disconnection from MQTT broker: {rc}")
    
    def publish_dispense_command(self, jobs):
        """
        Publish dispense command to ESP32
        
        Args:
            jobs: List of dict with 'relay' and 'duration_sec' keys
                  Example: [{"relay": 1, "duration_sec": 5}, {"relay": 2, "duration_sec": 7}]
        
        Returns:
            tuple: (success: bool, msg_id: str or None)
        """
        if not self.connected:
            print("Not connected to MQTT broker")
            return False, None
        
        msg_id = str(uuid.uuid4())
        
        payload = {
            "cmd": "dispense_parallel",
            "device_id": self.device_id,
            "jobs": jobs,
            "msg_id": msg_id
        }
        
        topic = f"mixion/command/{self.device_id}"
        
        try:
            with self.lock:
                result = self.client.publish(topic, json.dumps(payload), qos=1)
                result.wait_for_publish()
            
            print(f"Published dispense command: {payload}")
            return True, msg_id
            
        except Exception as e:
            print(f"Failed to publish MQTT message: {e}")
            return False, None
    
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
