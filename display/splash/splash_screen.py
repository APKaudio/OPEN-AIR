# display/splash/splash_screen.py
import tkinter as tk
from tkinter import ttk
import os
import sys
import pathlib

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False
    # Fallback console_log from within the splash_screen module if worker_active_logging is not yet available
    try:
        # This ensures console_log is available for the warning message
        # when PIL is not available but worker_active_logging might be.
        SPLASH_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
        if str(SPLASH_ROOT_DIR) not in sys.path:
            sys.path.append(str(SPLASH_ROOT_DIR))
        from workers.active.worker_active_logging import console_log
    except ImportError:
        def console_log(message):
            print(message)
    console_log("WARNING: Pillow (PIL) not available. Splash screen will not display image.")

# --- Path Setup ---
# This ensures the splash screen can find the project root to locate the image and other modules.
try:
    SPLASH_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
    if str(SPLASH_ROOT_DIR) not in sys.path:
        sys.path.append(str(SPLASH_ROOT_DIR))
    from workers.active.worker_active_logging import console_log
except ImportError:
    # Fallback if the path logic fails or modules are not found
    def console_log(message):
        print(message)

class SplashScreen:
    def __init__(self):
        self.splash_root = tk.Tk()
        self.splash_root.withdraw()
        
        # --- Faked Status Messages ---
        self.status_messages = [
            "Created by: Anthony Peter Kuzub",
            "www.like.audio",
            "Initializing...",

            "Loading GUI modules...",

        ]
        self.current_status_index = 0

        # --- Load Image ---
        self.splash_image = None
        image_path = None # Initialize image_path to avoid UnboundLocalError
        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(SPLASH_ROOT_DIR, 'display', 'splash', 'OPEN AIR LOGO.png')
                pil_image = Image.open(image_path)
                self.splash_image = ImageTk.PhotoImage(pil_image)
            except Exception as e:
                console_log(f"Splash screen error: Could not load image '{image_path}'. {e}")
                # Don't destroy root here, fallback to text
                PIL_AVAILABLE = False # Force fallback if image loading fails even with PIL
        
        # --- Window Setup ---
        self.splash_window = tk.Toplevel(self.splash_root)
        self.splash_window.overrideredirect(True)
        self.splash_window.attributes('-alpha', 0.0)

        # Widgets and sizing based on image availability
        if self.splash_image and PIL_AVAILABLE:
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

    def _update_status(self):
        if self.current_status_index < len(self.status_messages):
            self.status_label.config(text=self.status_messages[self.current_status_index])
            self.current_status_index += 1
            # The total duration of messages is 10 * 800ms = 8 seconds.
            self.splash_window.after(800, self._update_status)

    def _fade_in(self, alpha=0.0):
        if alpha <= 1.0:
            self.splash_window.attributes('-alpha', alpha)
            self.splash_window.after(20, lambda: self._fade_in(alpha + 0.05)) # Faster fade in
        else:
            self.splash_window.after(1000, self._fade_out) # Hold for 8 seconds while status updates

    def _fade_out(self, alpha=1.0):
        if alpha >= 0.0:
            self.splash_window.attributes('-alpha', alpha)
            self.splash_window.after(20, lambda: self._fade_out(alpha - 0.05)) # Faster fade out
        else:
            self.splash_root.destroy()
    
    def run(self):
        if not hasattr(self, 'splash_window'): # If init failed
            return
            
        # Start animations and status updates
        self.splash_window.after(10, self._fade_in)
        self.splash_window.after(1000, self._update_status) # Start status updates after 1 sec
        
        self.splash_root.mainloop()

if __name__ == '__main__':
    # For testing the splash screen directly
    splash = SplashScreen()
    splash.run()
