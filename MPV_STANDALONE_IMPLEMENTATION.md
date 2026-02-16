# Splash Screen Implementation - Runtime MPV Configuration

**Clean Architecture**: Video plays BEFORE app starts using runtime-controlled input

---

## 🎯 How It Works

### Old Approach (BROKEN)
```
Start App → Embed MPV in tkinter canvas → Touch blocked by MPV → ❌
```

### New Approach (PRODUCTION READY!)
```
Play MPV (runtime config) → User touches → MPV exits → Start App → ✅
```

### Key Innovation: Runtime Configuration
- **No system files modified**
- Touch-to-exit applies **ONLY** to splash video
- Other MPV usage remains unaffected
- Production compliant

---

## 🚀 Implementation

### Flow Diagram

```
┌─────────────────────────────────────────────────┐
│  1. Run: python app.py                          │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  2. Play splash video FULLSCREEN (MPV process)  │
│     - Video loops infinitely                    │
│     - Click anywhere → MPV exits                │
└────────────────┬────────────────────────────────┘
                 │
                 ↓ (User clicks)
┌─────────────────────────────────────────────────┐
│  3. MPV exits, subprocess.run() returns         │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  4. Start Tkinter app at MENU screen            │
│     - No splash screen needed!                  │
│     - Already saw video                         │
└─────────────────────────────────────────────────┘
```

---

## 📝 Code Changes

### 1. [app.py](app.py)

**Before**:
```python
if __name__ == "__main__":
    init_database()
    app = MixionApp(video_path=_resolve_video_path())
    app.run()
```

**After**:
```python
if __name__ == "__main__":
    init_database()
    
    # Play splash video BEFORE starting app
    video_path = _resolve_video_path()
    play_splash_video(video_path)  # ← BLOCKS until user clicks
    
    # After video exits, start the main app
    app = MixionApp(video_path=video_path)
    app.run()
```

### 2. [src/screens/splash_screen.py](src/screens/splash_screen.py)

New function: `play_splash_video()` with **runtime configuration**

```python
def play_splash_video(video_path):
    """
    Play splash video with runtime touch-to-exit.
    Uses runtime MPV configuration (no system files modified).
    """
    subprocess.run([
        "mpv",
        "--fullscreen",
        "--loop=inf",
        "--no-osd-bar",
        "--quiet",
        "--input-default-bindings=no",   # Disable ALL default bindings
        "--input-conf=/dev/null",         # Ignore persistent config files
        "--input-cmdlist=MOUSE_BTN0 quit", # Runtime touch-to-quit
        video_path
    ])
```

**Critical Parameters**:
- `--input-default-bindings=no`: Starts with clean slate
- `--input-conf=/dev/null`: Ignores ~/.config/mpv/input.conf
- `--input-cmdlist=MOUSE_BTN0 quit`: Touch-to-quit for THIS execution only

### 3. [src/core/app_controller.py](src/core/app_controller.py)

**Before**: Started at splash screen
```python
self._screens = {
    "splash": SplashScreen(...),
    "menu": MenuScreen(...),
    ...
}
self.show_screen("splash")
```

**After**: Start directly at menu
```python
self._screens = {
    "menu": MenuScreen(...),
    "custom": CustomMixScreen(...),
    "processing": ProcessingScreen(...),
}
self.show_screen("menu" Approach

### ⚠️ IMPORTANT: Cleanup Legacy Config

If you previously used persistent MPV configuration, **remove it**:

```bash
chmod +x setup_mpv_config.sh
./setup_mpv_config.sh
```

Or manually:
```bash
rm -f ~/.config/mpv/input.conf
```

### Why No Persistent Config?

**Problem with ~/.config/mpv/input.conf**:
- Applies to ALL MPV usage globally
- Training videos would also exit on touch
- Dashboard playback affected
- Hard to debug unexpected exits

**Solution: Runtime Configuration**:
```bash
mpv --input-conf=/dev/null \
    --input-cmdlist="MOUSE_BTN0 quit" \
    splash.mp4
