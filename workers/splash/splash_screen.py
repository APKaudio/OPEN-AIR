# display/splash/splash_screen.py
#
# This file (splash_screen.py) provides the SplashScreen class for displaying a customizable splash screen on application startup.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

import workers.setup.app_constants as app_constants

# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20251222.005500.3

import tkinter as tk
from tkinter import ttk
import os
import sys
import pathlib

# --- Global Scope Variables ---
Current_Date = 20251222
Current_Time = 5500
Current_iteration = 3 # Incremented version

current_version = "20251222.005500.3"
current_version_hash = (Current_Date * Current_Time * Current_iteration)
current_file = os.path.basename(__file__)

# --- Path Setup ---
SPLASH_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

# Import necessary libraries
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False

# Import lyrics data from the same directory
try:
    from . import lyrics_data
    LYRICS_AVAILABLE = True
except ImportError:
    lyrics_data = None
    LYRICS_AVAILABLE = False

class SplashScreen:
    def __init__(self, parent, app_version, debug_enabled, _func, debug_log_func):
        current_function_name = "__init__"
        self.debug_enabled = debug_enabled
        self._func = _func
        self.debug_log_func = debug_log_func
        
        if self.debug_enabled:
            self.debug_log_func(
                message=f"🖥️🟢 Entering '{current_function_name}'. The splash screen experiment begins!",
                file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}"
                
            )
        
        self.parent = parent
        self.app_version = app_version
        
        self.splash_window = tk.Toplevel(self.parent)
        self.splash_window.overrideredirect(True)
        self.splash_window.attributes('-alpha', 0.0)

        # --- Image Loading ---
        self.splash_image = None
        img_width, img_height = 400, 200 # Default size
        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(SPLASH_ROOT_DIR, 'workers', 'splash', 'OPEN AIR LOGO.png')
                pil_image = Image.open(image_path)
                self.splash_image = ImageTk.PhotoImage(pil_image)
                img_width, img_height = self.splash_image.width(), self.splash_image.height()
            except Exception as e:
                if self.debug_enabled:
                    self.debug_log_func(message=f"🔴 ERROR: Could not load splash image. {e}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}" )
                self.splash_image = None
        
        # --- Window Centering ---
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = (screen_width // 2) - (img_width // 2)
        y = (screen_height // 2) - (img_height // 2)
        self.splash_window.geometry(f'{img_width}x{img_height}+{x}+{y}')
        
        # --- Main Frame & Layout ---
        self.main_content_frame = tk.Frame(self.splash_window, bg="black")
        self.main_content_frame.pack(expand=True, fill=tk.BOTH)

        # Logo or Fallback Text
        if self.splash_image:
            logo_label = tk.Label(self.main_content_frame, image=self.splash_image, bg="black", bd=0)
            logo_label.image = self.splash_image
            logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            tk.Label(self.main_content_frame, text="OPEN-AIR", font=("Helvetica", 24, "bold"), fg="white", bg="black").place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Lyrics Label
        self.lyrics_label = tk.Label(self.main_content_frame, text="", fg="gray", bg="black", font=("Helvetica", 9, "italic"))
        self.lyrics_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Status Label (Centered below logo)
        self.status_label = tk.Label(self.main_content_frame, text="", fg="white", bg="black", font=("Helvetica", 10))
        self.status_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # --- Lyrics Loading Logic ---
        self.lyrics = []
        if LYRICS_AVAILABLE and hasattr(lyrics_data, 'lyrics'):
            self.lyrics = lyrics_data.lyrics
        
        # If lyrics are still not loaded, populate with a diagnostic message.
        if not self.lyrics:
            self.lyrics = ["[LYRICS FAILED TO LOAD]"]
            if self.debug_enabled:
                self.debug_log_func(
                    message="🔴 CRITICAL: Lyrics array is empty after attempting to load. Displaying error on screen.",
                    file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}"
                    
                )

        self.lyric_index = 0
        self.current_lyric = self.lyrics[0]
        self.lyrics_label.config(text=self.current_lyric)
        self.set_status("Initializing...")

        # --- Start Animations ---
        self.parent.after(10, self._fade_in)
        self.splash_window.after(1500, self.cycle_lyrics_async)

        if self.debug_enabled:
            self.debug_log_func(message="✅ Exiting SplashScreen.__init__().", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}" )

    def _fade_in(self, alpha=0.0):
        if self.splash_window.winfo_exists() and alpha <= 1.0:
            self.splash_window.attributes('-alpha', alpha)
            self.parent.after(20, self._fade_in, alpha + 0.05)

    def hide(self):
        if self.splash_window.winfo_exists():
            self._fade_out()

    def _fade_out(self, alpha=1.0):
        if self.splash_window.winfo_exists() and alpha >= 0.0:
            self.splash_window.attributes('-alpha', alpha)
            self.parent.after(20, self._fade_out, alpha - 0.05)
        elif self.splash_window.winfo_exists():
            self.splash_window.destroy()

    def set_status(self, message):
        if self.splash_window.winfo_exists():
            self.status_label.config(text=message)
            self.parent.update_idletasks()

    def cycle_lyrics_async(self):
        current_function_name = "cycle_lyrics_async"
        if self.splash_window.winfo_exists() and self.lyrics:
            self.lyric_index = (self.lyric_index + 1) % len(self.lyrics)
            self.current_lyric = self.lyrics[self.lyric_index]
            self.lyrics_label.config(text=self.current_lyric)
            if self.debug_enabled:
                self.debug_log_func(
                    message=f"🎶 Lyric changed to: {self.current_lyric}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}"
                    
                )
            self.splash_window.after(1500, self.cycle_lyrics_async)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    