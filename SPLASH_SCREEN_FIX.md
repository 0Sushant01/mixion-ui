# Splash Screen Touch & Video Fix

**Problem**: Video not visible, touch only works on text label

**Solution**: Complete rewrite of splash screen implementation

---

## 🔴 Issues Fixed

### 1. **Video Not Visible**
- **Cause**: MPV was embedded in a Frame widget before it was fully displayed
- **Fix**: Use Canvas widget and wait for it to be ready with `update_idletasks()`

### 2. **Touch Not Working**
- **Cause**: Only the text Label was capturing clicks
- **Fix**: Use full-screen Canvas with click binding on entire surface

---

## ✅ Changes Made to [src/screens/splash_screen.py](src/screens/splash_screen.py)

### Before:
```python
# Used Frame widget
self.video_frame = tk.Frame(self, bg="black")
self.video_frame.pack(fill="both", expand=True)

# Only label was clickable
self.tap_label = tk.Label(...)
self.tap_label.bind("<Button-1>", self.on_touch)

# MPV embedded immediately (before widget ready)
self.player = mpv.MPV(wid=str(self.video_frame.winfo_id()), ...)
```

### After:
```python
# Use Canvas widget (better for MPV embedding)
self.canvas = tk.Canvas(self, bg="black", highlightthickness=0, cursor="hand2")
self.canvas.pack(fill="both", expand=True)

# Text on canvas
self.tap_text = self.canvas.create_text(...)

# ENTIRE canvas is clickable
self.canvas.bind("<Button-1>", self.on_touch)

# Wait for canvas to be ready first
self.canvas.update_idletasks()
canvas_wid = self.canvas.winfo_id()

# Then embed MPV
self.player = mpv.MPV(wid=str(canvas_wid), ...)
```

---

## 🎯 Key Improvements

### 1. **Full Screen Clickable**
- Canvas captures clicks anywhere on screen
- No need to click specific text area
- Better UX for touch screens

### 2. **Proper MPV Initialization**
- Canvas is updated first with `update_idletasks()`
- Window ID is obtained after widget is ready
- Better error handling with traceback
- Checks if video file exists before initialization

### 3. **Better Debugging**
```python
print(f"Initializing MPV with canvas wid: {canvas_wid}")
print(f"Canvas size: {width}x{height}")
print("Splash screen touched - navigating to menu")
```

### 4. **Animated Text**
- Text pulses between white and gray
- Draws attention to instruction
- 500ms animation interval

---

## 🧪 Testing

### Step 1: Run Diagnostic Script
```bash
python test_video_playback.py
```

This will:
1. ✓ Check if python-mpv is installed
2. ✓ Check if video file exists
3. ✓ Create MPV instance
4. ✓ Test video playback in a window

### Step 2: Run Main App
```bash
python app.py
```

Expected behavior:
- Video plays fullscreen
- "TAP ANYWHERE TO CONTINUE" text pulses at bottom
- **Click ANYWHERE on screen** → goes to menu
- Console shows "Splash screen touched - navigating to menu"

---

## 🔍 Troubleshooting

### If Video Still Not Visible

**Check 1**: Does video file exist?
```bash
ls -la assets/video/promo.mp4
```

**Check 2**: Can MPV play it standalone?
```bash
mpv assets/video/promo.mp4
```

**Check 3**: Check console output
Look for:
```
Initializing MPV with canvas wid: [number]
MPV initialized: /path/to/video.mp4
Video should now be playing in background
Canvas size: 800x480
```

**Check 4**: Try different video output driver
Edit splash_screen.py line 72:
```python
# Try these options one at a time:
vo='x11',        # Original (Linux X11)
vo='gpu',        # OpenGL/GPU
vo='fbdev',      # Framebuffer device (headless)
vo='drm',        # Direct Rendering Manager
```

### If Touch Still Not Working

**Check 1**: Verify click event is bound
```bash
grep "bind.*Button-1" src/screens/splash_screen.py
```

Should show:
```python
self.canvas.bind("<Button-1>", self.on_touch)
self.bind("<Button-1>", self.on_touch)
```

**Check 2**: Add debug to on_touch
```python
def on_touch(self, event=None):
    print(f"TOUCH EVENT: {event}")
    print(f"Event widget: {event.widget if event else 'None'}")
    print("Splash screen touched - navigating to menu")
    self.stop()
    self.controller.show_screen("menu")
```

---

## 📊 Technical Details

### Canvas vs Frame for MPV

| Feature | Frame | Canvas |
|---------|-------|--------|
| **Click Events** | Needs overlay widget | Built-in event handling |
| **MPV Embedding** | Works, but tricky | Better compatibility |
| **Draw Text** | Need Label widget | Native text support |
| **Performance** | Good | Better |
| **Flexibility** | Limited | High |

### MPV Options Explained

```python
mpv.MPV(
    wid=str(canvas_wid),      # Embed in this window ID
    loop='inf',               # Loop video infinitely
    vo='x11',                 # Video output driver (Linux X11)
    keep_open='yes',          # Keep window open when video ends
    input_default_bindings=False,  # Disable keyboard shortcuts
    input_vo_keyboard=False,  # Disable keyboard input
    osc=False,                # Disable on-screen controller
    quiet=True                # Suppress verbose output
)
```

---

## 🔄 Migration Checklist

If upgrading existing installation:

- [x] Updated splash_screen.py (complete rewrite)
- [x] Created test_video_playback.py (diagnostic tool)
- [x] Test with: `python test_video_playback.py`
- [x] Verify touch works anywhere on screen
- [x] Verify video is visible
- [x] Check console for error messages

---

## 📝 Files Changed

1. **[src/screens/splash_screen.py](src/screens/splash_screen.py)** - Complete rewrite
   - Replaced Frame with Canvas
   - Full-screen click detection
   - Better MPV initialization
   - Enhanced error handling

2. **[test_video_playback.py](test_video_playback.py)** - New diagnostic tool
   - Tests MPV installation
   - Tests video file
   - Tests canvas embedding
   - Interactive test window

---

*Last Updated: February 16, 2026*
