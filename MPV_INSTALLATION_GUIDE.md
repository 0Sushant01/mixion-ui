# MPV Installation Guide for Raspberry Pi

**Quick Fix for `OSError: Cannot find libmpv`**

---

## 🔴 The Error

```
OSError: Cannot find libmpv in the usual places. Depending on your distro, 
you may try installing an mpv-devel or mpv-libs package.
```

---

## ✅ Solution (Raspberry Pi / Ubuntu / Debian)

### Step 1: Install System MPV Libraries

```bash
sudo apt-get update
sudo apt-get install mpv libmpv-dev
```

**What this installs:**
- `mpv` - The MPV media player application
- `libmpv-dev` - Development libraries that python-mpv needs

### Step 2: Verify MPV Installation

```bash
mpv --version
```

Expected output:
```
mpv 0.x.x Copyright © 2000-2024 mpv/MPlayer/mplayer2 projects
...
```

### Step 3: Reinstall python-mpv (if already installed)

```bash
# Activate your virtual environment first
source venv/bin/activate

# Reinstall python-mpv
pip install --upgrade python-mpv
```

### Step 4: Test Python Import

```bash
python -c "import mpv; print('MPV OK')"
```

Expected output:
```
MPV OK
```

---

## 🍓 Raspberry Pi Specific Notes

### Recommended Installation Order

1. **Update system** (important!)
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

2. **Install MPV system package**
   ```bash
   sudo apt-get install mpv libmpv-dev
   ```

3. **Create/activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. **Install Python packages**
   ```bash
   pip install -r requirements.txt
   ```

5. **Test application**
   ```bash
   python app.py
   ```

---

## 🔍 Troubleshooting

### Issue: `libmpv.so.1: cannot open shared object file`

**Solution**: Install libmpv1 package
```bash
sudo apt-get install libmpv1
```

### Issue: MPV version too old

Check version:
```bash
apt-cache policy mpv
```

If version is < 0.29.0, you may need to add backports:
```bash
sudo apt-get install -t buster-backports mpv libmpv-dev
```

### Issue: Still getting OSError after installation

Try adding library path:
```bash
export LD_LIBRARY_PATH=/usr/lib/arm-linux-gnueabihf:$LD_LIBRARY_PATH
```

Or find where libmpv is installed:
```bash
find /usr -name "libmpv.so*"
```

### Issue: Permission denied errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
which python  # Should show path inside venv
```

---

## 🖥️ Other Linux Distributions

### Ubuntu / Debian
```bash
sudo apt-get install mpv libmpv-dev
```

### Fedora / CentOS / RHEL
```bash
sudo dnf install mpv mpv-libs-devel
```

### Arch Linux
```bash
sudo pacman -S mpv
```

---

## 🍎 macOS

```bash
brew install mpv
pip install python-mpv
```

---

## 🪟 Windows

1. Download MPV from https://mpv.io/installation/
2. Extract to `C:\mpv`
3. Add `C:\mpv` to system PATH
4. Install python package:
   ```powershell
   pip install python-mpv
   ```

---

## ✨ Verification

After successful installation, your app should start without errors:

```bash
(venv) mixion@raspberrypi:~/phase1/mixion-ui $ python app.py
MPV initialized: assets/video/promo.mp4
Video playback started
Database initialized
MQTT connected to 192.168.1.100:1883
Application started successfully
```

---

## 📚 Additional Resources

- **MPV Official Site**: https://mpv.io/
- **python-mpv PyPI**: https://pypi.org/project/python-mpv/
- **MPV Manual**: https://mpv.io/manual/stable/
- **Raspberry Pi Forums**: https://forums.raspberrypi.com/

---

## 🆘 Still Having Issues?

1. Check system architecture:
   ```bash
   uname -m  # Should show armv7l or aarch64 for Raspberry Pi
   ```

2. Check if MPV binary exists:
   ```bash
   which mpv
   ls -la /usr/bin/mpv
   ```

3. Check if libmpv library exists:
   ```bash
   ldconfig -p | grep mpv
   ```

4. Check Python version compatibility:
   ```bash
   python --version  # Should be 3.9+
   ```

5. Try running app without video:
   - Comment out video playback temporarily
   - Or add a video file to skip splash screen

---

*Last Updated: February 16, 2026*
