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
        
        self._safe_log(f"🖥️🟢 Entering SplashScreen.__init__", force_print=True)

        self.parent = parent
        self.app_version = app_version
        
        self.gif_frames = []
        self.gif_frame_index = 0
        self.gif_animation_job = None
        self.status_label = None # Initialize to None

        try:
            self.splash_window = tk.Toplevel(self.parent)
            self.splash_window.overrideredirect(True)
            self.splash_window.attributes('-alpha', 0.0)
            self.splash_window.configure(bg='black')
            
            # --- Dimensions & Centering ---
            win_width, win_height = 600, 400
            self.splash_window.geometry(f'{win_width}x{win_height}')
            self.splash_window.tk.call('tk::PlaceWindow', str(self.splash_window), 'center')
            
            # --- GIF Background ---
            self.gif_label = tk.Label(self.splash_window, bg="black")
            self.gif_label.place(x=0, y=0, relwidth=1, relheight=1)

            if PIL_AVAILABLE:
                self._safe_log("Initializing GIF Animation...")
                try:
                    self._init_gif_animation()
                except Exception as e:
                    self._safe_log(f"🔴 GIF FAILED: {e}", is_error=True)
                    traceback.print_exc()
                    tk.Label(self.splash_window, text="[GIF Error]", fg="red", bg="black").place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            else:
                tk.Label(self.splash_window, text="[Image Libraries Missing]", fg="#333", bg="black").place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            # --- Widgets on top of the GIF ---
            header_frame = tk.Frame(self.splash_window, bg="black")
            header_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

            tk.Label(header_frame, text="Open ", font=("Helvetica", 36, "normal"), fg="#FF6B35", bg="black").pack(side=tk.LEFT)
            tk.Label(header_frame, text="Air", font=("Helvetica", 36, "bold"), fg="#33A1FD", bg="black").pack(side=tk.LEFT)

            self.lyrics_label = tk.Label(self.splash_window, text="", fg="gray", bg="black", font=("Helvetica", 10, "italic"))
            self.lyrics_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

            tk.Label(self.splash_window, text="Zone Awareness Processor", font=("Helvetica", 14), fg="white", bg="black").place(relx=0.5, rely=0.8, anchor=tk.CENTER)
            
            self.status_label = tk.Label(self.splash_window, text="Initializing...", fg="white", bg="black", font=("Helvetica", 10))
            self.status_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

            # --- Data & Logic ---
            self.lyrics = []
            if LYRICS_AVAILABLE and hasattr(lyrics_data, 'lyrics'):
                self.lyrics = lyrics_data.lyrics
            if not self.lyrics: self.lyrics = ["...Loading..."]
            
            self.lyric_index = 0
            self.current_lyric = self.lyrics[0]
            self.lyrics_label.config(text=self.current_lyric)

            # --- Start Timers ---
            self.parent.after(10, self._fade_in)
            self.parent.after(1500, self.cycle_lyrics_async)
            
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

    def _init_gif_animation(self):
        self.photo_images = []
        gif_path = pathlib.Path(__file__).parent / 'splash_logo.gif'
        if not gif_path.exists():
            self._safe_log(f"🔴 GIF not found at {gif_path}", is_error=True)
            return

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

        if self.photo_images:
            self._update_gif_frame()

    def _update_gif_frame(self):
        self._safe_log(f"Updating GIF frame to index {self.gif_frame_index}")
        if not self.splash_window.winfo_exists():
            return
            
        frame = self.photo_images[self.gif_frame_index]
        self.gif_label.config(image=frame)
        
        self.gif_frame_index = (self.gif_frame_index + 1) % len(self.photo_images)
        
        self.gif_animation_job = self.parent.after(self.gif_frame_duration, self._update_gif_frame)

    def _fade_in(self, alpha=0.0):
        if self.splash_window.winfo_exists() and alpha <= 1.0:
            self.splash_window.attributes('-alpha', alpha)
            self.parent.after(20, self._fade_in, alpha + 0.05)

    def hide(self):
        try:
            if self.gif_animation_job:
                self.splash_window.after_cancel(self.gif_animation_job)
                self.gif_animation_job = None
        except Exception: pass
        
        if self.splash_window.winfo_exists():
            self._fade_out()

    def _fade_out(self, alpha=1.0):
        if self.splash_window.winfo_exists() and alpha >= 0.0:
            self.splash_window.attributes('-alpha', alpha)
            self.parent.after(20, self._fade_out, alpha - 0.05)
        elif self.splash_window.winfo_exists():
            self.splash_window.destroy()

    def set_status(self, message):
        if self.splash_window.winfo_exists() and self.status_label:
            self.status_label.config(text=message)
            self.parent.update_idletasks()

    def cycle_lyrics_async(self):
        if self.splash_window.winfo_exists() and self.lyrics:
            self.lyric_index = (self.lyric_index + 1) % len(self.lyrics)
            self.current_lyric = self.lyrics[self.lyric_index]
            self.lyrics_label.config(text=self.current_lyric)
            self.parent.after(1500, self.cycle_lyrics_async)

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
