# 🎮 ESP32 Simulator Testing Guide

## Overview

The Mixion system provides **two ways** to test without real hardware:

1. **Testing Mode (`test.py`)** - Single command, everything runs together ⭐ **Recommended**
2. **Manual Mode (`test_esp32.py`)** - Simulator in one terminal, app in another

Both allow you to test the complete Mixion system without physical ESP32 hardware.

---

## ⭐ Method 1: Testing Mode (Easiest)

### Single Command - Everything Runs Together

```powershell
python test.py
```

**What happens:**
- ✅ Virtual ESP32 simulator starts in background
- ✅ Full application launches (UI + backend + database)
- ✅ Both run together - no need for separate terminals
- ✅ Simulator automatically responds to commands

**When to use:**
- Daily development
- Quick testing
- Demos
- When you want simplicity

**Example output:**
```
╔════════════════════════════════════════════════════════════╗
║                 MIXION TESTING MODE                        ║
║                                                            ║
║  Virtual ESP32 + Full Application                         ║
║  No hardware required!                                     ║
╚════════════════════════════════════════════════════════════╝

============================================================
MIXION TESTING MODE
============================================================
Starting virtual ESP32 simulator...
  Device ID:  esp32_1
  Broker:     192.168.1.100:1883
============================================================

[SIM] ✓ Virtual ESP32 connected and ready
[SIM] 🎮 Simulator running in background

============================================================
Starting Mixion Application...
============================================================

Database initialized: database/mixion.db
✓ MQTT client connected
VLC initialized: assets/video/promo.mp4
```

Then when you select a drink:
```
────────────────────────────────────────────────────────────
[SIM] 📨 Command received
[SIM] 🚀 Starting 3 parallel jobs...
[SIM] 🔄 Relay 1: RUNNING for 5.0s
[SIM] 🔄 Relay 2: RUNNING for 3.0s
[SIM] 🔄 Relay 3: RUNNING for 7.0s
[SIM] ✓ Relay 2: COMPLETED
[SIM] ✓ Relay 1: COMPLETED
[SIM] ✓ Relay 3: COMPLETED
[SIM] ✅ All jobs completed
────────────────────────────────────────────────────────────
```

---

## 🔧 Method 2: Manual Mode (Advanced)

### Two Terminals - Separate Control

**Terminal 1: Run the Simulator**

```powershell
python test_esp32.py
```

**Expected output:**
```
============================================================
MIXION ESP32 SIMULATOR
============================================================
Device ID:  esp32_1
Broker:     192.168.1.100:1883
Command:    mixion/command/esp32_1
Status:     mixion/status/esp32_1
============================================================

[SIM] Connecting to broker 192.168.1.100:1883...
[SIM] ✓ Connected successfully
[SIM] ✓ Subscribed to: mixion/command/esp32_1

[SIM] 🎮 Simulator ready and listening for commands...
[SIM] Press Ctrl+C to stop
```

### Terminal 2: Run the Mixion App

```powershell
python app.py
```

Now when you select a drink or custom mix in the UI, the simulator will respond!

---

## 🤔 Which Method Should I Use?

| Feature | `test.py` (Testing Mode) | `test_esp32.py` (Manual) |
|---------|-------------------------|-------------------------|
| **Ease of use** | ⭐⭐⭐⭐⭐ Single command | ⭐⭐⭐ Two terminals |
| **Startup** | One command | Start simulator, then app |
| **Output** | Combined in one window | Separate windows |
| **Control** | Less control | Full control of each |
| **Debugging** | Good for quick tests | Better for debugging |
| **Recommended for** | Daily development | Advanced debugging |

**Recommendation:** Use `test.py` for most testing. Use `test_esp32.py` when you need separate control of simulator and app.

---

## 📊 Simulator Behavior

### When Command Received

The simulator will:

1. **Acknowledge receipt:**
   ```
   [SIM] 📨 Command received
         Topic: mixion/command/esp32_1
         Payload: {
           "cmd": "dispense_parallel",
           "device_id": "esp32_1",
           "jobs": [
             {"relay": 1, "duration_sec": 5.0},
             {"relay": 2, "duration_sec": 3.0}
           ],
           "msg_id": "..."
         }
   ```

2. **Publish status: "received"**

3. **Execute jobs in parallel:**
   ```
   [SIM] 🚀 Starting 2 parallel jobs...
   [SIM] 🔄 Relay 1: RUNNING for 5.0s
   [SIM] 🔄 Relay 2: RUNNING for 3.0s
   [SIM] ✓ Relay 2: COMPLETED
   [SIM] ✓ Relay 1: COMPLETED
   [SIM] ✅ All jobs completed for msg_id: ...
   ```

4. **Publish status updates:**
   - `status: "running"` - for each relay
   - `status: "completed"` - for each relay
   - `status: "all_completed"` - when all done

## 🔄 Complete Test Flow

```
1. Start simulator
   ↓
2. Start app.py
   ↓
3. Navigate through UI:
   • Touch splash screen
   • Select a drink (e.g., "Mojito")
   ↓
4. Backend calculates and sends MQTT command
   ↓
5. Simulator receives command:
   [SIM] 📨 Command received
   [SIM] 🚀 Starting 3 parallel jobs...
   [SIM] 🔄 Relay 1: RUNNING for 5.0s
   [SIM] 🔄 Relay 2: RUNNING for 3.0s
   [SIM] 🔄 Relay 3: RUNNING for 7.0s
   ↓
6. Simulator publishes status updates
   ↓
7. Processing screen shows in UI
   ↓
8. Jobs complete:
   [SIM] ✓ Relay 2: COMPLETED
   [SIM] ✓ Relay 1: COMPLETED
   [SIM] ✓ Relay 3: COMPLETED
   [SIM] ✅ All jobs completed
```

