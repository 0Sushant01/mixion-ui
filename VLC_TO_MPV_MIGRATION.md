# VLC to MPV Migration

**Date**: February 16, 2026  
**Status**: ✅ Complete

---

## 🔄 Overview

Successfully migrated video playback from **VLC** to **MPV** media player across the entire Mixion project.

---

## 📝 Changes Made

### 1. **Code Changes**

#### [requirements.txt](requirements.txt)
- ❌ Removed: `python-vlc>=3.0.16120`
- ✅ Added: `python-mpv>=1.0.1`

#### [src/screens/splash_screen.py](src/screens/splash_screen.py)
Complete rewrite of video playback implementation:

**Before (VLC)**:
```python
import vlc
VLC_AVAILABLE = True

self.instance = vlc.Instance('--no-xlib --avcodec-hw=none --no-hw-decoding')
self.player = self.instance.media_player_new()
media = self.instance.media_new(self.video_path)
media.add_option('input-repeat=65535')
self.player.set_media(media)
self.player.play()
```

**After (MPV)**:
```python
import mpv
MPV_AVAILABLE = True

self.player = mpv.MPV(
    wid=str(self.video_frame.winfo_id()),
    loop='inf',
    vo='x11' if platform.system() == 'Linux' else 'gpu',
    keep_open='yes',
    input_default_bindings=False,
    input_vo_keyboard=False,
    osc=False
)
self.player.play(video_abs_path)
```

**Key Improvements**:
- Simpler API - fewer lines of code
- Automatic looping with `loop='inf'`
- Better cross-platform support
- No separate instance/media/player objects
- Direct `play()` method

---

### 2. **Documentation Updates**

Updated all references from VLC to MPV in:

#### Core Documentation
- ✅ [README.md](README.md)
  - Requirements section
  - Installation instructions
  - Troubleshooting guide
  
- ✅ [DEPENDENCIES.md](DEPENDENCIES.md)
  - Complete framework documentation
  - Installation guide
  - System requirements
  - Technology stack table
  - Troubleshooting section

- ✅ [SETUP.md](SETUP.md)
  - Installation steps
  - Troubleshooting

- ✅ [QUICKSTART.md](QUICKSTART.md)
  - Quick setup guide
  - Installation checklist

#### Testing Documentation
- ✅ [TESTING_WITH_SIMULATOR.md](TESTING_WITH_SIMULATOR.md)
- ✅ [LAUNCH_MODES.md](LAUNCH_MODES.md)
- ✅ [TEST_MODE_SUMMARY.md](TEST_MODE_SUMMARY.md)

#### Other Documentation
- ✅ [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
- ✅ [test_system.py](test_system.py) - System diagnostics

---

## 🎯 Why MPV?

### Advantages over VLC

1. **Simpler API**
   - Less boilerplate code
   - Cleaner implementation
   - Easier to maintain

2. **Better Performance**
   - Lower resource usage
   - Faster startup time
   - More efficient video decoding

3. **Modern Architecture**
   - Active development
   - Better hardware acceleration
   - Improved codec support

4. **Python Integration**
   - More Pythonic API
   - Better property access
   - Cleaner error handling

5. **Cross-Platform**
   - Consistent behavior across OS
   - Better Linux support
   - Simpler configuration

---

## 📦 Installation

### 1. Install MPV Media Player

**Windows**:
```powershell
# Download from https://mpv.io/installation/
# Or use Chocolatey:
choco install mpv
```

**Linux (Raspberry Pi/Ubuntu)**:
```bash
sudo apt-get update
sudo apt-get install mpv
```

**macOS**:
```bash
brew install mpv
```

### 2. Install Python Package

```bash
pip install python-mpv
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "import mpv; print('MPV OK')"
```

---

## 🔍 Testing

### Test Video Playback

```bash
# Run full application
python app.py

# Or test mode with simulator
python test.py
```

**Expected Output**:
```
MPV initialized: assets/video/promo.mp4
Video playback started
```

### Fallback Behavior

If MPV is not installed, the application will:
1. Display warning message: `"Warning: python-mpv not installed. Video playback disabled."`
2. Show error screen with instructions
3. Allow user to tap to continue to menu
4. Continue functioning normally (video is optional)

---

## 🔧 Configuration

No configuration changes needed! MPV uses the same video file path from [config.py](config.py):

```python
SPLASH_VIDEO = "assets/video/promo.mp4"
```

---

## 🚨 Breaking Changes

### For Users

**Action Required**:
1. Uninstall VLC (optional, but recommended to save space)
2. Install MPV media player
3. Reinstall dependencies: `pip install -r requirements.txt`

### For Developers

**Code Changes**:
- `import vlc` → `import mpv`
- `VLC_AVAILABLE` → `MPV_AVAILABLE`
- Different initialization API (see code examples above)

---

## 📊 Comparison

| Feature | VLC | MPV |
|---------|-----|-----|
| **Code Complexity** | High (3 objects) | Low (1 object) |
| **API Simplicity** | Complex | Simple |
| **Performance** | Good | Excellent |
| **Resource Usage** | Higher | Lower |
| **Hardware Accel** | Limited | Better |
| **Cross-Platform** | Good | Excellent |
| **Python Integration** | Functional | Native |
| **File Size** | ~80MB | ~40MB |
| **Active Development** | Moderate | Very Active |

---

## 🧪 Code Examples

### Playing Video

**VLC (Old)**:
```python
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new("video.mp4")
player.set_media(media)
player.play()
```

**MPV (New)**:
```python
player = mpv.MPV()
player.play("video.mp4")
```

### Looping Video

**VLC (Old)**:
```python
media.add_option('input-repeat=65535')
```

**MPV (New)**:
```python
player = mpv.MPV(loop='inf')
```

### Stopping Video

**VLC (Old)**:
```python
player.stop()
```

**MPV (New)**:
```python
player.terminate()
```

---

## ⚠️ Known Issues

### None Currently

Migration is complete and tested. No known issues with MPV implementation.

### If Problems Occur

1. **Import Error**:
   ```bash
   pip install --upgrade python-mpv
   ```

2. **MPV Not Found**:
   - Ensure MPV media player is installed on system
   - Check PATH environment variable

3. **Video Not Playing**:
   - Verify video file exists: `assets/video/promo.mp4`
   - Check file permissions
   - Test MPV directly: `mpv assets/video/promo.mp4`

---

## 📚 Resources

- **MPV Official**: https://mpv.io/
- **python-mpv PyPI**: https://pypi.org/project/python-mpv/
- **MPV Manual**: https://mpv.io/manual/stable/
- **python-mpv GitHub**: https://github.com/jaseg/python-mpv

---

## ✅ Migration Checklist

- [x] Updated requirements.txt
- [x] Rewrote splash_screen.py
- [x] Updated README.md
- [x] Updated DEPENDENCIES.md
- [x] Updated SETUP.md
- [x] Updated QUICKSTART.md
- [x] Updated test documentation
- [x] Updated troubleshooting guides
- [x] Updated system diagnostics (test_system.py)
- [x] Verified no VLC references remain
- [x] Tested new implementation

---

## 🎉 Result

**Status**: ✅ **Migration Complete**

All VLC references have been replaced with MPV. The application is ready to use with the new video player.

---

*Last Updated: February 16, 2026*
