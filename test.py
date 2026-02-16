#!/usr/bin/env python3
"""
Mixion Testing Mode Launcher

Starts the full Mixion application (UI + backend + database)
WITH a virtual ESP32 simulator running in the background.

Usage:
    python test.py

This allows testing the complete system without real hardware.
The simulator runs automatically - no need to start it separately.

When you want to use real ESP32 hardware, run app.py directly instead.
"""

import os
import sys
import json
import time
from threading import Thread, Lock
import paho.mqtt.client as mqtt

# Import configuration
try:
    import config
except ImportError:
    print("ERROR: Could not import config.py")
    print("Make sure config.py exists in the same directory")
    sys.exit(1)


class BackgroundESP32Simulator:
    """
    Virtual ESP32 that runs in background while the main app runs
    """
    
    def __init__(self):
        self.broker = config.MQTT_BROKER
        self.port = config.MQTT_PORT
        self.device_id = config.DEVICE_ID
        
        self.command_topic = f"mixion/command/{self.device_id}"
        self.status_topic = f"mixion/status/{self.device_id}"
        
        self.client = None
        self.connected = False
        self.lock = Lock()
        
    def start(self):
        """Start the simulator in the background"""
        print("\n" + "=" * 60)
        print("MIXION TESTING MODE")
        print("=" * 60)
        print("Starting virtual ESP32 simulator...")
        print(f"  Device ID:  {self.device_id}")
        print(f"  Broker:     {self.broker}:{self.port}")
        print(f"  Command:    {self.command_topic}")
        print(f"  Status:     {self.status_topic}")
        print("=" * 60)
        
        try:
            self.client = mqtt.Client(client_id=f"esp32_sim_{self.device_id}")
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            print("\n[SIM] Connecting to MQTT broker...")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()  # Non-blocking loop
            
            # Wait for connection
            time.sleep(1)
            
            if self.connected:
                print("[SIM] ✓ Virtual ESP32 connected and ready")
                print("[SIM] 🎮 Simulator running in background\n")
                return True
            else:
                print("[SIM] ✗ Failed to connect")
                print("[SIM] ⚠  App will run but commands won't be simulated\n")
                return False
                
        except Exception as e:
            print(f"[SIM] ✗ Connection error: {e}")
            print(f"[SIM] ⚠  App will run but commands won't be simulated\n")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            self.client.subscribe(self.command_topic)
            
            # Publish online status
            self._publish_status({
                "device_id": self.device_id,
                "status": "online",
                "timestamp": time.time()
            })
        else:
            self.connected = False
            print(f"[SIM] ✗ Connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        if rc != 0:
            print(f"[SIM] ⚠ Unexpected disconnection: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(msg.payload.decode())
            
            print("\n" + "─" * 60)
            print(f"[SIM] 📨 Command received")
            print(f"      Payload: {json.dumps(payload, indent=2)}")
            
            # Validate command
            if payload.get("cmd") != "dispense_parallel":
                print(f"[SIM] ⚠ Unknown command: {payload.get('cmd')}")
                return
            
            jobs = payload.get("jobs", [])
            msg_id = payload.get("msg_id", "unknown")
            
            if not jobs:
                print("[SIM] ⚠ No jobs in command")
                return
            
            # Send acknowledgment
            self._publish_status({
                "device_id": self.device_id,
                "status": "received",
                "msg_id": msg_id,
                "job_count": len(jobs),
                "timestamp": time.time()
            })
            
            # Execute jobs in parallel
            self._execute_jobs(jobs, msg_id)
            
        except json.JSONDecodeError as e:
            print(f"[SIM] ✗ Invalid JSON: {e}")
        except Exception as e:
            print(f"[SIM] ✗ Error processing message: {e}")
    
    def _execute_jobs(self, jobs, msg_id):
        """Execute dispense jobs in parallel threads"""
        print(f"[SIM] 🚀 Starting {len(jobs)} parallel jobs...")
        
        threads = []
        for job in jobs:
            thread = Thread(
                target=self._execute_single_job,
                args=(job, msg_id),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all jobs to complete in a separate thread
        completion_thread = Thread(
            target=self._wait_for_completion,
            args=(threads, msg_id),
            daemon=True
        )
        completion_thread.start()
    
    def _execute_single_job(self, job, msg_id):
        """Execute a single relay job"""
        relay = job.get("relay")
        duration_sec = job.get("duration_sec", 0)
        
        if relay is None or duration_sec <= 0:
            print(f"[SIM] ⚠ Invalid job: {job}")
            return
        
        try:
            # Publish running status
            print(f"[SIM] 🔄 Relay {relay}: RUNNING for {duration_sec}s")
            self._publish_status({
                "device_id": self.device_id,
                "status": "running",
                "relay": relay,
                "duration_sec": duration_sec,
                "msg_id": msg_id,
                "timestamp": time.time()
            })
            
            # Simulate pump operation
            time.sleep(duration_sec)
            
            # Publish completed status
            print(f"[SIM] ✓ Relay {relay}: COMPLETED")
            self._publish_status({
                "device_id": self.device_id,
                "status": "completed",
                "relay": relay,
                "msg_id": msg_id,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"[SIM] ✗ Error in relay {relay}: {e}")
    
    def _wait_for_completion(self, threads, msg_id):
        """Wait for all jobs to complete and send final status"""
        for thread in threads:
            thread.join()
        
        print(f"[SIM] ✅ All jobs completed for msg_id: {msg_id}")
        print("─" * 60 + "\n")
        
        # Publish final completion status
        self._publish_status({
            "device_id": self.device_id,
            "status": "all_completed",
            "msg_id": msg_id,
            "timestamp": time.time()
        })
    
    def _publish_status(self, status_data):
        """Publish status to MQTT"""
        try:
            payload = json.dumps(status_data)
            self.client.publish(self.status_topic, payload, qos=1)
        except Exception as e:
            print(f"[SIM] ✗ Failed to publish status: {e}")
    
    def stop(self):
        """Stop the simulator"""
        if self.client:
            self._publish_status({
                "device_id": self.device_id,
                "status": "offline",
                "timestamp": time.time()
            })
            self.client.loop_stop()
            self.client.disconnect()


def start_simulator():
    """Start the virtual ESP32 simulator"""
    simulator = BackgroundESP32Simulator()
    simulator.start()
    return simulator


def start_application():
    """Start the main Mixion application"""
    print("=" * 60)
    print("Starting Mixion Application...")
    print("=" * 60)
    print()
    
    # Import and run the main application
    from src.core.app_controller import MixionApp
    from src.core.database import init_database
    
    def _resolve_video_path():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "assets", "video", "promo.mp4")
    
    # Initialize database
    init_database()
    
    # Create and run the app
    app = MixionApp(video_path=_resolve_video_path())
    app.run()


def main():
    """Main entry point for testing mode"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                 MIXION TESTING MODE                        ║")
    print("║                                                            ║")
    print("║  Virtual ESP32 + Full Application                         ║")
    print("║  No hardware required!                                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Start the simulator in the background
    simulator = start_simulator()
    
    try:
        # Start the main application (this blocks on Tkinter mainloop)
        start_application()
    except KeyboardInterrupt:
        print("\n\n[TEST] Shutting down...")
    finally:
        # Clean up simulator
        if simulator:
            print("[TEST] Stopping simulator...")
            simulator.stop()
        print("[TEST] Goodbye!")


if __name__ == "__main__":
    main()
