# Mixion Drink Machine Software

Production-ready drink dispensing system with Tkinter UI, SQLite database, and MQTT communication with ESP32.

## 🏗️ Architecture

```
User Interface (Tkinter)
       ↓
Pour Engine (Business Logic)
       ↓
MQTT Client → ESP32 Hardware
       ↓
Database (SQLite)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MQTT Broker

Edit [config.py](config.py) and set your MQTT broker IP:

```python
MQTT_BROKER = "192.168.1.100"  # Your broker IP
MQTT_PORT = 1883
DEVICE_ID = "esp32_1"
```

### 3. Run Application

```bash
python app.py
```

The database will be **created automatically** on first run.

> **✨ Auto-Migration:** Schema changes (like adding the `flow_rate` column) are applied automatically when you run `app.py` or `db.py`. No manual migration commands needed!

## 📁 Project Structure

```
mixion-ui/
│
├── app.py                    # Main entry point
├── config.py                 # MQTT and app configuration
├── requirements.txt          # Python dependencies
│
├── src/
│   ├── core/
│   │   ├── database.py       # SQLite database manager
│   │   ├── mqtt_client.py    # MQTT communication
│   │   ├── pour_engine.py    # ML → Seconds conversion
│   │   └── app_controller.py # Main application controller
│   │
│   └── screens/
│       ├── splash_screen.py   # Splash video screen
│       ├── menu_screen.py     # Drink selection menu
│       ├── custom_screen.py   # Custom mix builder
│       └── processing_screen.py # Pour progress screen
│
├── assets/
│   └── video/
│       └── promo.mp4         # Splash video (add your own)
│
└── database/
    └── mixion.db             # SQLite database (auto-created)
```

## 🔄 User Flow

1. **Splash Screen** → Video plays until user touches screen
2. **Menu Screen** → User selects predefined drink or custom mix
3. **Custom Screen** (optional) → User builds custom drink
4. **Processing Screen** → Drink is being dispensed
5. **Return to Menu** → Ready for next customer

## 🗄️ Database Schema

### bottles
- `id` - Primary key
- `name` - Bottle name
- `position` - Relay position (1-8)
- `flow_rate` - ML per second (default: 10.0)
- `enabled` - Active status (0/1)

### drinks
- `id` - Primary key
- `name` - Drink name
- `price` - Price in cents
- `active` - Visible in menu (0/1)

### recipes
- `drink_id` - Foreign key to drinks
- `bottle_id` - Foreign key to bottles
- `amount_ml` - Amount in milliliters

### custom_limits
- `bottle_id` - Foreign key to bottles
- `min_ml` - Minimum pour amount
- `max_ml` - Maximum pour amount

## ⚙️ Business Logic

### ML → Seconds Conversion

The ESP32 understands **time**, not **volume**. The pour engine automatically converts:

```python
duration_sec = amount_ml / flow_rate
```

**Example:**
- Amount needed: 50 ml
- Flow rate: 10 ml/sec
- Duration sent to ESP32: **5 seconds**

### MQTT Command Format

**Topic:** `mixion/command/{device_id}`

**Payload:**
```json
{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [
    {"relay": 1, "duration_sec": 5.0},
    {"relay": 2, "duration_sec": 7.5}
  ],
  "msg_id": "unique-uuid"
}
```

## 🔧 Configuration

### Adding Bottles

Use the admin interface or directly in database:

```sql
INSERT INTO bottles (name, position, flow_rate, enabled) 
VALUES ('Vodka', 1, 12.0, 1);
```

### Adding Drinks

```sql
-- Add drink
INSERT INTO drinks (name, price, active) 
VALUES ('Mojito', 500, 1);

-- Add recipe (assuming drink_id=1, bottle_ids 1,2,3)
INSERT INTO recipes (drink_id, bottle_id, amount_ml) VALUES 
  (1, 1, 50),  -- 50ml from bottle 1
  (1, 2, 25),  -- 25ml from bottle 2
  (1, 3, 75);  -- 75ml from bottle 3
```

### Setting Custom Limits

```sql
UPDATE custom_limits 
SET min_ml = 10, max_ml = 100 
WHERE bottle_id = 1;
```

## 🎨 UI Customization

Edit [config.py](config.py) to customize:

```python
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FULLSCREEN = True

COLOR_PRIMARY = "#1a1a2e"
COLOR_ACCENT = "#0f3460"
COLOR_HIGHLIGHT = "#e94560"
```

## 🧪 Testing Without Hardware

You can test the complete system using the **ESP32 simulator** without any physical hardware.

### Start the Simulator

**Terminal 1:**
```bash
python test_esp32.py
```

This creates a virtual ESP32 that responds to MQTT commands.

### Start the Application

**Terminal 2:**
```bash
python app.py
```

Now when you select drinks in the UI, the simulator will:
- Receive MQTT commands
- Execute jobs in parallel
- Publish status updates
- Print realistic console output

**Example output:**
```
[SIM] 📨 Command received
[SIM] 🚀 Starting 3 parallel jobs...
[SIM] 🔄 Relay 1: RUNNING for 5.0s
[SIM] 🔄 Relay 2: RUNNING for 3.0s
[SIM] 🔄 Relay 3: RUNNING for 7.0s
[SIM] ✓ Relay 2: COMPLETED
[SIM] ✓ Relay 1: COMPLETED
[SIM] ✓ Relay 3: COMPLETED
[SIM] ✅ All jobs completed
```

See **[TESTING_WITH_SIMULATOR.md](TESTING_WITH_SIMULATOR.md)** for detailed testing guide.

## 🐛 Troubleshooting

### MQTT Connection Failed
- Check broker IP in [config.py](config.py)
- Ensure broker is running: `mosquitto -v`
- Test connection: `mosquitto_pub -h <broker_ip> -t test -m "hello"`

### Video Not Playing
- Install VLC media player
- Install python-vlc: `pip install python-vlc`
- Check video path in [config.py](config.py)

### Database Errors
- Database schema migrates automatically when running `app.py` or `db.py`
- Delete `database/mixion.db` to recreate from scratch if needed
- Check file permissions
- Run [examples/database_usage.py](examples/database_usage.py) for testing
- Optional: Run `python migrate_database.py` for manual migration (usually not needed)

## 📊 System Status

The application prints status information:

```
Database initialized: database/mixion.db
✓ MQTT client connected
VLC initialized: assets/video/promo.mp4
Selected drink: Mojito (ID: 1)
Published dispense command: {...}
```

## 🔐 Production Considerations

### Current Implementation
- ✅ Modular architecture
- ✅ Separation of concerns
- ✅ Error handling
- ✅ Database transactions
- ✅ MQTT reliability (QoS 1)

### Not Yet Implemented
- ❌ Payment processing
- ❌ Stock tracking
- ❌ ESP32 status feedback
- ❌ Pour cancellation
- ❌ User authentication

## 🚀 Future Enhancements

1. **ESP32 Feedback**
   - Subscribe to `mixion/status/{device_id}`
   - Update processing screen with real-time progress

2. **Stock Management**
   - Track bottle levels
   - Alert when low
   - Disable out-of-stock ingredients

3. **Payment Integration**
   - Card reader support
   - QR code payments
   - Receipt printing

4. **Analytics**
   - Sales tracking
   - Popular drinks
   - Usage patterns

## 📝 Development

### Running Tests
```bash
python examples/database_usage.py
```

### Database Admin
The admin interface is already available in `src/admin/admin_app.py`:

```bash
python -m src.admin.admin_app
```

## 📄 License

Proprietary - Mixion Drink Machine System

---

**Built with ❤️ for perfect pours every time**
