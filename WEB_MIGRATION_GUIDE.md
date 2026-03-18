# Mixion UI - Web App Migration Guide

This guide provides step-by-step instructions on how to migrate the current Mixion UI (Tkinter-based) to a modern web application (HTML/JS/CSS + FastAPI). It is designed so you can start from scratch and preserve all core logic.

---

## 1. Prerequisites

You will need to install the following Python packages for the web backend:
```bash
pip install fastapi "uvicorn[standard]" websockets
```

---

## 2. Web Backend Setup (`web_app.py`)

Create a new file named `web_app.py` in the root directory. This will replace the old `app.py`. Its purpose is to serve the HTML frontend, initialize the database/MQTT via your existing core code, and handle REST/WebSocket APIs.

**Create `web_app.py`:**
```python
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import config
from src.core.database import init_database
from src.core.mqtt_client import MQTTClient
from src.core.pour_engine import PourEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application State
class AppState:
    def __init__(self):
        self.db = None
        self.mqtt_client = None
        self.pour_engine = None
        self.active_websockets = []
        self.background_tasks = set()

app_state = AppState()

# WebSocket Manager for broadcasting MQTT events to the browser
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {e}")

manager = ConnectionManager()

def mqtt_status_listener(data):
    """Callback fired by MQTT client when status is received"""
    if data:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast({"type": "device_status", "data": data}))
        except RuntimeError:
            pass

async def background_status_poller():
    """Periodically asks MQTT client for status"""
    while True:
        try:
            if app_state.mqtt_client and app_state.mqtt_client.is_connected():
                app_state.mqtt_client.publish_status_request(
                    config.STATUS_REQUEST_TOPIC, 
                    config.STATUS_REQUEST_PAYLOAD
                )
                status_str = app_state.mqtt_client.get_device_status(config.DEVICE_STATUS_TIMEOUT_SEC)
                await manager.broadcast({"type": "connection_status", "status": status_str})
        except Exception as e:
            pass
        await asyncio.sleep(config.STATUS_REQUEST_INTERVAL_SEC)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    app_state.db = init_database()
    app_state.mqtt_client = MQTTClient(
        broker=config.MQTT_BROKER, port=config.MQTT_PORT,
        device_id=config.DEVICE_ID, status_topic=config.TOPIC_STATUS
    )
    app_state.mqtt_client.add_status_listener(mqtt_status_listener)
    app_state.mqtt_client.connect()
    app_state.pour_engine = PourEngine(app_state.db, app_state.mqtt_client)
    
    poll_task = asyncio.create_task(background_status_poller())
    app_state.background_tasks.add(poll_task)
    
    yield
    
    # --- Shutdown ---
    poll_task.cancel()
    app_state.mqtt_client.disconnect()


app = FastAPI(lifespan=lifespan)

# Mount Frontend Files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    html_file = os.path.join("static", "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h1>Web UI Not Built Yet</h1>", status_code=404)

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## 3. Creating REST API Routes

You need REST APIs so the frontend can query data from SQLite and trigger the pour engine. 
Create a file `src/api/routes.py` (you must create the `src/api` folder).

**Create `src/api/routes.py`:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from web_app import app_state

router = APIRouter()

@router.get("/drinks")
def get_drinks():
    return app_state.db.get_active_drinks()

@router.get("/bottles")
def get_bottles():
    return app_state.db.get_enabled_bottles()

@router.get("/limits")
def get_limits():
    return app_state.db.get_limits_map()

@router.post("/dispense/drink/{drink_id}")
def dispense_drink(drink_id: int):
    success, msg, msg_id, payload = app_state.pour_engine.dispense_drink(drink_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg, "msg_id": msg_id}

class CustomDispenseRequest(BaseModel):
    bottle_amounts: Dict[int, int]  # mapped as { bottle_id: amount_ml }

@router.post("/dispense/custom")
def dispense_custom(req: CustomDispenseRequest):
    success, msg, msg_id, payload = app_state.pour_engine.dispense_custom(req.bottle_amounts)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg, "msg_id": msg_id}
```

*Note: You must link these routes in `web_app.py` right before the `os.makedirs("static", exist_ok=True)` block like this:*
```python
from src.api.routes import router as api_router
app.include_router(api_router, prefix="/api")
```

---

## 4. Frontend Construction (`static/`)

Create a `static` folder in the root directory. Inside it, create `index.html`. 

**Create `static/index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mixion Web UI</title>
    <style>
        body { font-family: sans-serif; background: #1a1a2e; color: white; display:flex; flex-direction:column; align-items:center; }
        .screen { display: none; width: 100%; max-width: 800px; padding: 20px; }
        .active { display: block; }
        .drink-btn { padding: 15px; margin: 5px; background: #0f3460; color: white; border: none; cursor: pointer; border-radius: 8px;}
        #top-bar { width: 100%; padding: 10px; text-align: right; border-bottom: 1px solid #333; }
    </style>
</head>
<body>
    <div id="top-bar">
        Status: <span id="conn-status">Connecting...</span>
    </div>

    <!-- Menu Screen -->
    <div id="screen-menu" class="screen active">
        <h1>Select a Drink</h1>
        <div id="drink-list">Loading...</div>
        <button onclick="showScreen('screen-custom')">Custom Mix</button>
    </div>

    <!-- Custom Mix Screen -->
    <div id="screen-custom" class="screen">
        <h1>Custom Mix</h1>
        <div id="custom-bottles">Loading...</div>
        <button onclick="dispenseCustom()">Dispense Custom</button>
        <button onclick="showScreen('screen-menu')">Back</button>
    </div>

    <!-- Processing Screen -->
    <div id="screen-processing" class="screen">
        <h1>Dispensing...</h1>
        <h2 id="dispense-progress">0%</h2>
    </div>

    <script>
        const ws = new WebSocket(`ws://${location.host}/ws`);
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === "connection_status") {
                document.getElementById('conn-status').innerText = msg.status;
            } else if (msg.type === "device_status") {
                if (msg.data.cmd === "status") {
                    // Update progress on processing screen here if dispensing
                    console.log("ESP Status update: ", msg.data);
                }
            }
        };

        function showScreen(screenId) {
            document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
        }

        async function loadDrinks() {
            const res = await fetch('/api/drinks');
            const drinks = await res.json();
            const list = document.getElementById('drink-list');
            list.innerHTML = "";
            drinks.forEach(drink => {
                const btn = document.createElement('button');
                btn.className = "drink-btn";
                btn.innerText = `${drink.name} - ₹${drink.price}`;
                btn.onclick = () => dispenseDrink(drink.id);
                list.appendChild(btn);
            });
        }

        async function dispenseDrink(id) {
            showScreen('screen-processing');
            await fetch(`/api/dispense/drink/${id}`, { method: 'POST' });
        }

        async function dispenseCustom() {
            // Read ranges and submit to /api/dispense/custom
            showScreen('screen-processing');
        }

        // On Load
        loadDrinks();
    </script>
</body>
</html>
```

---

## 5. How to Run It

Once you have created all the files above, run the server using `uvicorn`:

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

1. Open your web browser and go to `http://localhost:8000`.
2. You will see the HTML interface. 
3. The server will initialize your exact SQLite database and MQTT client. 
4. The WebSocket will automatically start streaming ESP32 connection status to the browser header.

Once you confirm the web app is working and dispensing correctly via MQTT, you can safely delete the `src/screens` and Tkinter-specific UI files.
