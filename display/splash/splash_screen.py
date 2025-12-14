# display/splash/splash_screen.py
#
# This file (splash_screen.py) provides the SplashScreen class for displaying a customizable splash screen on application startup.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

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
import threading
import queue # For thread-safe status updates

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

class SplashScreen(threading.Thread):
    def __init__(self):
        super().__init__()
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Entering SplashScreen.__init__().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.__init__",
                console_print_func=console_log
            )
        self.daemon = True # Allow main program to exit even if splash is still running
        self.splash_root = None # Will be created in the thread
        self.splash_window = None
        self.status_label = None
        self.status_queue = queue.Queue() # For thread-safe status updates
        self._fade_animation_id = None # To store after_id for fade animation
        self._status_update_id = None # To store after_id for status updates
        self._destroyed = False # Flag to prevent multiple destructions

        # --- Faked Status Messages (initial set) ---
        self.status_messages_list = [
            "Created by: Anthony Peter Kuzub",
            "www.like.audio",
            "Initializing...",
            "Loading GUI modules...",
        ]
        self.current_status_index = 0

        # Enqueue initial status messages
        for msg in self.status_messages_list:
            self.status_queue.put(msg)

        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Exiting SplashScreen.__init__().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.__init__",
                console_print_func=console_log
            )

        self.splash_image = None
        
    def _init_ui(self):
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Entering SplashScreen._init_ui().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._init_ui",
                console_print_func=console_log
            )
        self.splash_root = tk.Tk()
        self.splash_root.withdraw()
        
        self.splash_window = tk.Toplevel(self.splash_root)
        self.splash_window.overrideredirect(True)
        self.splash_window.attributes('-alpha', 0.0)

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

        screen_width = self.splash_root.winfo_screenwidth()
        screen_height = self.splash_root.winfo_screenheight()
        x = (screen_width // 2) - (img_width // 2)
        y = (screen_height // 2) - (total_height // 2)
        self.splash_window.geometry(f'{img_width}x{total_height}+{x}+{y}')

        # Status Bar
        self.status_label = tk.Label(self.splash_window, text="", fg="white", bg="black", font=("Helvetica", 10))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Exiting SplashScreen._init_ui().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._init_ui",
                console_print_func=console_log
            )

    def _update_status(self):
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Entering _update_status().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._update_status",
                console_print_func=console_log
            )
        if not self.splash_window or not self.splash_window.winfo_exists():
            if Local_Debug_Enable:
                debug_log(
                    message="DEBUG: Splash window does not exist, stopping status updates.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}._update_status",
                    console_print_func=console_log
                )
            return

        try:
            message = self.status_queue.get_nowait()
            self.status_label.config(text=message)
            self.current_status_index += 1
            # Reschedule itself
            self._status_update_id = self.splash_window.after(800, self._update_status)
        except queue.Empty:
            # If no new messages, just reschedule to check again
            self._status_update_id = self.splash_window.after(800, self._update_status)
        
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Exiting _update_status().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._update_status",
                console_print_func=console_log
            )

    def _fade_in(self, alpha=0.0):
        if Local_Debug_Enable:
            debug_log(
                message=f"DEBUG: Entering _fade_in(). Alpha: {alpha}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._fade_in",
                console_print_func=console_log
            )
        if not self.splash_window or not self.splash_window.winfo_exists():
            if Local_Debug_Enable:
                debug_log(
                    message="DEBUG: Splash window does not exist, stopping fade-in.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}._fade_in",
                    console_print_func=console_log
                )
            return

        if alpha <= 1.0:
            self.splash_window.attributes('-alpha', alpha)
            self._fade_animation_id = self.splash_window.after(20, lambda: self._fade_in(alpha + 0.05))
        else:
            self._start_status_updates()
        if Local_Debug_Enable:
            debug_log(
                message=f"DEBUG: Exiting _fade_in(). Alpha: {alpha}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._fade_in",
                console_print_func=console_log
            )

    def _start_status_updates(self):
        # Start status updates after fade-in is complete
        if self.splash_window and self.splash_window.winfo_exists():
            self._status_update_id = self.splash_window.after(100, self._update_status)

    def _fade_out(self, alpha=1.0):
        if Local_Debug_Enable:
            debug_log(
                message=f"DEBUG: Entering _fade_out(). Alpha: {alpha}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._fade_out",
                console_print_func=console_log
            )
        if not self.splash_window or not self.splash_window.winfo_exists():
            if Local_Debug_Enable:
                debug_log(
                    message="DEBUG: Splash window does not exist, stopping fade-out.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}._fade_out",
                    console_print_func=console_log
                )
            return

        if alpha >= 0.0:
            self.splash_window.attributes('-alpha', alpha)
            self._fade_animation_id = self.splash_window.after(20, lambda: self._fade_out(alpha - 0.05))
        else:
            self._destroy_splash()
        if Local_Debug_Enable:
            debug_log(
                message=f"DEBUG: Exiting _fade_out(). Alpha: {alpha}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._fade_out",
                console_print_func=console_log
            )

    def _destroy_splash(self):
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Entering _destroy_splash().",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._destroy_splash",
                console_print_func=console_log
            )
        if self._destroyed:
            if Local_Debug_Enable:
                debug_log(
                    message="DEBUG: _destroy_splash() called, but splash screen already destroyed.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}._destroy_splash",
                    console_print_func=console_log
                )
            return

        if self.splash_root and self.splash_root.winfo_exists():
            # Cancel any pending after calls
            if self._fade_animation_id:
                self.splash_root.after_cancel(self._fade_animation_id)
            if self._status_update_id:
                self.splash_root.after_cancel(self._status_update_id)
            try:
                self.splash_root.destroy()
            except tk.TclError as e:
                if Local_Debug_Enable:
                    debug_log(
                        message=f"ERROR: Tkinter TclError during splash screen destruction: {e}",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}._destroy_splash",
                        console_print_func=console_log
                    )
            finally:
                self._destroyed = True # Set the flag even if an error occurred during destroy
        else:
            self._destroyed = True # If root doesn't exist or already gone, mark as destroyed

        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Exiting _destroy_splash()..",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._destroy_splash",
                console_print_func=console_log
            )

    def run(self):
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Entering SplashScreen.run() thread.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.run",
                console_print_func=console_log
            )
        self._init_ui()
        self.splash_window.after(10, self._fade_in)
        self.splash_root.mainloop()
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Exiting SplashScreen.run() thread.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.run",
                console_print_func=console_log
            )

    def hide(self):
        if Local_Debug_Enable:
            debug_log(
                message="DEBUG: Request to hide splash screen received.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.hide",
                console_print_func=console_log
            )
        if self.splash_root and self.splash_root.winfo_exists():
            self.splash_root.after(0, self._destroy_splash) # Use after(0) for immediate execution in Tkinter's event loop
        else:
            if Local_Debug_Enable:
                debug_log(
                    message="DEBUG: Splash screen root not found or already destroyed, cannot hide.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.hide",
                    console_print_func=console_log
                )

    def set_status(self, message):
        if Local_Debug_Enable:
            debug_log(
                message=f"DEBUG: Setting splash screen status: {message}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.set_status",
                console_print_func=console_log
            )
        self.status_queue.put(message)

if __name__ == '__main__':
    # For testing the splash screen directly
    splash = SplashScreen()
    splash.start() # Start the splash screen in a new thread
    
    # Simulate some work
    import time
    time.sleep(1)
    splash.set_status("Doing important work...")
    time.sleep(2)
    splash.set_status("Almost done...")
    time.sleep(1)
    
    splash.hide() # Hide the splash screen
    
    # Keep the main thread alive for a bit to see if splash closes cleanly
    time.sleep(1)
    console_log("Main thread exiting.")