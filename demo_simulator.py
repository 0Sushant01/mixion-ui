"""
Quick Demo Script for ESP32 Simulator

This script demonstrates the simulator by sending a test command.
You can use this to verify MQTT connectivity without running the full UI.

Usage:
    Terminal 1: python test_esp32.py
    Terminal 2: python demo_simulator.py
"""

import json
import time
import paho.mqtt.client as mqtt
import config


def send_test_command():
    """Send a test dispense command to the simulator"""
    
    print("=" * 60)
    print("MIXION SIMULATOR DEMO")
    print("=" * 60)
    print(f"Broker: {config.MQTT_BROKER}:{config.MQTT_PORT}")
    print(f"Device: {config.DEVICE_ID}")
    print("=" * 60)
    
    # Create test command
    test_command = {
        "cmd": "dispense_parallel",
        "device_id": config.DEVICE_ID,
        "jobs": [
            {"relay": 1, "duration_sec": 3.0},
            {"relay": 2, "duration_sec": 5.0},
            {"relay": 3, "duration_sec": 2.0}
        ],
        "msg_id": "demo-test-123"
    }
    
    print("\nTest Command:")
    print(json.dumps(test_command, indent=2))
    print()
    
    # Connect to MQTT
    print("Connecting to MQTT broker...")
    client = mqtt.Client(client_id="mixion_demo")
    
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
        client.loop_start()
        time.sleep(1)
        
        print("✓ Connected\n")
        
        # Publish command
        topic = f"mixion/command/{config.DEVICE_ID}"
        payload = json.dumps(test_command)
        
        print(f"Publishing to: {topic}")
        result = client.publish(topic, payload, qos=1)
        result.wait_for_publish()
        
        print("✓ Command sent!\n")
        print("Check the simulator terminal for output.")
        print("\nExpected simulator output:")
        print("  [SIM] 📨 Command received")
        print("  [SIM] 🚀 Starting 3 parallel jobs...")
        print("  [SIM] 🔄 Relay 1: RUNNING for 3.0s")
        print("  [SIM] 🔄 Relay 2: RUNNING for 5.0s")
        print("  [SIM] 🔄 Relay 3: RUNNING for 2.0s")
        print("  [SIM] ✓ Relay 3: COMPLETED")
        print("  [SIM] ✓ Relay 1: COMPLETED")
        print("  [SIM] ✓ Relay 2: COMPLETED")
        print("  [SIM] ✅ All jobs completed")
        print()
        
        # Wait a bit for delivery
        time.sleep(1)
        
        # Disconnect
        client.loop_stop()
        client.disconnect()
        
        print("=" * 60)
        print("Demo complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure:")
        print("  1. MQTT broker is running")
        print("  2. config.py has correct broker IP")
        print("  3. Simulator is running (python test_esp32.py)")


if __name__ == "__main__":
    send_test_command()
