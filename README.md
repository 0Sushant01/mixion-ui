# Mixion UI

Mixion UI is a Tkinter-based kiosk application for the Mixion drink machine. This version implements a fullscreen splash video and a placeholder menu screen.

## Features (Version 1)

- Fullscreen splash / attract video loop
- Tap or click anywhere to navigate to the menu screen
- Menu placeholder (black background with centered text)

## Project Structure

```
mixion-ui/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── core/
│   └── screens/
├── assets/
│   ├── video/
│   │   └── promo.mp4
│   └── images/
└── database/
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

```
python app.py
```

## Notes

- Place the promo video at `assets/video/promo.mp4`.
- The app runs in fullscreen mode and is designed for a touchscreen kiosk.

## Roadmap (Future)

- Drink selection UI
- Payments
- Admin and maintenance screens
- Hardware integration (ESP32, pumps, sensors)
- Telemetry and cloud sync
