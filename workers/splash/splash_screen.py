# display/splash/splash_screen.py
#
# This file (splash_screen.py) provides the SplashScreen class for displaying a customizable splash screen on application startup.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251215  ##Update on the day the change was made
Current_Time = 200500  ## update at the time it was edited and compiled
Current_iteration = 3 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
from display.logger import debug_log, console_log, log_visa_command

# --- Global Scope Variables ---
current_version = "UNKNOWN_VERSION.000000.0" # Placeholder, update as needed
current_version_hash = 0
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
Local_Debug_Enable = True

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False
    if Local_Debug_Enable:
        debug_log(
            message="WARNING: Pillow (PIL) not available. Splash screen will not display image.",
            file=current_file,
            version=current_version,
            function="SplashScreen Module", # Module level function for logging
            console_print_func=console_log
        )

class SplashScreen:
    def __init__(self, parent):
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Entering SplashScreen.__init__().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.__init__",
                console_print_func=console_log
            )
        
        self.parent = parent
        self.splash_window = tk.Toplevel(self.parent)
        self.splash_window.overrideredirect(True)
        self.splash_window.attributes('-alpha', 0.0)

        self.splash_image = None
        image_path = None # Initialize image_path to avoid UnboundLocalError
        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(SPLASH_ROOT_DIR, 'display', 'splash', 'OPEN AIR LOGO.png')
                pil_image = Image.open(image_path)
                self.splash_image = ImageTk.PhotoImage(pil_image)
            except Exception as e:
                if Local_Debug_Enable:
                    debug_log(
                        message=f"Splash screen error: Could not load image '{image_path}'. {e}",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}._init_ui",
                        console_print_func=console_log
                    )
                self.splash_image = None
        
        # Widgets and sizing based on image availability
        if self.splash_image:
            label = tk.Label(self.splash_window, image=self.splash_image, bd=0)
            label.image = self.splash_image # Keep a reference!
            label.pack()
            img_width = self.splash_image.width()
            img_height = self.splash_image.height()
        else:
            # Fallback text label if image not loaded
            label = tk.Label(self.splash_window, text="OPEN-AIR", font=("Helvetica", 24, "bold"), fg="white", bg="black")
            label.pack(expand=True, fill=tk.BOTH)
            # Use a default size for text-only splash
            img_width = 400 
            img_height = 200
            self.splash_window.config(bg="black") # Set background for text label if no image

        status_bar_height = 30 
        total_height = img_height + status_bar_height

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = (screen_width // 2) - (img_width // 2)
        y = (screen_height // 2) - (total_height // 2)
        self.splash_window.geometry(f'{img_width}x{total_height}+{x}+{y}')

        # Status Bar
        self.status_label = tk.Label(self.splash_window, text="", fg="white", bg="black", font=("Helvetica", 10))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        self.parent.after(10, self._fade_in)

        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Exiting SplashScreen.__init__().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.__init__",
                console_print_func=console_log
            )

    def _fade_in(self, alpha=0.0):
        if self.splash_window.winfo_exists():
            if alpha <= 1.0:
                self.splash_window.attributes('-alpha', alpha)
                self.parent.after(20, lambda: self._fade_in(alpha + 0.05))

    def hide(self):
        if self.splash_window.winfo_exists():
            self._fade_out()

    def _fade_out(self, alpha=1.0):
        if self.splash_window.winfo_exists():
            if alpha >= 0.0:
                self.splash_window.attributes('-alpha', alpha)
                self.parent.after(20, lambda: self._fade_out(alpha - 0.05))
            else:
                self.splash_window.destroy()

    def set_status(self, message):
        if self.splash_window.winfo_exists():
            self.status_label.config(text=message)
            self.parent.update_idletasks()

if __name__ == '__main__':
    # For testing the splash screen directly
    root = tk.Tk()
    root.withdraw()
    splash = SplashScreen(root)
    
    # Simulate some work
    import time
    
    splash.set_status("Doing important work...")
    
    splash.set_status("Almost done...")
        
    splash.hide()
    
    # Keep the main thread alive for a bit to see if splash closes cleanly
    root.after(2000, root.destroy)
    root.mainloop()
    console_log("Main thread exiting.")