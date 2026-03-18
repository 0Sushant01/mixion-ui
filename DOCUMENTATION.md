# Mixion System Documentation

This document outlines the complete internal architecture, computational logic, strategies, and methodologies utilized within the Mixion application (Python 3 Tkinter UI + ESP32 Hardware Integration).

---

## 1. High-Level Architecture
Mixion is a hybrid system built primarily with a modular, asynchronous Graphical User Interface (GUI) running on a master computer/tablet (e.g. Raspberry Pi), interfacing rapidly with a physical dispensing microcontroller (ESP32) through an MQTT message broker broker.

**Key Technologies:**
1. **Frontend**: CustomTkinter / Tkinter (Hardware-accelerated GUI via X11).
2. **Backend**: Python 3.
3. **Database**: SQLite3 (Local file persistence `mixion.db`).
4. **Networking**: Paho-MQTT (Asynchronous protocol, QoS level 1).
5. **Video Processing**: MPV (Low-latency display via `libmpv`).

---

## 2. Core Methodologies & Logic Strategy

### A. The Engine Pipeline (`pour_engine.py`)
The most mathematically crucial component is the pour logic engine. It uses deterministic calculations to convert requested liquid volume into physical hardware-pump duration.

**Methodology**:
1. Retrieve custom configuration dictating a liquid type, target relay position (e.g. `Relay 2`), and a target volume (e.g. `25 ml`).
2. Identify the specific bottle's predefined hardware flow rate (e.g. `600 ml/min`).
3. Compute dispensing seconds using the following algorithm:
   - `duration = ((amount_ml * 60) / flow_rate) + latency_offset`
   - *Example: 25ml at 600ml/m requires `(25 * 60 / 600) + 0.3 = 2.8` seconds of open relay time.*
4. The result dictates precisely how long the target physical pump powers on to deliver exact measurements without relying on live feedback loops which could add networking latency blockages.

### B. Networking Subsystem (`mqtt_client.py`)
To ensure the GUI never freezes while waiting on hardware execution, an asynchronous threading model is implemented using MQTT.

**Strategy**:
1. **Non-Blocking Dispatch**: Commands (like `dispense_parallel`) are fired rapidly across the Wi-Fi protocol using threading locks, immediately returning execution control to the main UI. 
2. **No Infinite Hangs**: `.wait_for_publish(timeout=5.0)` is forcefully applied. If the hardware server dies mid-pour command, the UI safely catches the exception and drops the request rather than deadlocking the user's touchscreen terminal.
3. **Payload Structure**: Data packages sent over the network strictly adhere to a streamlined minimal JSON footprint specifying only the target hardware relay and operational duration seconds. No excessive metadata (e.g. `amount_ml`) is bundled to save packet weight.

### C. State Management & Graphics Delivery
The UI utilizes several advanced methodologies for high-performance touch feedback:

**UI Generation (`menu_screen.py`)**:
- Uses an implementation of the *Diffing Algorithm Strategy* applied typically in web-framework DOM updates. 
- Instead of rebuilding 50 images from disk upon every page load, it computes a `JSON` configuration hash of the underlying SQLite database states. If the hash remains static, screen regeneration is bypassed entirely, slashing loading times from seconds down to `0.0ms` directly executing a cache response.

---

## 3. Core Directory & File Map

* `app.py` ➔ Core execution origin. Manages MPV video dismissal synchronization and `app_controller` startup.
* `/assets/` ➔ Images, Icons, and MPV standard formats (like `.mp4` Splash Screens).
* `/database/` ➔ Holds `mixion.db` persistent data structure tracking ingredients, limits, rates, and historical logs.
* `/src/`:
  * `/core/`: 
     * `app_controller.py` ➔ Controls screen routing matrices and master component injection.
     * `database.py` ➔ Abstraction wrapper utilizing Context Managers for safe threaded SQL transactions.
     * `mqtt_client.py` ➔ Thread-safe network proxy class handling the Paho MQTT connection flow.
     * `pour_engine.py` ➔ Processing gateway orchestrating recipe computation algorithms.
  * `/screens/`:
     * `splash_screen.py` ➔ Non-blocking background thread monitor rendering promotional media content.
     * `menu_screen.py` ➔ Core advanced Kiosk pagination interface leveraging cached widgets and CustomTkinter aesthetics.
     * `custom_screen.py` ➔ Advanced mix slider screen routing array configurations to the backend.
     * `processing_screen.py` ➔ Event-loop loading canvas utilizing concurrent animations synchronized safely to underlying Database state insertions.

---

## 4. Hardware/Software Synchronization

**Flow of Execution**:
1. User interacts with UI (e.g. Selects standard drink or custom).
2. UI contacts SQLite database for configuration maps.
3. Config map traverses `pour_engine.py` for conversion algorithms.
4. Calculated schema hits `mqtt_client.py` executing threaded dispatch.
5. `processing_screen.py` is called displaying load animations.
6. The `ESP32` signals `Completed` upon relay completion back to MQTT.
7. Callback thread fires into UI, terminating the UI load loop gracefully.
