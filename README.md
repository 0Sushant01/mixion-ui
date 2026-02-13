# Mixion UI

Mixion UI is a Tkinter-based kiosk application for the Mixion drink machine. This version implements a fullscreen splash video and a placeholder menu screen.

## Features (Version 1)

- Fullscreen splash / attract video loop with audio
- Tap or click anywhere to navigate to the menu screen
- Menu placeholder (black background with centered text)
- SQLite database with auto-migration
- Drink recipe and bottle management system

## Project Structure

```
mixion-ui/
├── app.py                    # Main kiosk application
├── db.py                     # Database admin tool
├── requirements.txt
├── README.md
├── src/
│   ├── core/
│   │   ├── app_controller.py
│   │   └── database.py
│   ├── admin/                # Admin UI modules
│   │   ├── admin_app.py
│   │   ├── bottles_page.py
│   │   ├── drinks_page.py
│   │   ├── recipes_page.py
│   │   └── limits_page.py
│   ├── screens/
│   └── widgets/
├── assets/
│   ├── video/
│   │   └── promo.mp4
│   └── images/
├── database/
│   └── mixion.db (auto-created)
└── examples/
    └── database_usage.py
```

## Requirements

- Python 3.9+ recommended
- VLC media player installed on system
- python-vlc (listed in requirements.txt)

## Setup

### 1) Create a virtual environment

Windows (PowerShell):

```
python -m venv venv
```

macOS / Linux:

```
python3 -m venv venv
```

### 2) Activate the virtual environment

Windows (PowerShell):

```
venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```
venv\Scripts\activate.bat
```

macOS / Linux:

```
source venv/bin/activate
```

### 3) Install VLC media player

**Raspberry Pi / Linux:**
```bash
sudo apt-get update
sudo apt-get install vlc
```

**Windows:**
Download and install from https://www.videolan.org/vlc/

**macOS:**
```bash
brew install vlc
```

### 4) Install Python dependencies

```bash
pip install -r requirements.txt
```

## Running the App

### Quick Start

1. **First time setup:**
   ```bash
   python db.py
   ```
   Use the admin tool to configure bottles, add drinks, and define recipes.

2. **Run the kiosk:**
   ```bash
   python app.py
   ```
   This launches the customer-facing fullscreen UI.

### Applications

**Kiosk Application (Customer UI):**
```
python app.py
```
- Fullscreen touch interface
- Plays splash video
- Shows menu (future: drink selection)

**Database Manager (Admin Tool):**
```
python db.py
```
- Windowed desktop application
- Configure system settings
- Manage bottles, drinks, recipes

See [Database Manager Guide](docs/DATABASE_MANAGER_GUIDE.md) for detailed usage instructions.

## Database Management

### Database Schema

The app uses SQLite (`database/mixion.db`) for data storage. The database is automatically created and migrated on first run.

**Tables:**

- **bottles**: Defines installed liquids (name, position, enabled status)
- **drinks**: Predefined menu items (name, price, active status)
- **recipes**: Ingredient mapping for drinks (drink_id, bottle_id, amount_ml)
- **custom_limits**: Safety limits for custom pour (min_ml, max_ml per bottle)

**Default Data:**

On first boot, the database is populated with:
- 3 default bottles (Bottle A, B, C)
- Custom pour limits (0-150ml per bottle)

### Programming Examples

See `examples/database_usage.py` for code examples on:
- Reading bottles
- Creating drinks with recipes
- Querying custom limits

Run the example:
```
python examples/database_usage.py
```
```

## Adding Video

1. Place your promo video (MP4 with audio) at `assets/video/promo.mp4`
2. The video will automatically play with audio on startup

**Requirements:**
- Video format: MP4
- Audio: Included in the video file
- The video fills the entire screen and loops continuously

## Notes

- The app runs in fullscreen mode and is designed for a touchscreen kiosk
- Video playback uses VLC for reliable audio/video synchronization
- Database is automatically created and migrated on first run

## Roadmap (Future)

- Drink selection UI
- Payments
- Admin and maintenance screens
- Hardware integration (ESP32, pumps, sensors)
- Telemetry and cloud sync
