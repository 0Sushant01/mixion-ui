# Runtime MPV Configuration - Quick Reference

**Objective**: Touch-to-exit for splash video WITHOUT system-level configuration files

---

## ⚠️ Pre-Condition: Cleanup

Remove any legacy persistent configuration:

```bash
rm -f ~/.config/mpv/input.conf
```

Or use the cleanup script:

```bash
./setup_mpv_config.sh
```

---

## 🎯 Implementation

### Splash Video Command

```bash
mpv --fullscreen \
    --loop=inf \
    --no-osd-bar \
    --quiet \
    --input-default-bindings=no \
    --input-conf=/dev/null \
    --input-cmdlist="MOUSE_BTN0 quit" \
    splash.mp4
```

### Python Integration

```python
import subprocess

def play_splash_video(video_path):
    subprocess.run([
        "mpv",
        "--fullscreen",
        "--loop=inf",
        "--no-osd-bar",
        "--quiet",
        "--input-default-bindings=no",   # Clean slate
        "--input-conf=/dev/null",         # Ignore persistent configs
        "--input-cmdlist=MOUSE_BTN0 quit", # Runtime touch-to-quit
        video_path
    ])

# Usage
play_splash_video("assets/video/promo.mp4")  # Blocks until touch
print("Continuing to main app...")
```

---

## 🔍 Parameter Explanation

| Parameter | Purpose |
|-----------|---------|
| `--fullscreen` | Display in fullscreen mode |
| `--loop=inf` | Loop video infinitely |
| `--no-osd-bar` | Hide on-screen display |
| `--quiet` | Suppress console output |
| `--input-default-bindings=no` | Disable ALL default MPV keybindings |
| `--input-conf=/dev/null` | Ignore ~/.config/mpv/input.conf |
| `--input-cmdlist=MOUSE_BTN0 quit` | **Runtime only**: Click/touch to quit |

---

## ✅ Advantages Over Persistent Config

| Aspect | Persistent (~/.config/mpv/input.conf) | Runtime (--input-cmdlist) |
|--------|---------------------------------------|---------------------------|
| **Scope** | ALL mpv commands | THIS execution only |
| **System Files** | Creates config file | Zero modification |
| **Other Videos** | Affected (training, dashboard) | Unaffected |
| **Debugging** | Hidden behavior | Explicit in code |
| **Rollback** | Must delete file | Just change command |
| **Production** | ⚠️ Risky | ✅ Safe |

---

## 🧪 Verification

### Test 1: Splash Video (Should Exit on Touch)

```bash
mpv --fullscreen \
    --input-conf=/dev/null \
    --input-cmdlist="MOUSE_BTN0 quit" \
    assets/video/promo.mp4
```

**Expected**: Touch anywhere → video exits

### Test 2: Training Video (Should NOT Exit on Touch)

```bash
mpv assets/video/training.mp4
```

**Expected**: Touch does nothing, video continues

### Test 3: Verify No Persistent Config

```bash
cat ~/.config/mpv/input.conf
```

**Expected**: File not found OR file is empty

---

## 🚀 Runtime Flow

```
┌─────────────────────────────────────┐
│ python app.py                       │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│ play_splash_video()                 │
│   subprocess.run([                  │
│     "mpv",                          │
│     "--input-cmdlist=...",  ← RUNTIME CONFIG
│     "splash.mp4"                    │
│   ])                                │
└──────────────┬──────────────────────┘
               │
               ↓ (MPV running)
┌─────────────────────────────────────┐
│ Video loops infinitely              │
│ Waiting for touch...                │
└──────────────┬──────────────────────┘
               │
               ↓ (User touches)
┌─────────────────────────────────────┐
│ MPV exits (MOUSE_BTN0 quit)         │
│ subprocess.run() returns            │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│ app.run()                           │
│ Main application starts             │
└─────────────────────────────────────┘
```

**Key**: Input config exists ONLY during subprocess execution!

---

## 🔧 Troubleshooting

### Issue: Touch doesn't exit video

**Possible causes**:
1. Old MPV version (doesn't support --input-cmdlist)
2. Legacy ~/.config/mpv/input.conf interfering

**Solutions**:
```bash
# Update MPV
sudo apt-get update
sudo apt-get upgrade mpv

# Remove legacy config
rm -f ~/.config/mpv/input.conf

# Test again
mpv --input-cmdlist="MOUSE_BTN0 quit" --fullscreen splash.mp4
```

### Issue: All videos exit on touch (NOT DESIRED)

**Cause**: Legacy persistent configuration still exists

**Solution**:
```bash
# Check for config file
ls -la ~/.config/mpv/input.conf

# Remove it
rm -f ~/.config/mpv/input.conf

# Verify removal
cat ~/.config/mpv/input.conf
# Should show: No such file or directory
```

---

## 📋 Deployment Checklist

- [ ] MPV installed: `which mpv` → /usr/bin/mpv
- [ ] Legacy config removed: `rm -f ~/.config/mpv/input.conf`
- [ ] Test splash: Touch exits video
- [ ] Test training video: Touch does NOT exit
- [ ] Documented for operations team
- [ ] Team understands runtime vs persistent config

---

## 🎓 Key Concept

### Persistent Configuration (BAD for this use case)

```bash
# In ~/.config/mpv/input.conf
MOUSE_BTN0 quit

# Problem: Affects EVERYTHING
mpv splash.mp4      # ← Exits on touch ✓
mpv training.mp4    # ← ALSO exits on touch ✗
mpv dashboard.mp4   # ← ALSO exits on touch ✗
```

### Runtime Configuration (GOOD!)

```bash
# Splash video
mpv --input-cmdlist="MOUSE_BTN0 quit" splash.mp4  # ← Exits on touch ✓

# Training video (different command)
mpv training.mp4  # ← Normal behavior ✓

# Dashboard video
mpv dashboard.mp4  # ← Normal behavior ✓
```

**Each MPV invocation has isolated behavior!**

---

## 🎉 Benefits Summary

✅ **Zero system modification**
✅ **Isolated behavior per video**
✅ **Production safe**
✅ **Easy rollback** (just change command)
✅ **Predictable** (config visible in code)
✅ **Maintainable** (no hidden files)
✅ **Operational compliance**

---

*Engineering Pattern: Runtime Configuration > Persistent Configuration*
