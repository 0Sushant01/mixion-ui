# Mixion Drink Machine Software

**Production-ready drink dispensing system** with Tkinter UI, SQLite database, and MQTT communication with ESP32.

## 🎯 Overview

Mixion is a complete software solution for automated drink dispensing machines. It features:

- ✅ **Modern Tkinter UI** - Fullscreen kiosk interface with splash video
- ✅ **Smart Pour Engine** - Automatic ML → seconds conversion using pump flow rates
- ✅ **MQTT Integration** - Real-time communication with ESP32 hardware
- ✅ **SQLite Database** - Robust data management for drinks, recipes, and bottles
- ✅ **Admin Panel** - Easy configuration of drinks, recipes, and limits
- ✅ **Custom Mix Mode** - Let customers create their own drinks
- ✅ **Modular Architecture** - Clean separation of UI, business logic, and data

## 🚀 Quick Start

See **[QUICKSTART.md](QUICKSTART.md)** for step-by-step setup instructions.

### Testing Mode (No Hardware)

```powershell
# Single command - starts simulator + app together
python test.py
```

### Production Mode (Real Hardware)

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure MQTT broker in config.py
# Edit config.py and set your broker IP

# 3. Add sample data
python setup_sample_data.py

# 4. Run with real ESP32
python app.py
```

> **Note:** Database migration happens automatically when you run `app.py`, `test.py`, or `db.py`. No extra commands needed!

## 📁 Project Structure

```
mixion-ui/
│
├── app.py                    # Main entry point
├── config.py                 # MQTT and UI configuration ⚙️
├── requirements.txt          # Python dependencies
│
├── src/
│   ├── core/
│   │   ├── database.py       # SQLite database manager
│   │   ├── mqtt_client.py    # MQTT communication 📡
│   │   ├── pour_engine.py    # ML → Seconds conversion 🧮
│   │   └── app_controller.py # Main app controller
│   │
│   ├── screens/
│   │   ├── splash_screen.py   # Splash video screen
│   │   ├── menu_screen.py     # Drink selection menu
│   │   ├── custom_screen.py   # Custom mix builder
│   │   └── processing_screen.py # Pour progress display
│   │
│   └── admin/                # Admin interface
│       ├── admin_app.py
│       ├── bottles_page.py
│       ├── drinks_page.py
│       ├── recipes_page.py
│       └── limits_page.py
│
├── assets/
│   └── video/
│       └── promo.mp4         # Splash video (add your own)
│
├── database/
│   └── mixion.db             # SQLite database (auto-created)
│
└── docs/
    ├── QUICKSTART.md         # Quick start guide 🚀
    ├── SETUP.md              # Detailed setup documentation
    └── DATABASE_MANAGER_GUIDE.md