## 🛠️ Testing Scenarios

### Test 1: Predefined Drink

```powershell
# Terminal 1
python test_esp32.py

# Terminal 2
python app.py
```

1. Touch splash → Menu
2. Select "Mojito"
3. Watch simulator execute jobs
4. Processing screen shows in UI

### Test 2: Custom Mix

1. From menu → "Custom Mix"
2. Set amounts on sliders
3. Click "Start Pour"
4. Watch simulator logs

### Test 3: Multiple Drinks

1. Select drink
2. Wait for completion
3. Return to menu
4. Select another drink
5. Verify simulator handles sequential commands

## 📡 MQTT Messages

### Command Format (UI → Simulator)

**Topic:** `mixion/command/esp32_1`

**Payload:**
```json
{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [
    {"relay": 1, "duration_sec": 5.0},
    {"relay": 2, "duration_sec": 3.0}
  ],
  "msg_id": "a1b2c3d4-..."
}
```

### Status Format (Simulator → UI)

**Topic:** `mixion/status/esp32_1`

**Payloads:**

```json
// Acknowledgment
{
  "device_id": "esp32_1",
  "status": "received",
  "msg_id": "...",
  "job_count": 2,
  "timestamp": 1708123456.789
}

// Job running
{
  "device_id": "esp32_1",
  "status": "running",
  "relay": 1,
  "duration_sec": 5.0,
  "msg_id": "...",
  "timestamp": 1708123456.789
}

// Job completed
{
  "device_id": "esp32_1",
  "status": "completed",
  "relay": 1,
  "msg_id": "...",
  "timestamp": 1708123461.789
}

// All jobs done
{
  "device_id": "esp32_1",
  "status": "all_completed",
  "msg_id": "...",
  "timestamp": 1708123461.789
}
```

## 🐛 Troubleshooting

### Simulator Won't Connect

```
[SIM] ✗ Connection failed
```

**Solution:**
1. Check MQTT broker is running: `mosquitto -v`
2. Verify config.py has correct broker IP
3. Test broker: `mosquitto_pub -h <ip> -t test -m hello`

### No Commands Received

**Solution:**
1. Check device_id matches in config.py
2. Verify app.py is using same broker
3. Monitor MQTT: `mosquitto_sub -h <ip> -t "mixion/#" -v`

### Jobs Not Running in Parallel

This is expected behavior! The simulator uses threads to run jobs simultaneously, matching real hardware behavior.

## 🔍 Monitoring MQTT Traffic

### Subscribe to All Topics

```powershell
mosquitto_sub -h 192.168.1.100 -t "mixion/#" -v
```

This shows both command and status messages in real-time.

## ⚙️ Configuration

The simulator uses settings from `config.py`:

```python
MQTT_BROKER = "192.168.1.100"  # Must match app
MQTT_PORT = 1883
DEVICE_ID = "esp32_1"           # Must match app
```

**No changes needed** - simulator automatically reads these values.

## 🎯 What Gets Tested

✅ **Backend Logic**
- ML → seconds conversion
- Recipe calculations
- MQTT command formatting

✅ **MQTT Communication**
- Command publishing
- Status receiving (future enhancement)
- Message format validation

✅ **UI Flow**
- Screen transitions
- Processing screen display
- Error handling

✅ **Parallel Execution**
- Multiple pumps at once
- Thread safety
- Timing accuracy

## 🚀 Advanced Testing

### Test with Multiple Devices

Edit config.py to test different device IDs:

```python
DEVICE_ID = "esp32_2"
```

Run multiple simulators for different devices!

### Custom Test Commands

Send manual commands:

```powershell
mosquitto_pub -h 192.168.1.100 -t "mixion/command/esp32_1" -m '{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [
    {"relay": 1, "duration_sec": 2.0}
  ],
  "msg_id": "manual-test"
}'
```

Watch simulator respond!

## 📋 Simulator Features

✅ **Realistic Behavior**
- Parallel job execution with threads
- Realistic timing (actual sleep for duration)
- Status updates at appropriate times

✅ **Error Handling**
- Invalid JSON detection
- Missing fields validation
- Continues running on errors

✅ **Logging**
- Clear console output
- Unicode icons for visual feedback
- Timestamped status messages

✅ **MQTT Quality**
- QoS 1 for reliable delivery
- Proper connect/disconnect handling
- Auto-reconnect ready

## 🎓 Understanding the Simulation

### Real ESP32 vs Simulator

| Aspect | Real ESP32 | Simulator |
|--------|-----------|-----------|
| GPIO | Controls physical relays | Prints to console |
| Timing | Hardware PWM | Python sleep() |
| Parallel | FreeRTOS tasks | Python threads |
| MQTT | WiFi connection | Same broker |
| Status | Hardware sensors | Simulated status |

### Why This Works

The backend sends **time values** (duration_sec), not hardware commands. The simulator:

1. Receives the same MQTT messages
2. Parses the same JSON format
3. Publishes compatible status updates
4. Simulates the same timing

**Result:** Backend can't tell the difference!

## ✅ Verification Checklist

- [ ] Simulator connects to broker
- [ ] Simulator subscribes to command topic
- [ ] App.py connects to same broker
- [ ] Selecting drink triggers command
- [ ] Simulator receives and parses command
- [ ] Jobs execute in parallel
- [ ] Duration matches calculation
- [ ] Status messages published
- [ ] Processing screen appears in UI
- [ ] Can select multiple drinks sequentially

---

**Happy testing! 🍹**

The simulator lets you develop and test the complete system before hardware is ready!
