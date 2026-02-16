# Dependencies & Frameworks

Complete overview of all frameworks, libraries, and technologies used in the Mixion Drink Machine Software.

---

## 📋 Table of Contents

1. [Built-in Python Frameworks](#built-in-python-frameworks)
2. [External Libraries](#external-libraries)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Technology Stack Summary](#technology-stack-summary)

---

## 🐍 Built-in Python Frameworks

These are part of Python's standard library and require **no installation**.

### 1. **Tkinter**
- **Version**: Included with Python 3.9+
- **Purpose**: GUI framework for fullscreen kiosk interface
- **Usage in Project**:
  - All UI screens (Splash, Menu, Custom, Processing)
  - Custom widgets and components
  - Event handling and touch screen interaction
  - Fullscreen kiosk mode
- **Files**: `src/screens/*.py`, `src/widgets/*.py`

### 2. **SQLite3**
- **Version**: Included with Python 3.9+
- **Purpose**: Embedded database for data persistence
- **Usage in Project**:
  - Store bottles configuration (name, position, flow_rate, status)
  - Store drink recipes and prices
  - Store custom drink limits
  - Auto-migration support for schema changes
- **Files**: `src/core/database.py`
- **Database Location**: `database/mixion.db`

### 3. **Threading**
- **Version**: Included with Python 3.9+
- **Purpose**: Concurrency for parallel pump execution
- **Usage in Project**:
  - Parallel job execution in ESP32 simulator
  - Background MQTT loop in test mode
  - Daemon threads for non-blocking operations
- **Files**: `test_esp32.py`, `test.py`

### 4. **JSON**
- **Version**: Included with Python 3.9+
- **Purpose**: Data serialization for MQTT messages
- **Usage in Project**:
  - MQTT command payloads
  - Status message parsing
- **Files**: `src/core/mqtt_client.py`, `test_esp32.py`

### 5. **UUID**
- **Version**: Included with Python 3.9+
- **Purpose**: Generate unique message IDs
- **Usage in Project**:
  - Unique `msg_id` for each MQTT command
  - Tracking dispense requests
- **Files**: `src/core/mqtt_client.py`

### 6. **Time**
- **Version**: Included with Python 3.9+
- **Purpose**: Delays and timing for animations
- **Usage in Project**:
  - Simulate dispense duration in test mode
  - Animation timing
  - Status update intervals
- **Files**: `test_esp32.py`, `src/screens/processing_screen.py`

### 7. **Sys**
- **Version**: Included with Python 3.9+
- **Purpose**: System-level operations
- **Usage in Project**:
  - Exit application
  - Path manipulation
- **Files**: Various

---

## 📦 External Libraries

These are in [requirements.txt](requirements.txt) and must be installed.

### 1. **paho-mqtt**
- **Version**: Latest (1.6.1+)
- **Purpose**: MQTT client for ESP32 communication
- **Documentation**: https://pypi.org/project/paho-mqtt/
- **Usage in Project**:
  - Connect to MQTT broker (Mosquitto)
  - Publish dispense commands to `mixion/command/{device_id}`
  - Subscribe to status updates from `mixion/status/{device_id}`
  - Handle connection errors and reconnection
- **Files**: `src/core/mqtt_client.py`, `test_esp32.py`, `test.py`
- **Key Methods**:
  - `Client()` - Create MQTT client instance
  - `connect()` - Connect to broker
  - `publish()` - Send messages
  - `subscribe()` - Listen to topics
  - `loop_start()` - Non-blocking background loop
  - `loop_forever()` - Blocking loop for simulators

**Installation**:
```bash
pip install paho-mqtt
```

### 2. **python-mpv**
- **Version**: Latest (1.0.1+)
- **Purpose**: Video playback for splash screen
- **Documentation**: https://pypi.org/project/python-mpv/
- **Usage in Project**:
  - Play promotional video on splash screen
  - Looping video playback
  - Embedded media player widget
- **Files**: `src/screens/splash_screen.py`
- **Key Methods**:
  - `mpv.MPV()` - Create MPV instance
  - `play()` - Load and play media file
  - `terminate()` - Stop playback
  - `pause` - Pause/resume control

**Installation**:
```bash
pip install python-mpv
```

**System Requirement**: Requires **MPV Media Player** installed on the system.

---

## 🖥️ System Requirements

### Operating System
- **Linux** (Raspberry Pi OS recommended)
- **Windows** (10/11)
- **macOS** (10.14+)

### Python
- **Python 3.9 or higher**
- Check version: `python --version`

### MPV Media Player
Required for video playback (used by python-mpv).

⚠️ **IMPORTANT**: Install MPV **BEFORE** installing python-mpv package!

#### Linux (Debian/Ubuntu/Raspberry Pi):
```bash
sudo apt-get update
sudo apt-get install mpv libmpv-dev
```

#### macOS (Homebrew):
```bash
brew install mpv
```

#### Windows:
Download from: https://mpv.io/installation/

### MQTT Broker
Required for ESP32 communication.

#### Recommended: Mosquitto
**Linux**:
```bash
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

**macOS**:
```bash
brew install mosquitto
brew services start mosquitto
```

**Windows**:
Download from: https://mosquitto.org/download/

### ESP32 Hardware
- **ESP32 Development Board**
- **8-channel relay module** (for pumps)
- **Peristaltic pumps** (8 pumps)
- **MQTT firmware** (custom Arduino sketch)

---

## 📥 Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd mixion-ui
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install MPV System Package (REQUIRED FIRST!)

⚠️ **Install MPV BEFORE running pip install**

**Raspberry Pi / Ubuntu / Debian:**
```bash
sudo apt-get update
sudo apt-get install mpv libmpv-dev
```

**macOS:**
```bash
brew install mpv
```

**Windows:**
Download and install from https://mpv.io/installation/

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `paho-mqtt` - MQTT client library
- `python-mpv` - MPV bindings for Python
See [System Requirements](#system-requirements) above.

### 5. Configure MQTT Broker
Edit [config.py](config.py):
```python
MQTT_BROKER = "192.168.1.100"  # Your broker IP
MQTT_PORT = 1883
DEVICE_ID = "esp32_1"
```

### 6. Run Application
```bash
# Production mode (requires ESP32)
python app.py

# Testing mode (virtual ESP32 simulator)
python test.py
```

---

## 🏗️ Technology Stack Summary

| **Layer** | **Technology** | **Type** | **Purpose** |
|-----------|---------------|----------|-------------|
| **UI Framework** | Tkinter | Built-in | GUI, screens, widgets |
| **Database** | SQLite3 | Built-in | Data persistence, auto-migration |
| **Communication** | paho-mqtt | External | ESP32 MQTT communication |
| **Media Player** | python-mpv | External | Splash screen video playback |
| **Concurrency** | Threading | Built-in | Parallel pump execution |
| **Data Format** | JSON | Built-in | MQTT message serialization |
| **Unique IDs** | UUID | Built-in | Message tracking |
| **Business Logic** | Pure Python | Built-in | Pour engine, calculations |

---

## 🔧 Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                    (Tkinter Screens)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  APP CONTROLLER                             │
│              (Orchestrates Components)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
    ┌─────────┐   ┌──────────┐   ┌─────────┐
    │ Database│   │   Pour   │   │  MQTT   │
    │ (SQLite)│←──│  Engine  │──→│ Client  │
    └─────────┘   └──────────┘   └────┬────┘
                        │              │
                        │              ↓
                        │    ┌──────────────────┐
                        │    │  MQTT Broker     │
                        │    │  (Mosquitto)     │
                        │    └────────┬─────────┘
                        │             │
                        ↓             ↓
                  ┌──────────────────────┐
                  │   ESP32 Hardware     │
                  │  (8 Relay Pumps)     │
                  └──────────────────────┘
```

---

## 📝 Dependency Breakdown

### What Gets Installed from requirements.txt

```
paho-mqtt    → MQTT protocol client
python-mpv   → Python bindings for MPV media player
```

### What Comes with Python

```
tkinter      → GUI framework
sqlite3      → Database engine
threading    → Concurrency primitives
json         → JSON encoding/decoding
uuid         → Unique ID generation
time         → Time/delay functions
sys          → System operations
os           → Operating system interface
pathlib      → Path manipulation
```

### What Needs System Installation

```
MPV Media Player     → Video codec backend
MQTT Broker          → Message broker (Mosquitto)
ESP32 Firmware       → Hardware communication
```

---

## 🔄 Update Dependencies

To update all external packages to their latest versions:

```bash
pip install --upgrade -r requirements.txt
```

To check for outdated packages:

```bash
pip list --outdated
```

---

## 🧪 Testing Dependencies

For development and testing, no additional packages are required. The testing mode uses the same dependencies as production:

```bash
# Run with virtual ESP32 simulator
python test.py
```

The simulator uses:
- `paho-mqtt` - Same MQTT client as production
- `threading` - Parallel job execution
- `json` - Command parsing

---

## 📚 Additional Resources

- **Tkinter**: https://docs.python.org/3/library/tkinter.html
- **SQLite3**: https://docs.python.org/3/library/sqlite3.html
- **paho-mqtt**: https://pypi.org/project/paho-mqtt/
- **python-mpv**: https://pypi.org/project/python-mpv/
- **MQTT Protocol**: https://mqtt.org/
- **Mosquitto Broker**: https://mosquitto.org/

---

## ⚠️ Troubleshooting

### ImportError: No module named 'paho.mqtt'
```bash
pip install paho-mqtt
```

### ImportError: No module named 'mpv'
```bash
pip install python-mpv
# Also ensure MPV Media Player is installed on your system
```

### OSError: Cannot find libmpv

This means the system MPV library is missing.

**Raspberry Pi / Ubuntu:**
```bash
sudo apt-get install mpv libmpv-dev
pip install --upgrade python-mpv
```

**macOS:**
```bash
brew install mpv
pip install --upgrade python-mpv
```

**Windows:**
1. Download MPV from https://mpv.io/installation/
2. Extract to C:\mpv
3. Add C:\mpv to PATH
4. Reinstall: `pip install --upgrade python-mpv`

### Tkinter not available
**Linux**:
```bash
sudo apt-get install python3-tk
```

**macOS**: Tkinter comes with Python, but if missing:
```bash
brew install python-tk
```

### MQTT Connection Failed
- Ensure Mosquitto broker is running
- Check MQTT_BROKER IP in [config.py](config.py)
- Verify firewall allows port 1883
- Test with: `mosquitto_sub -h 192.168.1.100 -t test`

---

## 📄 License

This project uses the following open-source libraries:
- **paho-mqtt**: Eclipse Public License 2.0
- **python-mpv**: LGPL-2.1+
- **Tkinter**: Python Software Foundation License
- **SQLite**: Public Domain

---

*Last Updated: February 16, 2026*