```

## 🔄 User Flow

1. **Splash Screen** → Promotional video plays until user touches screen
2. **Menu Screen** → User selects a predefined drink or "Custom Mix"
3. **Custom Screen** (if selected) → User builds custom drink with sliders
4. **Pour Calculation** → System converts ML to seconds based on pump flow rates
5. **MQTT Command** → Command sent to ESP32 with relay timings
6. **Processing Screen** → "Preparing your drink..." animation
7. **Return to Menu** → Ready for next customer

## 🧮 How It Works

### The Critical Business Logic

ESP32 hardware understands **TIME**, not **VOLUME**. The pour engine automatically converts:

```python
duration_seconds = amount_ml / flow_rate
```

**Example:**
- Recipe requires: 50 ml of vodka
- Pump flow rate: 10 ml/second
- **Command sent to ESP32: Run pump for 5 seconds**

### MQTT Command Format

**Topic:** `mixion/command/esp32_1`

**Payload:**
```json
{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [
    {"relay": 1, "duration_sec": 5.0},
    {"relay": 2, "duration_sec": 3.0},
    {"relay": 3, "duration_sec": 7.0}
  ],
  "msg_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

The ESP32 receives this and runs multiple pumps in parallel for the specified durations.

## 🗄️ Database Schema

### bottles
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Bottle name (e.g., "Vodka") |
| position | INTEGER | Relay position (1-8) |
| flow_rate | REAL | ML per second (e.g., 10.0) |
| enabled | INTEGER | Active status (0/1) |

### drinks
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Drink name (e.g., "Mojito") |
| price | INTEGER | Price in cents |
| active | INTEGER | Show in menu (0/1) |

### recipes
| Column | Type | Description |
|--------|------|-------------|
| drink_id | INTEGER | FK to drinks |
| bottle_id | INTEGER | FK to bottles |
| amount_ml | INTEGER | Amount in milliliters |

### custom_limits
| Column | Type | Description |
|--------|------|-------------|
| bottle_id | INTEGER | FK to bottles |
| min_ml | INTEGER | Minimum pour (e.g., 0) |
| max_ml | INTEGER | Maximum pour (e.g., 150) |

## 💻 Requirements

- **Python 3.9+**
- **MPV Media Player** (for video playback)
- **MQTT Broker** (Mosquitto recommended)
- **ESP32** (for hardware control)

### Python Dependencies

```
paho-mqtt>=1.6.1      # MQTT client for ESP32 communication
python-mpv>=1.0.1     # Video playback (requires MPV installed)
```

Installed automatically with: `pip install -r requirements.txt`

> 📖 **For complete framework and technology details**, see [DEPENDENCIES.md](DEPENDENCIES.md)

## ⚙️ Configuration

Edit [config.py](config.py):

```python
# MQTT Configuration
MQTT_BROKER = "192.168.1.100"  # Your broker IP
MQTT_PORT = 1883
DEVICE_ID = "esp32_1"

# UI Configuration
FULLSCREEN = True
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# Video Assets
SPLASH_VIDEO = "assets/video/promo.mp4"
```

## 🔧 Setup & Installation

## 🔧 Setup & Installation

### 1) Create a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) Install MPV media player

⚠️ **Install MPV BEFORE running `pip install -r requirements.txt`**

**Windows:** Download from https://mpv.io/installation/

**Linux (Raspberry Pi/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install mpv libmpv-dev
```

**macOS:**
```bash
brew install mpv
```

### 3) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4) Install and run MQTT broker

**Windows:**
```powershell
# Download Mosquitto from https://mosquitto.org/download/
# Or use Docker:
docker run -d -p 1883:1883 eclipse-mosquitto
```

**Linux:**
```bash
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

### 5) Configure the application

Edit [config.py](config.py) and set your MQTT broker IP address.

### 6) Populate sample data

```bash
python setup_sample_data.py
```

This creates sample drinks, bottles, and recipes for testing.

### 7) Run the application

```bash
python app.py
```

> **Note:** Database is automatically created and migrated on first run. If you have an existing database without the `flow_rate` column, it will be added automatically.

## 🎮 Running the Applications

### Testing Mode (Recommended for Development)

```bash
python test.py
```

**What happens:**
- ✅ Virtual ESP32 simulator starts in background
- ✅ Full application launches (UI + backend + database)
- ✅ Both run together - no need for separate terminals
- ✅ Select drinks in UI, watch simulator respond

**Perfect for:**
- Development without hardware
- Testing new features
- Demos and presentations

### Customer Kiosk (Main App)

```bash
python app.py
```

Fullscreen touch interface for customers to select and order drinks.

### Admin Panel

```bash
python -m src.admin.admin_app
```

or

```bash
python db.py
```

Desktop application for configuring:
- Bottles (name, position, flow rate)
- Drinks (name, price, active status)
- Recipes (ingredient combinations)
- Custom limits (min/max pour amounts)

See [DATABASE_MANAGER_GUIDE.md](docs/DATABASE_MANAGER_GUIDE.md) for details.

### System Tests

```bash
python test_system.py
```

Validates all components are working correctly:
- Database connectivity
- MQTT connection
- Pour engine calculations
- Configuration validation

## 🧪 Testing

### Test Without Hardware (Simulator)

Run the virtual ESP32 simulator to test the complete system without real hardware:

**Terminal 1:**
```bash
python test_esp32.py
```

**Terminal 2:**
```bash
python app.py
```

The simulator responds to MQTT commands exactly like real ESP32 hardware.

See **[TESTING_WITH_SIMULATOR.md](TESTING_WITH_SIMULATOR.md)** for detailed guide.

### Monitor MQTT Messages

```bash
# Subscribe to all Mixion topics
mosquitto_sub -h 192.168.1.100 -t "mixion/#" -v
```

### Send Test Command

```bash
mosquitto_pub -h 192.168.1.100 -t "mixion/command/esp32_1" -m '{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [{"relay": 1, "duration_sec": 2.0}],
  "msg_id": "test-123"
}'
```

### Run Database Tests

```bash
python examples/database_usage.py
```

## 📊 Example: Adding a New Drink

### Using Admin Panel (GUI)

1. Run admin panel: `python db.py`
2. Go to "Drinks" tab → Add new drink
3. Go to "Recipes" tab → Configure ingredients
4. Test in main app

### Using Code

```python
from src.core.database import init_database

db = init_database()

# Add drink
drink_id = db.add_drink("Margarita", price=550, active=1)

# Add recipe
db.set_recipe(drink_id, bottle_id=1, amount_ml=50)  # 50ml tequila
db.set_recipe(drink_id, bottle_id=2, amount_ml=25)  # 25ml triple sec
db.set_recipe(drink_id, bottle_id=3, amount_ml=25)  # 25ml lime juice
```

## 🎨 Customization

### UI Colors

Edit [config.py](config.py):

```python
COLOR_PRIMARY = "#1a1a2e"
COLOR_ACCENT = "#0f3460"
COLOR_HIGHLIGHT = "#e94560"
```

### Splash Video

Replace `assets/video/promo.mp4` with your own video:
- Format: MP4
- Audio: Included
- Resolution: Match your display

### Flow Rate Calibration

Measure actual pump output and update in admin panel:

1. Run pump for 10 seconds
2. Measure ML dispensed
3. Calculate: `flow_rate = ml_dispensed / 10`
4. Update in admin panel or database

## 🐛 Troubleshooting

### MQTT Not Connected

```
⚠ MQTT client not connected - commands will fail
```

**Solution:**
1. Check broker IP in [config.py](config.py)
2. Verify broker is running: `mosquitto -v`
3. Test connectivity: `mosquitto_pub -h <ip> -t test -m hello`

### Video Not Playing

```
Warning: python-mpv not installed
```

**Solution:**
1. Install MPV media player
2. Reinstall: `pip install --upgrade python-mpv`
3. Verify: `python -c "import mpv; print('OK')"`

### Database Locked

**Solution:**
1. Close all applications using the database
2. Delete `database/mixion.db`
3. Run `python app.py` to recreate

### No Drinks Showing

**Solution:**
```bash
python setup_sample_data.py
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[LAUNCH_MODES.md](LAUNCH_MODES.md)** - How to run the system (testing vs production)
- **[SETUP.md](SETUP.md)** - Detailed documentation
- **[TESTING_WITH_SIMULATOR.md](TESTING_WITH_SIMULATOR.md)** - Testing without hardware
- **[DATABASE_MANAGER_GUIDE.md](docs/DATABASE_MANAGER_GUIDE.md)** - Admin panel guide
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - What was built

## 🔐 Production Deployment

### Checklist

- [ ] Calibrate pump flow rates
- [ ] Configure real drink menu
- [ ] Set correct MQTT broker IP
- [ ] Add splash video
- [ ] Enable fullscreen mode
- [ ] Test all drinks thoroughly
- [ ] Configure custom limits
- [ ] Set up auto-start on boot

### Auto-Start on Raspberry Pi

Create `/etc/systemd/system/mixion.service`:

```ini
[Unit]
Description=Mixion Kiosk
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/mixion-ui
ExecStart=/home/pi/mixion-ui/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable mixion
sudo systemctl start mixion
```

## 🚀 Future Enhancements

### Planned Features

- [ ] ESP32 status feedback (real-time progress)
- [ ] Stock tracking and alerts
- [ ] Payment integration
- [ ] Receipt printing
- [ ] Usage analytics
- [ ] Remote monitoring
- [ ] Multi-language support
- [ ] Loyalty program

### Architecture Ready For

✅ Multiple ESP32 devices  
✅ Cloud synchronization  
✅ Payment processing  
✅ Real-time telemetry  
✅ Pour cancellation  
✅ Stock management  

## 🛠️ Development

### Code Structure

```
UI Layer (Tkinter)
    ↓
Business Logic (Pour Engine)
    ↓
Data Layer (Database)
    ↓
Communication (MQTT)
    ↓
Hardware (ESP32)
```

### Key Classes

- **`MixionApp`** - Main application controller
- **`PourEngine`** - Business logic for dispensing
- **`MQTTClient`** - MQTT communication wrapper
- **`Database`** - SQLite database manager
- **Screens** - UI components (splash, menu, custom, processing)

### Extending the System

**Add new screen:**
1. Create screen class in `src/screens/`
2. Register in `app_controller.py`
3. Navigate with `controller.show_screen("name")`

**Add new MQTT command:**
1. Add method to `MQTTClient`
2. Call from `PourEngine` or screen

**Add database table:**
1. Add schema to `database.py::_create_tables()`
2. Add methods for CRUD operations

## 📄 License

Proprietary - Mixion Drink Machine System

---

## 🙋 Support

For issues or questions:
1. Check [QUICKSTART.md](QUICKSTART.md)
2. Run `python test_system.py`
3. Check logs in console output

---

**Built with ❤️ for perfect pours every time 🍹**