```

- ✅ Applies ONLY to this execution
- ✅ No system files modified
- ✅ Other MPV usage unaffected
- ✅ Predictable behavior
- ✅ Production safe
# Keyboard shortcuts (backup)Runtime Config |
|---------|----------------|----------------|
| **Video Visible** | ❌ Often broken | ✅ Always works |
| **Touch Works** | ❌ Blocked by MPV | ✅ Native MPV input |
| **System Files** | ❌ Needs config | ✅ Zero modification |
| **Other Videos** | ❌ Affected | ✅ Unaffected |
| **Code Complexity** | 🔴 High (200+ lines) | 🟢 Low (45 lines) |
| **Reliability** | ❌ Fragile | ✅ Robust |
| **Dependencies** | python-mpv + libmpv | mpv command only |
| **Production Safe** | 🔴 Risky | 🟢 Complian

| Feature | Old (Embedded) | New (Standalone) |
|---------|----------------|------------------|
| **Video Visible** | ❌ Often broken | ✅ Always works |
| **Touch WoClean Up Legacy Config (If Needed)

```bash
chmod +x setup_mpv_config.sh
./setup_mpv_config.sh
```

### Step 2: Test Runtime Touch-to-Exit

```bash
mpv --fullscreen \
    --input-conf=/dev/null \
    --input-cmdlist="MOUSE_BTN0 quit" \
    assets/video/promo.mp4
```

- Video should play fullscreen
- Touch/click anywhere → video exits immediately
- No permanent configuration created

### Step 3: Verify Other Videos Unaffected

```bash
mpv assets/video/training.mp4
```

- Video plays normally
- Touch does NOT exit (expected behavior)
- Only splash video has touch-to-quit

### Step 4
### Step 2: Test Video Playback Standalone

```bash
mpv --fullscreen assets/video/promo.mp4
```

- Video should play fullscreen
- Click anywhere → video should exit
- If not, check `~/.config/mpv/input.conf`

### Step 3: Run App

```bash
python app.py
```

**Expected Flow**:
1. ✅ Video plays fullscreen (looping)
2. ✅ Click/tap anywhere on screen
3.Clean up any legacy configuration
chmod +x setup_mpv_config.sh
./setup_mpv_config.sh

# Install Python packages (NO python-mpv needed!)
pip install -r requirements.txt  # Only needs paho-mqtt now!
```

### Verify MPV Installation

```bash
# Check MPV is installed
which mpv
# Should output: /usr/bin/mpv

# Check version
mpv --version

# Test runtime touch-to-quit
mpv --fullscreen \
    --input-conf=/dev/null \
    --input-cmdlist="MOUSE_BTN0 quit" \
    assets/video/promo.mp4
# Touch anywhere → should exit immediatelyt  # Only needs paho-mqtt now!
```

### Verify MPV InstallatioTouch

**Problem**: Runtime arguments not recognized

**Solution**:
```bash
# Check MPV version (needs recent version)
mpv --version

# If MPV is old, update it
sudo apt-get update
sudo apt-get upgrade mpv

# Test with explicit runtime config
mpv --fullscreen \
    --input-default-bindings=no \
    --input-conf=/dev/null \
    --input-cmdlist="MOUSE_BTN0 quit" \
    assets/video/promo.mp4
```

### Legacy Config Interfering

**Problem**: Old ~/.config/mpv/input.conf still exists

**Solution**:
```bash
# Remove it
rm -f ~/.config/mpv/input.conf

# Or run cleanup script
./setup_mpv_config.sh

## 🐛 Troubleshooting

### Video Doesn't Exit on Click

**Problem**: MPV not configured to quit on click

**Solution**:
```bash
# Create/edit config file
nano ~/.config/mpv/input.conf

# Add this line:
MOUSE_BTN0 quit

# Save and exit (Ctrl+X, Y, Enter)

