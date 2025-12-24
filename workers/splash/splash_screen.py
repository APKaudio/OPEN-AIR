# display/splash/splash_screen.py
# Version 20251223.GIF.Integration
#
# UPDATES:
# 1. Removed Matplotlib/Numpy animation to reduce overhead and potential driver conflicts.
# 2. Replaced dynamic animation with a pre-rendered GIF ('splash_logo.gif') using Pillow.
# 3. Text rendering, versioning, and status updates remain unchanged.

import workers.setup.app_constants as app_constants
import tkinter as tk
from tkinter import ttk
import os
import sys
import pathlib
import traceback

# --- Image Library Imports ---
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow (PIL) not found. GIF animation will be disabled.")

from workers.utils.log_utils import _get_log_args 

# --- Path Setup ---
SPLASH_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

# Import lyrics data
try:
    from . import lyrics_data
    LYRICS_AVAILABLE = True
except ImportError:
    lyrics_data = None
    LYRICS_AVAILABLE = False

class SplashScreen:
    def __init__(self, parent, app_version, debug_enabled, _func, debug_log_func):
        self.debug_enabled = debug_enabled
        self._func = _func
        self.debug_log_func = debug_log_func
        
        self._safe_log(f"🖥️🟢 Entering SplashScreen.__init__") # Removed force_print=True

        self.parent = parent
        self.app_version = app_version
        
        self.gif_frames = []
        self.gif_frame_index = 0
        self.gif_animation_job = None
        self.status_label = None # Initialize to None

        try:
            self.splash_window = tk.Toplevel(self.parent)
            self.splash_window.overrideredirect(True)
            self.splash_window.attributes('-alpha', 1.0) # Always full opacity
            self.splash_window.configure(bg='black')
            self.parent.protocol("WM_DELETE_WINDOW", self.hide) # Add this line
            
            # --- Dimensions & Centering ---
            win_width, win_height = 600, 500
            screen_width = self.parent.winfo_screenwidth()
            screen_height = self.parent.winfo_screenheight()
            x = (screen_width // 2) - (win_width // 2)
            y = (screen_height // 2) - (win_height // 2) + 500
            self.splash_window.geometry(f'{win_width}x{win_height}+{x}+{y}')
            
            self.main_content_frame = tk.Frame(self.splash_window, bg="black")
            self.main_content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

            # --- 1. Header ---
            header_frame = tk.Frame(self.main_content_frame, bg="black")
            header_frame.pack(side=tk.TOP, pady=(10, 5)) 

            tk.Label(header_frame, text="Open ", font=("Helvetica", 36, "normal"), fg="#FF6B35", bg="black").pack(side=tk.LEFT)
            tk.Label(header_frame, text="Air", font=("Helvetica", 36, "bold"), fg="#33A1FD", bg="black").pack(side=tk.LEFT)

            # --- 2. Sub-header ---
            tk.Label(self.main_content_frame, text="Zone Awareness Processor", font=("Helvetica", 14), fg="white", bg="black").pack(side=tk.TOP, pady=(5, 10))
            
            self.status_label = tk.Label(self.main_content_frame, text="Initializing...", fg="white", bg="black", font=("Helvetica", 10))
            self.status_label.pack(side=tk.TOP, pady=5)

            # --- 3. Animation Area (Now a GIF) ---
            vis_frame = tk.Frame(self.main_content_frame, bg="black", height=250)
            vis_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=10)
            vis_frame.pack_propagate(False)

            if PIL_AVAILABLE:
                self._safe_log("Initializing GIF Animation...")
                try:
                    self._init_gif_animation(vis_frame)
                except Exception as e:
                    self._safe_log(f"🔴 GIF FAILED: {e}", is_error=True)
                    traceback.print_exc()
                    tk.Label(vis_frame, text="[GIF Error]", fg="red", bg="black").pack(expand=True)
            else:
                tk.Label(vis_frame, text="[Image Libraries Missing]", fg="#333", bg="black").pack(expand=True)

            # --- 4. Lyrics ---
            self.lyrics_label = tk.Label(self.main_content_frame, text="", fg="gray", bg="black", font=("Helvetica", 10, "italic"))
            self.lyrics_label.pack(side=tk.BOTTOM, pady=(10, 0))

            # --- Data & Logic ---
            self.lyrics = []
            if LYRICS_AVAILABLE and hasattr(lyrics_data, 'lyrics'):
                self.lyrics = lyrics_data.lyrics
            if not self.lyrics: self.lyrics = ["...Loading..."]
            
            self.lyric_index = 0
            self.current_lyric = self.lyrics[0]
            self.lyrics_label.config(text=self.current_lyric)

            # --- No fade-in, start animation directly ---
            if self.photo_images:
                self._update_gif_frame() # Start GIF immediately
            
            self._safe_log("✅ SplashScreen Init Complete.")

        except Exception as e:
            self._safe_log(f"🔴 CRITICAL SPLASH ERROR: {e}", is_error=True)
            traceback.print_exc()

    def _safe_log(self, message, is_error=False, force_print=False):
        if is_error or force_print or self.debug_enabled:
            print(f"[SPLASH_DEBUG] {message}")
        try:
            if self.debug_enabled and self.debug_log_func:
                self.debug_log_func(message=message, **_get_log_args())
        except Exception: pass

    def _init_gif_animation(self, parent_frame):
        self.photo_images = []
        gif_path = pathlib.Path(__file__).parent / 'splash_logo.gif'
        if not gif_path.exists():
            self._safe_log(f"🔴 GIF not found at {gif_path}", is_error=True)
            tk.Label(parent_frame, text="[splash_logo.gif not found]", fg="red", bg="black").pack(expand=True)
            return

        self.gif_label = tk.Label(parent_frame, bg="black")
        self.gif_label.pack(expand=True)

        try:
            with Image.open(gif_path) as img:
                for i in range(img.n_frames):
                    img.seek(i)
                    frame_image = img.copy().convert("RGBA")
                    photo_image = ImageTk.PhotoImage(frame_image)
                    self.photo_images.append(photo_image)
                
                self.gif_frame_duration = img.info.get('duration', 50)
                # FIX: Keep a reference to the images on the label itself
                self.gif_label.photo_images = self.photo_images

        except Exception as e:
            self._safe_log(f"🔴 Failed to load GIF frames: {e}", is_error=True)

    def _update_gif_frame(self):
        self._safe_log(f"Updating GIF frame to index {self.gif_frame_index}")
        if not self.splash_window.winfo_exists():
            return
            
        frame = self.photo_images[self.gif_frame_index]
        self.gif_label.config(image=frame)
        
        self.gif_frame_index = (self.gif_frame_index + 1) % len(self.photo_images)
        
        self.gif_animation_job = self.splash_window.after(self.gif_frame_duration, self._update_gif_frame)

    # _fade_in and _fade_out methods removed
    
    def hide(self):
        # Ensure splash_window still exists before trying to interact with it
        if self.splash_window and self.splash_window.winfo_exists():
            try:
                if self.gif_animation_job:
                    self.splash_window.after_cancel(self.gif_animation_job)
                    self.gif_animation_job = None
            except Exception: pass # Ignore errors if job already cancelled or window destroyed
            
            self.splash_window.destroy() # Destroy the splash window directly
            self.splash_window = None # Clear the reference

    def set_status(self, message):
        if self.splash_window.winfo_exists() and self.status_label:
            self.status_label.config(text=message)
            self.parent.update_idletasks()

    def cycle_lyrics_async(self):
        # This method is no longer called in init, but kept for potential future use or direct invocation
        if self.splash_window.winfo_exists() and self.lyrics:
            self.lyric_index = (self.lyric_index + 1) % len(self.lyrics)
            self.current_lyric = self.lyrics[self.lyric_index]
            self.lyrics_label.config(text=self.current_lyric)
            self.splash_window.after(1500, self.cycle_lyrics_async)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    print("Starting Standalone Test...")
    
    def mock_debug_log(message, **kwargs):
        print(f"[DEBUG] {message}")

    splash = SplashScreen(root, "TestVer", True, lambda: None, mock_debug_log)
    
    # Close after 10 seconds for testing
    root.after(10000, splash.hide)
    
    root.mainloop()
