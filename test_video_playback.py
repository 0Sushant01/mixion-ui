#!/usr/bin/env python3
"""
Test MPV Video Playback
Diagnostic script to verify MPV and video file are working correctly
"""

import os
import sys
import tkinter as tk
from pathlib import Path

# Test 1: Check if MPV is installed
print("=" * 60)
print("TEST 1: Checking MPV Installation")
print("=" * 60)

try:
    import mpv
    print("✓ python-mpv package is installed")
    MPV_AVAILABLE = True
except ImportError as e:
    print("✗ python-mpv package NOT installed")
    print(f"  Error: {e}")
    print("  Install with: pip install python-mpv")
    MPV_AVAILABLE = False
except OSError as e:
    print("✗ libmpv system library NOT found")
    print(f"  Error: {e}")
    print("  Install with: sudo apt-get install mpv libmpv-dev")
    MPV_AVAILABLE = False

if not MPV_AVAILABLE:
    print("\nPlease install MPV before continuing.")
    sys.exit(1)

# Test 2: Check video file exists
print("\n" + "=" * 60)
print("TEST 2: Checking Video File")
print("=" * 60)

VIDEO_PATH = "assets/video/promo.mp4"
video_abs_path = os.path.abspath(VIDEO_PATH)

if os.path.exists(video_abs_path):
    print(f"✓ Video file found: {video_abs_path}")
    file_size = os.path.getsize(video_abs_path)
    print(f"  File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
else:
    print(f"✗ Video file NOT found: {video_abs_path}")
    print("\nPlease add a video file to assets/video/promo.mp4")
    
    # Try to find any video files
    assets_dir = Path("assets/video")
    if assets_dir.exists():
        video_files = list(assets_dir.glob("*.mp4")) + list(assets_dir.glob("*.avi")) + list(assets_dir.glob("*.mkv"))
        if video_files:
            print(f"\nFound other video files:")
            for vf in video_files:
                print(f"  - {vf}")
    sys.exit(1)

# Test 3: Try to create MPV instance
print("\n" + "=" * 60)
print("TEST 3: Creating MPV Player Instance")
print("=" * 60)

try:
    test_player = mpv.MPV(
        loop='inf',
        quiet=True,
        keep_open='yes'
    )
    print("✓ MPV player instance created successfully")
    
    # Try to load video
    print(f"\nLoading video: {video_abs_path}")
    test_player.play(video_abs_path)
    print("✓ Video loaded successfully")
    
    # Get video properties
    try:
        import time
        time.sleep(0.5)  # Wait for video to load
        
        if hasattr(test_player, 'width') and test_player.width:
            print(f"  Video resolution: {test_player.width}x{test_player.height}")
        if hasattr(test_player, 'duration') and test_player.duration:
            print(f"  Video duration: {test_player.duration:.2f} seconds")
    except:
        pass
    
    test_player.terminate()
    print("\n✓ All MPV tests passed!")
    
except Exception as e:
    print(f"✗ Error creating MPV player: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Tkinter canvas embedding test
print("\n" + "=" * 60)
print("TEST 4: Testing MPV with Tkinter Canvas")
print("=" * 60)
print("\nOpening window with video playback...")
print("Click anywhere on the screen to close the test window.")

class VideoTestWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MPV Video Playback Test")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            bg="black",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Add instruction text
        self.text = self.canvas.create_text(
            400, 550,
            text="⬆ CLICK ANYWHERE TO CLOSE TEST ⬆",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        
        # Bind click to close
        self.canvas.bind("<Button-1>", self.close)
        
        # Initialize video
        self.player = None
        self.init_video()
        
    def init_video(self):
        try:
            # Wait for canvas to be ready
            self.canvas.update_idletasks()
            canvas_wid = self.canvas.winfo_id()
            
            print(f"Canvas window ID: {canvas_wid}")
            
            # Create MPV player
            self.player = mpv.MPV(
                wid=str(canvas_wid),
                loop='inf',
                vo='x11',  # Force X11 output on Linux
                keep_open='yes',
                input_default_bindings=False,
                input_vo_keyboard=False,
                osc=False,
                quiet=True
            )
            
            # Load video
            self.player.play(video_abs_path)
            
            print("✓ Video embedded in canvas")
            print("If you see the video playing, MPV is working correctly!")
            
        except Exception as e:
            print(f"✗ Error embedding video: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error on canvas
            self.canvas.create_text(
                400, 300,
                text=f"Error: {str(e)}\n\nClick to close",
                font=("Arial", 14),
                fill="red",
                justify="center"
            )
    
    def close(self, event=None):
        print("\nClosing test window...")
        if self.player:
            try:
                self.player.terminate()
            except:
                pass
        self.root.destroy()
        print("✓ Test completed!")
    
    def run(self):
        self.root.mainloop()

# Run the test
try:
    app = VideoTestWindow()
    app.run()
except Exception as e:
    print(f"✗ Error running test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
