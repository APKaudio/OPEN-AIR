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

import tkinter as tk
from tkinter import ttk
import os
import sys
import pathlib

# --- Path Setup ---
# This defines the absolute, true root path of the project, irrespective of the CWD.
SPLASH_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

# Assuming sys.path is already set up by main.py

# Import necessary libraries
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False

# Import lyrics data from a dedicated file
try:
    from workers.splash import lyrics_data
    LYRICS_AVAILABLE = True
except ImportError:
    lyrics_data = None
    LYRICS_AVAILABLE = False
    # This error might occur if lyrics_data.py is missing or has syntax errors.

class SplashScreen:
    def __init__(self, parent, app_version, debug_enabled, console_log_func, debug_log_func):
        if debug_enabled:
            debug_log_func(
                message="DEBUG: Entering SplashScreen.__init__().",
                file=os.path.basename(__file__), # Use os.path.basename(__file__) as current_file
                version=app_version,
                function=f"{self.__class__.__name__}.__init__",
                console_print_func=console_log_func
            )
        
        self.parent = parent
        self.app_version = app_version
        self.debug_enabled = debug_enabled
        self.console_log_func = console_log_func
        self.debug_log_func = debug_log_func
        self.splash_window = tk.Toplevel(self.parent)
        self.splash_window.overrideredirect(True) # Remove window decorations
        self.splash_window.attributes('-alpha', 0.0) # Start fully transparent

        self.splash_image = None
        image_path = None # Initialize image_path to avoid UnboundLocalError
        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(SPLASH_ROOT_DIR, 'workers', 'splash', 'OPEN AIR LOGO.png')
                pil_image = Image.open(image_path)
                self.splash_image = ImageTk.PhotoImage(pil_image)
            except Exception as e:
                if self.debug_enabled:
                    self.debug_log_func(
                        message=f"Splash screen error: Could not load image '{image_path}'. {e}",
                        file=os.path.basename(__file__),
                        version=self.app_version,
                        function=f"{self.__class__.__name__}.__init__", # Logging from __init__
                        console_print_func=self.console_log_func
                    )
                self.splash_image = None
        
        # Frame for the main content (image or text)
        self.main_content_frame = tk.Frame(self.splash_window, bd=0)
        self.main_content_frame.pack(expand=True, fill=tk.BOTH)

        # Widgets and sizing based on image availability
        if self.splash_image:
            label = tk.Label(self.main_content_frame, image=self.splash_image, bd=0)
            label.image = self.splash_image # Keep a reference!
            label.pack()
            img_width = self.splash_image.width()
            img_height = self.splash_image.height()
        else:
            # Fallback text label if image not loaded
            label = tk.Label(self.main_content_frame, text="OPEN-AIR", font=("Helvetica", 24, "bold"), fg="white", bg="black")
            label.pack(expand=True, fill=tk.BOTH)
            # Use a default size for text-only splash
            img_width = 400 
            img_height = 200
            self.splash_window.config(bg="black") # Set background for text label if no image

        status_bar_height = 30 
        # Adjust total height calculation based on layout; ensure it accommodates all elements.
        # Assuming main content height is img_height for this calculation.
        total_height = img_height + status_bar_height 

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = (screen_width // 2) - (img_width // 2)
        y = (screen_height // 2) - (total_height // 2)
        self.splash_window.geometry(f'{img_width}x{total_height}+{x}+{y}')

        # Frame for the status bar at the bottom
        status_bar_frame = tk.Frame(self.splash_window, height=status_bar_height, bg="black")
        status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Lyrics Label at the top
        self.lyrics_label = tk.Label(self.splash_window, text="", fg="gray", bg="black", font=("Helvetica", 9, "italic"))
        self.lyrics_label.pack(side=tk.TOP, fill=tk.X, pady=5) # Position lyrics at the top

        # Status Message Label within the status bar frame
        self.status_label = tk.Label(status_bar_frame, text="", fg="white", bg="black", font=("Helvetica", 10))
        self.status_label.pack(fill=tk.X, side=tk.LEFT, padx=10) # Align status to left within its frame

        # Load lyrics from dedicated file and handle potential loading issues robustly
        self.lyrics = [] # Initialize as empty list
        if LYRICS_AVAILABLE:
            try:
                # Check if lyrics_data is a module and has a 'lyrics' attribute which is a list
                if hasattr(lyrics_data, 'lyrics') and isinstance(lyrics_data.lyrics, list):
                    self.lyrics = lyrics_data.lyrics
                # Check if the imported object 'lyrics_data' itself is a list
                elif isinstance(lyrics_data, list):
                    self.lyrics = lyrics_data
                else:
                    # Module imported, but doesn't contain a list attribute named 'lyrics' or is not a list
                    if self.debug_enabled:
                        self.debug_log_func(
                            message="WARNING: Imported lyrics data is neither a list nor a module with a 'lyrics' attribute.",
                            file=os.path.basename(__file__),
                            version=self.app_version,
                            function=f"{self.__class__.__name__}.__init__",
                            console_print_func=self.console_log_func
                        )
                    self.lyrics = [] # Ensure it's an empty list
            except Exception as e:
                if self.debug_enabled:
                    self.debug_log_func(
                        message=f"🔴 ERROR loading lyrics data: {e}",
                        file=os.path.basename(__file__),
                        version=self.app_version,
                        function=f"{self.__class__.__name__}.__init__",
                        console_print_func=self.console_log_func
                    )
                self.lyrics = [] # Fallback to empty list on error
        else:
            # If import failed (LYRICS_AVAILABLE is False)
            if self.debug_enabled:
                self.debug_log_func(
                    message="WARNING: Could not import lyrics module.",
                    file=os.path.basename(__file__),
                    version=self.app_version,
                    function=f"{self.__class__.__name__}.__init__",
                    console_print_func=self.console_log_func
                )
            self.lyrics = [] # Ensure lyrics is an empty list

        self.lyric_index = 0
        # Initialize current_lyric safely, handling empty lyrics list
        if self.lyrics:
            self.current_lyric = self.lyrics[self.lyric_index % len(self.lyrics)]
        else:
            self.current_lyric = "" # Default if no lyrics are loaded
            if self.debug_enabled:
                self.debug_log_func(
                    message="WARNING: Lyrics list is empty. Splash screen might not show lyrics.",
                    file=os.path.basename(__file__),
                    version=self.app_version,
                    function=f"{self.__class__.__name__}.__init__",
                    console_print_func=self    .console_log_func
                )
        
        self.lyrics_label.config(text=self.current_lyric)
        self.status_message = "Initializing..."
        
        # Set initial status and lyric by calling set_status to ensure both are updated
        self.set_status(self.status_message) 

        # Fading animation uses self.parent.after directly, avoiding lambdas.
        self.parent.after(10, self._fade_in)
        self.splash_window.after(5000, self.cycle_lyrics_async)

        if debug_enabled:
            debug_log_func(
                message="DEBUG: Exiting SplashScreen.__init__().",
                file=os.path.basename(__file__),
                version=self.app_version,
                function=f"{self.__class__.__name__}.__init__",
                console_print_func=console_log_func
            )

    def _fade_in(self, alpha=0.0):
        if self.splash_window.winfo_exists():
            if alpha <= 1.0:
                self.splash_window.attributes('-alpha', alpha)
                # Use self.parent.after directly with arguments, avoiding lambdas.
                self.parent.after(20, self._fade_in, alpha + 0.05)

    def hide(self):
        if self.splash_window.winfo_exists():
            self._fade_out()

    def _fade_out(self, alpha=1.0):
        if self.splash_window.winfo_exists():
            if alpha >= 0.0:
                self.splash_window.attributes('-alpha', alpha)
                # Use self.parent.after directly with arguments, avoiding lambdas.
                self.parent.after(20, self._fade_out, alpha - 0.05)
            else:
                self.splash_window.destroy()

    def set_status(self, message):
        """
        Updates the status message.
        """
        if self.splash_window.winfo_exists():
            self.status_message = message
            self.status_label.config(text=f"{self.status_message}") # Only status message in status bar
            self.parent.update_idletasks() # Ensure UI updates immediately

    def cycle_lyrics_async(self):
        """
        Asynchronously cycles through the lyrics and updates the lyrics_label.
        """
        if self.splash_window.winfo_exists() and self.lyrics:
            self.lyric_index = (self.lyric_index + 1) % len(self.lyrics)
            self.current_lyric = self.lyrics[self.lyric_index]
            self.lyrics_label.config(text=self.current_lyric)
            self.debug_log_func(
                message=f"Lyric changed to: {self.current_lyric}",
                file=os.path.basename(__file__),
                version=self.app_version,
                function=f"{self.__class__.__name__}.cycle_lyrics_async",
                console_print_func=self.console_log_func
            )
            self.splash_window.after(5000, self.cycle_lyrics_async) # Cycle every 5 seconds (5000ms)

if __name__ == '__main__':
    # For testing the splash screen directly
    root = tk.Tk()
    root.withdraw() # Hide the main root window

    # Dummy values for testing
    app_version_val = "20251215.120000.58"
    debug_enabled_val = True
    # Dummy logger functions
    def dummy_debug_log(*args, **kwargs): print(f"DEBUG: {kwargs.get('message')}")
    def dummy_console_log(*args, **kwargs): print(f"CONSOLE: {kwargs.get('message')}")

    # Pass necessary arguments to SplashScreen constructor
    splash = SplashScreen(root, app_version=app_version_val, debug_enabled=debug_enabled_val, console_log_func=dummy_console_log, debug_log_func=dummy_debug_log)
    
    # Simulate some work by calling set_status multiple times
    splash.set_status("Loading core modules...")
    # In a real app, this would be actual initialization steps.
    # time.sleep is blocking and should not be used in the actual app's main thread.
    # For testing, we use root.after to simulate work without blocking the event loop.
    
    root.after(1000, lambda: splash.set_status("Initializing GUI components..."))
    root.after(2000, lambda: splash.set_status("Connecting to services..."))
    root.after(3000, lambda: splash.set_status("All systems go!"))
    
    # Hide splash screen after simulated work
    root.after(4000, splash.hide)
    
    # Ensure the main window is set up if needed, or just end the demo
    root.after(4500, root.destroy) # Destroy root after splash closes
    root.mainloop()
    dummy_console_log("Main thread exiting.")
