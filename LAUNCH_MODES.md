# 🚀 Mixion Launch Modes - Quick Reference

## Overview

The Mixion system has different launch modes for different purposes:

```
┌─────────────────────────────────────────────────────────┐
│  DEVELOPMENT & TESTING     →    python test.py         │
│  (No hardware needed)                                   │
├─────────────────────────────────────────────────────────┤
│  PRODUCTION                →    python app.py          │
│  (With real ESP32)                                      │
├─────────────────────────────────────────────────────────┤
│  ADMIN / CONFIGURATION     →    python db.py           │
│  (Database management)                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎮 Testing Mode: `python test.py`

**Purpose:** Development and testing without hardware

**What it does:**
- ✅ Starts virtual ESP32 simulator in background
- ✅ Launches full application (UI + backend + database)
- ✅ Everything runs in one command

**When to use:**
- ✅ Daily development
- ✅ Testing new features
- ✅ Demos without hardware
- ✅ Learning the system

**Example:**
```powershell
python test.py
```

**Output:**
```
╔════════════════════════════════════════════════════════════╗
║                 MIXION TESTING MODE                        ║
║  Virtual ESP32 + Full Application                         ║
╚════════════════════════════════════════════════════════════╝

[SIM] ✓ Virtual ESP32 connected and ready
[SIM] 🎮 Simulator running in background

Database initialized: database/mixion.db
✓ MQTT client connected
```

Then when you select drinks:
```
[SIM] 📨 Command received
[SIM] 🚀 Starting 3 parallel jobs...
[SIM] 🔄 Relay 1: RUNNING for 5.0s
```

---

## 🏭 Production Mode: `python app.py`

**Purpose:** Running with real ESP32 hardware

**What it does:**
- ✅ Launches full application (UI + backend + database)
- ✅ Connects to real MQTT broker
- ✅ Expects real ESP32 to respond
- ❌ NO simulator

**When to use:**
- ✅ Production deployment
- ✅ Testing with real hardware
- ✅ Final integration testing
- ✅ Customer-facing operation

**Example:**
```powershell
python app.py
```

**Output:**
```
Database initialized: database/mixion.db
✓ MQTT client connected
VLC initialized: assets/video/promo.mp4
```

**Requirements:**
- Real ESP32 connected to MQTT broker
- ESP32 running Mixion firmware
- Correct broker IP in config.py

---

## 🛠️ Admin Mode: `python db.py`

**Purpose:** Database configuration and management

**What it does:**
- ✅ Opens admin GUI interface
- ✅ Manage bottles, drinks, recipes
- ✅ Configure custom limits
- ✅ Database-only (no UI, no MQTT)

**When to use:**
- ✅ Initial setup
- ✅ Adding/editing drinks
- ✅ Changing bottle configuration
- ✅ Setting flow rates
- ✅ Configuring custom mix limits

**Example:**
```powershell
python db.py
```

**Features:**
- Bottles management (name, position, flow_rate, enabled)
- Drinks management (name, price, active status)
- Recipe configuration (ingredients per drink)
- Custom limits (min/max pour amounts)

---

## 🔧 Advanced: Manual Simulator

**Purpose:** Separate simulator and app control

**What it does:**
- Runs simulator in one terminal
- Runs app in another terminal
- Full control of each component

**When to use:**
- Advanced debugging
- Monitoring MQTT traffic
- Testing MQTT communication
- Component isolation

**Example:**

**Terminal 1:**
```powershell
python test_esp32.py
```

**Terminal 2:**
```powershell
python app.py
```

---

## 📊 Comparison Matrix

| Mode | Command | Hardware | Simulator | UI | Admin | Use Case |
|------|---------|----------|-----------|----|----|----------|
| **Testing** | `test.py` | ❌ | ✅ Auto | ✅ | ❌ | Development |
| **Production** | `app.py` | ✅ | ❌ | ✅ | ❌ | Real usage |
| **Admin** | `db.py` | ❌ | ❌ | ❌ | ✅ | Configuration |
| **Manual Sim** | `test_esp32.py` + `app.py` | ❌ | ✅ Manual | ✅ | ❌ | Debugging |

---

## 🎯 Decision Tree

```
Do you have real ESP32 hardware?
├─ YES → python app.py
└─ NO
   ├─ Want to test the full system?
   │  └─ YES → python test.py
   └─ Just want to configure database?
      └─ YES → python db.py
```

---

## 💡 Common Workflows

### Initial Setup
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure broker in config.py
# Edit MQTT_BROKER = "192.168.1.100"

# 3. Add sample data
python setup_sample_data.py

# 4. Open admin to configure
python db.py
```

### Daily Development
```powershell
# Just run testing mode
python test.py
```

### Testing with Hardware
```powershell
# 1. Ensure ESP32 is connected and running
# 2. Run the app
python app.py
```

### Debugging MQTT Issues
```powershell
# Terminal 1: Monitor MQTT
mosquitto_sub -h 192.168.1.100 -t "mixion/#" -v

# Terminal 2: Run simulator
python test_esp32.py

# Terminal 3: Run app
python app.py
```

---

## 🔍 What Happens Behind the Scenes

### `python test.py`
```
1. Import config.py
2. Start BackgroundESP32Simulator
   ├─ Connect to MQTT broker
   ├─ Subscribe to command topic
   ├─ Start MQTT loop (non-blocking)
   └─ Print "[SIM] ready"
3. Import app.py components
4. Initialize database
5. Create MixionApp
6. Run Tkinter mainloop (blocking)
   └─ When user selects drink:
      ├─ Backend sends MQTT command
      ├─ Simulator receives command
      ├─ Simulator executes jobs
      └─ Processing screen shows
```

### `python app.py`
```
1. Import config.py
2. Initialize database
3. Create MixionApp
   ├─ Create MQTTClient (expects real ESP32)
   ├─ Create PourEngine
   └─ Create UI screens
4. Run Tkinter mainloop (blocking)
   └─ When user selects drink:
      ├─ Backend sends MQTT command
      ├─ Real ESP32 receives command
      ├─ Real ESP32 controls hardware
      └─ Processing screen shows
```

**Notice:** The only difference is whether simulator or real ESP32 responds!

---

## 🚀 Quick Commands Reference

```powershell
# Testing (simulator + app)
python test.py

# Production (real ESP32)
python app.py

# Admin panel
python db.py

# Manual simulator only
python test_esp32.py

# Demo simulator
python demo_simulator.py

# System tests
python test_system.py

# Add sample data
python setup_sample_data.py

# Manual migration (usually not needed)
python migrate_database.py
```

---

## 📝 Summary

- **Most common:** `python test.py` for development
- **Production:** `python app.py` with real hardware
- **Configuration:** `python db.py` for setup
- **Debugging:** `test_esp32.py` + `app.py` in separate terminals

---

**Choose the right mode for your needs and start building! 🍹**
