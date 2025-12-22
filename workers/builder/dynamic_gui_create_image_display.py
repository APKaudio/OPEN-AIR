# workers/builder/dynamic_gui_create_image_display.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log, console_log
import os

class ImageDisplayCreatorMixin:
    def _create_image_display(self, parent_frame, label, config, path):
        """Creates an image display widget."""
        current_function_name = "_create_image_display"
        if app_constants.Local_Debug_Enable:
            debug_log(message=f"Creating image display for {label}", file=os.path.basename(__file__), function=current_function_name)

        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        image_path = config.get("image_path", "")
        
        try:
            pil_image = Image.open(image_path)
            # You might want to resize the image here, e.g.:
            # pil_image = pil_image.resize((width, height), Image.ANTIALIAS)
            tk_image = ImageTk.PhotoImage(pil_image)
        except Exception as e:
            # Handle image loading errors, maybe display a placeholder
            tk_image = None
            console_log(f"🔴 ERROR loading image: {e}")
            if app_constants.Local_Debug_Enable:
                debug_log(message=f"🔴 ERROR loading image: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)


        image_label = ttk.Label(frame, image=tk_image)
        image_label.image = tk_image # Keep a reference to avoid garbage collection
        image_label.pack(side=tk.LEFT)

        self.topic_widgets[path] = {"widget": image_label}