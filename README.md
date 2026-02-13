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
- OpenCV and Pillow (listed in requirements.txt)

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

### 3) Install dependencies

```
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

### Programming Examplesin/max ml per bottle)

This is an **operator/developer tool** - not the customer-facing kiosk UI.

### Database Schema

- **bottles**: Defines installed liquids (name, position, enabled status)
- **drinks**: Predefined menu items (name, price, active status)
- **recipes**: Ingredient mapping for drinks (drink_id, bottle_id, amount_ml)
- **custom_limits**: Safety limits for custom pour (min_ml, max_ml per bottle)

### Default Data

On first boot, the database is populated with:
- 3 default bottles (Bottle A, B, C)
- Custom pour limits (0-150ml per bottle)

### Working with the Database

See `examples/database_usage.py` for code examples on:
- Reading bottles
- Creating drinks with recipes
- Querying custom limits

Run the example:
```
python examples/database_usage.py
```
```

## Adding Video and Audio

1. Place your promo video (with audio) at `assets/video/promo.mp4`
2. The app will automatically extract and play audio from the MP4 file on startup

## Notes

- The app runs in fullscreen mode and is designed for a touchscreen kiosk.
- Audio and video play in sync and loop continuously on the splash screen.

## Roadmap (Future)

- Drink selection UI
- Payments
- Admin and maintenance screens
- Hardware integration (ESP32, pumps, sensors)
- Telemetry and cloud sync
