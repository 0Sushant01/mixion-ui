# Mixion UI - Application Workflow

This document explains the step-by-step user journey, screen transitions, and background processes of the Mixion application.

---

## 1. Startup & Splash Screen

When the Raspberry Pi / Device boots up:
1. **Video Initialization**: The `app.py` script starts playing the promotional video (`promo.mp4`) immediately using an external process (MPV). This gives the user instant visual feedback.
2. **Background Loading**: While the video plays, Python initializes:
   - The SQLite Database (checking for migrations and default data).
   - The MQTT Client (attempting to connect to the configured Broker IP).
   - The Tkinter `MixionApp` Controller and rendering all UI screens hidden in memory.
3. **Handoff**: Once the heavy UI lifting is complete, the background script kills the video player and raises the Tkinter window.
4. **Transition**: The application immediately transitions to the **Menu Screen**.

---

## 2. Menu Screen (Main Hub)

This is the primary resting state for the application.

- **Display**: Shows a grid or paginated list of all active drinks pulled from the database, along with their prices.
- **Header/Footer**: Shows device connection status (Online/Offline based on MQTT pinging).
- **Idle Timeout (1 Minute)**: 
  - If a user is interacting with the screen, the interaction timer resets.
  - If there is **no interaction for 60 seconds**, the screen resets itself (e.g., returning to page 1, or clearing selected states) to ensure the machine is ready for the next customer.
- **User Actions**:
  - **Click a Drink**: Triggers the dispense logic. Transitions to the **Processing Screen**.
  - **Click "Custom Mix"**: Transitions to the **Custom Screen**.
  - **Click "Admin" (Hidden/Secret)**: Transitions to the Admin Interface for machine configuration.

---

## 3. Custom Mix Screen

This screen allows users to build their own drinks using sliders.

- **Display**: Shows sliders for each configured/enabled bottle attached to the machine.
- **Validation**: Enforces `min_ml` and `max_ml` limits set in the database to prevent overflowing a standard cup.
- **Total Calculation**: Dynamically adds up the total volume selected.
- **Idle Timeout**: Similar to the Menu, sitting idle for too long will automatically transition the user back to the **Menu Screen** to clear their custom draft.
- **User Actions**:
  - **Click "Dispense Custom Mix"**: Consolidates the slider values, checks limits, and transitions to the **Processing Screen**.
  - **Click "Back / Cancel"**: Aborts the custom mix and returns to the **Menu Screen**.

---

## 4. Processing Screen (Dispensing)

This screen manages the visual feedback while the machine is physically pouring liquid.

1. **Initialization**: 
   - Receives the requested drink ID or custom recipe.
   - Uses the `PourEngine` to convert requested milliliters into pumping seconds (based on calibrated flow rates).
   - Packages this into a JSON Payload.
2. **Command Execution**:
   - Publishes the JSON payload via MQTT to the `mixion/command/{device_id}` topic.
   - Listens for an acknowledgment from the ESP32 hardware.
3. **Visual Feedback**:
   - Displays a progress bar, an animated ring, or a "Dispensing..." message.
   - Listens to the `mixion/status/{device_id}` MQTT topic. As the ESP32 pumps, it sends percentage updates back to the UI, smoothly moving the progress bar.
4. **Completion Flow**:
   - Once the ESP32 broadcasts a `status: completed` message, the screen shows a "Drink Ready!" success message for a few seconds.
   - If an error occurs (e.g., pump timeout, MQTT disconnect), it shows a failure message.
5. **Transition**: After a short delay (e.g., 5 seconds), it automatically transitions back to the **Menu Screen** for the next order.

---

## Summary of Screen Flow Paths

- **Boot** --> Splash Video --> **Menu Screen**
- **Menu Screen** --> (Drink Clicked) --> **Processing Screen**
- **Menu Screen** --> (Custom Clicked) --> **Custom Screen**
- **Custom Screen** --> (Back Clicked) --> **Menu Screen**
- **Custom Screen** --> (Dispense Clicked) --> **Processing Screen**
- **Custom Screen** --> (Idle 60s) --> **Menu Screen**
- **Processing Screen** --> (Done/Error + 5s Delay) --> **Menu Screen**
