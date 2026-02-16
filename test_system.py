"""
System Test Script
Verifies all components of the Mixion system are working correctly
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.core.database import init_database
from src.core.mqtt_client import MQTTClient
from src.core.pour_engine import PourEngine


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"       {message}")


def test_database():
    """Test database initialization and operations"""
    print_header("DATABASE TESTS")
    
    try:
        db = init_database()
        print_result("Database initialization", True, f"Path: {config.DATABASE_PATH}")
    except Exception as e:
        print_result("Database initialization", False, str(e))
        return False
    
    # Test bottle operations
    try:
        bottles = db.get_all_bottles()
        print_result("Get all bottles", True, f"Found {len(bottles)} bottles")
        
        if bottles:
            # Check if flow_rate field exists
            has_flow_rate = 'flow_rate' in bottles[0]
            print_result("Flow rate field exists", has_flow_rate)
            
            if has_flow_rate:
                for bottle in bottles[:3]:  # Show first 3
                    print(f"       • {bottle['name']}: {bottle['flow_rate']} ml/sec (pos {bottle['position']})")
    except Exception as e:
        print_result("Get all bottles", False, str(e))
    
    # Test drink operations
    try:
        drinks = db.get_active_drinks()
        print_result("Get active drinks", True, f"Found {len(drinks)} active drinks")
        
        for drink in drinks[:3]:  # Show first 3
            recipes = db.get_recipes_for_drink(drink['id'])
            print(f"       • {drink['name']}: {len(recipes)} ingredients")
    except Exception as e:
        print_result("Get active drinks", False, str(e))
    
    # Test custom limits
    try:
        limits = db.get_all_limits()
        print_result("Get custom limits", True, f"Found {len(limits)} limits configured")
    except Exception as e:
        print_result("Get custom limits", False, str(e))
    
    return True


def test_mqtt():
    """Test MQTT client connection"""
    print_header("MQTT TESTS")
    
    try:
        mqtt = MQTTClient(
            broker=config.MQTT_BROKER,
            port=config.MQTT_PORT,
            device_id=config.DEVICE_ID
        )
        print_result("MQTT client creation", True, f"Broker: {config.MQTT_BROKER}:{config.MQTT_PORT}")
    except Exception as e:
        print_result("MQTT client creation", False, str(e))
        return False
    
    # Try to connect
    try:
        connected = mqtt.connect()
        print_result("MQTT connection", connected, 
                    "Connected successfully" if connected else "Connection failed - is broker running?")
        
        if connected:
            # Test publishing a dummy command
            test_jobs = [{"relay": 1, "duration_sec": 1.0}]
            success, msg_id = mqtt.publish_dispense_command(test_jobs)
            print_result("MQTT publish test", success, f"Message ID: {msg_id}" if success else "Failed to publish")
            
            mqtt.disconnect()
            print_result("MQTT disconnect", True)
        
        return connected
    except Exception as e:
        print_result("MQTT connection", False, str(e))
        return False


def test_pour_engine():
    """Test pour engine calculations"""
    print_header("POUR ENGINE TESTS")
    
    try:
        db = init_database()
        mqtt = MQTTClient(config.MQTT_BROKER, config.MQTT_PORT, config.DEVICE_ID)
        mqtt.connect()
        
        engine = PourEngine(db, mqtt)
        print_result("Pour engine initialization", True)
    except Exception as e:
        print_result("Pour engine initialization", False, str(e))
        return False
    
    # Test duration calculation
    try:
        test_cases = [
            (50, 10.0, 5.0),   # 50ml at 10ml/sec = 5sec
            (100, 20.0, 5.0),  # 100ml at 20ml/sec = 5sec
            (75, 15.0, 5.0),   # 75ml at 15ml/sec = 5sec
        ]
        
        all_passed = True
        for amount_ml, flow_rate, expected in test_cases:
            result = engine._calculate_duration(amount_ml, flow_rate)
            passed = abs(result - expected) < 0.01
            all_passed = all_passed and passed
            if not passed:
                print(f"       ✗ {amount_ml}ml ÷ {flow_rate}ml/s = {result}s (expected {expected}s)")
        
        print_result("Duration calculations", all_passed, 
                    "All test cases passed" if all_passed else "Some test cases failed")
    except Exception as e:
        print_result("Duration calculations", False, str(e))
    
    # Test drink dispensing (if drinks exist)
    try:
        drinks = db.get_active_drinks()
        if drinks:
            test_drink = drinks[0]
            recipes = db.get_recipes_for_drink(test_drink['id'])
            
            if recipes:
                print(f"\n       Testing dispense calculation for '{test_drink['name']}':")
                
                # Calculate what would be sent
                jobs = []
                for recipe in recipes:
                    duration = engine._calculate_duration(recipe['amount_ml'], recipe['flow_rate'])
                    jobs.append({
                        "relay": recipe['position'],
                        "duration_sec": duration
                    })
                    print(f"       • Relay {recipe['position']}: {recipe['amount_ml']}ml ÷ {recipe['flow_rate']}ml/s = {duration}s")
                
                total_ml = sum(r['amount_ml'] for r in recipes)
                max_duration = max(j['duration_sec'] for j in jobs)
                print(f"       → Total: {total_ml}ml in ~{max_duration:.1f}s (parallel)")
                
                print_result("Dispense calculation", True, f"{len(jobs)} pumps will run")
        else:
            print_result("Dispense calculation", False, "No drinks in database")
    except Exception as e:
        print_result("Dispense calculation", False, str(e))
    
    finally:
        mqtt.disconnect()
    
    return True


def test_configuration():
    """Test configuration values"""
    print_header("CONFIGURATION TESTS")
    
    print_result("MQTT broker configured", bool(config.MQTT_BROKER), config.MQTT_BROKER)
    print_result("MQTT port configured", bool(config.MQTT_PORT), str(config.MQTT_PORT))
    print_result("Device ID configured", bool(config.DEVICE_ID), config.DEVICE_ID)
    print_result("Database path configured", bool(config.DATABASE_PATH), config.DATABASE_PATH)
    
    # Check if database file exists
    db_exists = os.path.exists(config.DATABASE_PATH)
    print_result("Database file exists", db_exists, 
                "Ready to use" if db_exists else "Run app.py to create")
    
    # Check if video file exists
    video_exists = os.path.exists(config.SPLASH_VIDEO)
    print_result("Splash video exists", video_exists,
                config.SPLASH_VIDEO if video_exists else "Add video to assets/video/promo.mp4")
    
    return True


def test_imports():
    """Test that all required modules can be imported"""
    print_header("DEPENDENCY TESTS")
    
    imports = {
        "sqlite3": "SQLite database",
        "tkinter": "GUI framework",
        "paho.mqtt.client": "MQTT communication",
    }
    
    all_good = True
    for module, description in imports.items():
        try:
            __import__(module)
            print_result(description, True, module)
        except ImportError as e:
            print_result(description, False, f"{module} - {str(e)}")
            all_good = False
    
    # VLC is optional
    try:
        import vlc
        print_result("VLC (optional)", True, "Video playback available")
    except ImportError:
        print_result("VLC (optional)", False, "Install VLC and python-vlc for video playback")
    
    return all_good


def print_summary():
    """Print system summary"""
    print_header("SYSTEM SUMMARY")
    
    db = init_database()
    bottles = db.get_all_bottles()
    drinks = db.get_active_drinks()
    
    print(f"""
📊 SYSTEM STATUS:

Database:
  • Bottles: {len(bottles)} configured
  • Drinks: {len(drinks)} active
  • Path: {config.DATABASE_PATH}

MQTT:
  • Broker: {config.MQTT_BROKER}:{config.MQTT_PORT}
  • Device: {config.DEVICE_ID}
  • Command Topic: {config.TOPIC_COMMAND}

UI:
  • Resolution: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}
  • Fullscreen: {config.FULLSCREEN}
  • Video: {config.SPLASH_VIDEO}

💡 NEXT STEPS:
  1. Configure MQTT broker IP in config.py
  2. Add sample data: python setup_sample_data.py
  3. Run application: python app.py
  4. Test with ESP32
""")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                 MIXION SYSTEM TEST                         ║
║              Verifying all components...                   ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Run all tests
    test_imports()
    test_configuration()
    test_database()
    test_mqtt()
    test_pour_engine()
    print_summary()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("\n✓ All core components tested. Check results above.")
    print("\n")
