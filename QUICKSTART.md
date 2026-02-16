# 🚀 Mixion Quick Start Guide

## Step-by-Step Setup

### 1️⃣ Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `paho-mqtt` - MQTT communication with ESP32
- `python-vlc` - Video playback for splash screen

### 2️⃣ Install VLC Media Player

Download and install VLC: https://www.videolan.org/vlc/

Required for video playback on splash screen.

### 3️⃣ Configure MQTT Broker

Edit `config.py` and set your MQTT broker IP address:

```python
MQTT_BROKER = "192.168.1.100"  # ← Change this to your broker IP
```

**Testing MQTT Connection:**

```powershell
# Subscribe to status (in one terminal)
mosquitto_sub -h 192.168.1.100 -t "mixion/#" -v

# Publish test (in another terminal)
mosquitto_pub -h 192.168.1.100 -t "mixion/command/esp32_1" -m "test"
```

### 4️⃣ Add Sample Data

```powershell
python setup_sample_data.py
```

This will:
- Create 6 bottles with 10 ml/sec flow rate
- Add 5 sample drinks (Mojito, Margarita, etc.)
- Configure recipes for each drink
- Set custom mix limits (0-150ml)

### 5️⃣ Run the Application

**Testing Mode (Easiest - No Hardware):**
```powershell
python test.py
```

This single command starts:
- ✅ Virtual ESP32 simulator
- ✅ Full Mixion application
- ✅ Everything runs together!

**Production Mode (Real ESP32):**
```powershell
python app.py
```

**Expected output (testing mode):**
```
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

> **✨ Auto-Migration:** The database is automatically created and migrated on first run. If upgrading from an older version, the `flow_rate` column will be added automatically - no manual migration needed!

## 🎯 Testing the Flow

### Option 1: Testing Mode (Easiest - Single Command)

**Just run:**
```powershell
python test.py
```

That's it! Everything starts automatically:
- Virtual ESP32 simulator runs in background
- Full application launches
- Select drinks and watch the simulator respond!

See [TESTING_WITH_SIMULATOR.md](TESTING_WITH_SIMULATOR.md) for details.

### Option 2: Manual Simulator (Two Terminals)

**Terminal 1 - Start Simulator:**
```powershell
python test_esp32.py
```

**Terminal 2 - Start App:**
```powershell
python app.py
```

The simulator acts as a virtual ESP32 and responds to commands!

### Option 3: Real ESP32 Hardware

**Just run:**
```powershell
python app.py
```

Make sure your ESP32 is connected and running the firmware.

### Test 1: Predefined Drink

1. Touch splash screen → goes to menu
2. Click "Mojito" → SELECT button
3. Processing screen appears
4. MQTT command sent to ESP32

**Expected MQTT Message:**
```json
{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [
    {"relay": 1, "duration_sec": 5.0},
    {"relay": 2, "duration_sec": 3.0},
    {"relay": 3, "duration_sec": 7.0}
  ],
  "msg_id": "..."
}
```

### Test 2: Custom Mix

1. From menu → click "CUSTOM MIX"
2. Adjust sliders for each bottle
3. Click "START POUR"
4. Processing screen appears
5. MQTT command sent

### Test 3: Admin Panel

```powershell
python -m src.admin.admin_app
```

Use the admin panel to:
- Add/edit bottles
- Add/edit drinks
- Configure recipes
- Set custom limits

## 📊 Monitoring MQTT

### Subscribe to All Topics

```powershell
mosquitto_sub -h 192.168.1.100 -t "mixion/#" -v
```

### Manual Test Command

```powershell
mosquitto_pub -h 192.168.1.100 -t "mixion/command/esp32_1" -m '{
  "cmd": "dispense_parallel",
  "device_id": "esp32_1",
  "jobs": [
    {"relay": 1, "duration_sec": 2.0}
  ],
  "msg_id": "test-123"
}'
```

## 🐛 Common Issues

### Issue: "MQTT client not connected"

**Solution:**
1. Check broker IP in `config.py`
2. Ensure MQTT broker is running
3. Test with mosquitto_pub/sub
4. Check firewall settings

### Issue: "Video playback unavailable"

**Solution:**
1. Install VLC media player
2. Reinstall python-vlc: `pip install --upgrade python-vlc`
3. Check video path in config.py
4. Place a video at `assets/video/promo.mp4`

### Issue: "No drinks available"

**Solution:**
```powershell
python setup_sample_data.py
```

### Issue: Database locked

**Solution:**
1. Close all applications using the database
2. Delete `database/mixion.db`
3. Run `python app.py` to recreate

## 📁 Important Files

| File | Purpose |
|------|---------|
| `config.py` | MQTT broker IP, device ID, UI settings |
| `app.py` | Main application entry point |
| `setup_sample_data.py` | Populate database with test data |
| `database/mixion.db` | SQLite database (auto-created) |
| `assets/video/promo.mp4` | Splash screen video |

## 🔧 Customization

### Change Flow Rates

Edit in admin panel or database:
```sql
UPDATE bottles SET flow_rate = 15.0 WHERE id = 1;
```

### Add New Drink

1. Open admin panel
2. Go to "Drinks" tab
3. Click "Add Drink"
4. Go to "Recipes" tab
5. Configure ingredients

### Adjust Custom Limits

1. Open admin panel
2. Go to "Limits" tab
3. Set min/max for each bottle

## 🎨 Window Settings

Edit `config.py`:

```python
FULLSCREEN = False  # For testing on desktop
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
```

Press ESC to exit fullscreen mode (if enabled).

## ✅ Verification Checklist

- [ ] Python dependencies installed
- [ ] VLC installed
- [ ] MQTT broker accessible
- [ ] config.py configured
- [ ] Sample data loaded
- [ ] Application runs without errors
- [ ] Can navigate screens
- [ ] MQTT commands being sent
- [ ] ESP32 receiving commands

## 🚀 Production Deployment

1. Set `FULLSCREEN = True` in config.py
2. Configure correct MQTT broker IP
3. Add your splash video
4. Configure real bottles and flow rates
5. Add real drink menu
6. Test thoroughly
7. Deploy on kiosk hardware

## 📞 Next Steps

1. **Test with real ESP32**: Verify commands are received
2. **Calibrate flow rates**: Measure actual ml/sec for each pump
3. **Add real drinks**: Replace sample data with your menu
4. **Customize UI**: Update colors and fonts in config.py
5. **Add splash video**: Place your promo video in assets/video/

---

**Ready to pour! 🍹**