# Test again
mpv --fullscreen assets/video/promo.mp4
```

### MPV Command Not Found

**Problem**: MPV not installed

**Solution**:
```bash
sudo apt-get install mpv
```

### Video File Not Found

**Problem**: Video path incorrect

**Solution**:
```bash
# Check file exists
ls -la assets/video/promo.mp4

# If missing, add your video file:
cp /path/to/your/video.mp4 assets/video/promo.mp4
```

### Video Plays But App Doesn't Start

**Problem**: `play_splash_video()` blocking forever

**Solution**:
- Press 'q' to manually quit MPV
- Check MPV configuration (click-to-quit)
- Check console for errors

---

## 📦 Requirements Update

### Before

```txt
paho-mqtt>=1.6.1
python-mpv>=1.0.1  # ← Complex, needs libmpv
```

### After

```txt
paProblem with persistent config**:
- ~/.config/mpv/input.conf applies globally
- Training videos exit on touch
- Dashboard playback affected
- Hard to debug

**Solution with runtime config**:
- MPV runs as its own process
- Input config applied per-execution only
- No system files modified
- Each MPV call has isolated behavior
- Simple, robust, production-safe

### subprocess.run() is Blocking

This is **exactly** what we want!

```python
play_splash_video(video_path)  # ← Blocks here
print("This runs AFTER video exits")
```

The app waits for the video to finish before continuing. Perfect for splash screens!

### Runtime vs Persistent Configuration

**Persistent (OLD)**:
```bash
# In ~/.config/mpv/input.conf
MOUSE_BTN0 quit

# Affects ALL mpv commands
mpv training.mp4  # ← Also exits on touch! BAD!
```

**Runtime (NEW)**:
```bash
# Only affects THIS command
mpv --input-cmdl (45 lines)
- ✅ No dependencies on python-mpv
- ✅ No system files modified
- ✅ Other videos unaffected
- ✅ Professional user experience
- ✅ Easy to debug
- ✅ Production compliant
- ✅ Maintenance safe

**This is the correct way to implement splash screens with video!**

## 📋 Deployment Checklist

- [ ] Install MPV: `sudo apt-get install mpv`
- [ ] Remove legacy config: `./setup_mpv_config.sh`
- [ ] Test splash: `python app.py` → touch to exit
- [ ] Test other videos: `mpv training.mp4` → should NOT exit on touch
- [ ] Verify no ~/.config/mpv/input.conf exists
- [ ] Document for operations team
2. Clear: "Click/tap anywhere"
3. Instant response
4. Professional feel

---

## 🔑 Key Insights

### Why This Works

**Problem with embedding**:
- MPV embeds as a separate window in canvas
- Captures ALL mouse/touch events
- tkinter can't intercept events
- Complex, fragile, platform-specific

**Solution with standalone**:
- MPV runs as its own process
- Native input handling (works perfectly)
- No tkinter involvement (no conflicts)
- Simple, robust, cross-platform

### subprocess.run() is Blocking

This is **exactly** what we want!

```python
play_splash_video(video_path)  # ← Blocks here
print("This runs AFTER video exits")
```

The app waits for the video to finish before continuing. Perfect for splash screens!

---

## 📊 File Changes Summary

| File | Change | Lines Changed |
|------|--------|---------------|
| app.py | Add video playback call | +5 |
| src/screens/splash_screen.py | Simplified, added play_splash_video() | -150, +40 |
| src/core/app_controller.py | Remove splash screen import | -5 |
| setup_mpv_config.sh | New configuration script | +30 |

**Total**: Removed ~120 lines of complex code, added ~75 lines of simple code

**Net**: Simpler AND better!

---

## 🎉 Result

- ✅ Video always visible
- ✅ Touch always works
- ✅ Simpler code
- ✅ No dependencies on python-mpv
- ✅ Professional user experience
- ✅ Easy to debug
- ✅ Cross-platform compatible

**This is the correct way to implement splash screens with video!**

---

*Last Updated: February 16, 2026*
