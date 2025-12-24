# workers/builder/dynamic_gui_create_image_display.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
import os

class ImageDisplayCreatorMixin:
    def _create_image_display(self, parent_frame, label, config, path):
        """Creates an image display widget."""
        current_function_name = "_create_image_display"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to render an image for '{label}'.",
**_get_log_args()
                


            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        image_path = config.get("image_path", "")
        
        try:
            pil_image = Image.open(image_path)
            tk_image = ImageTk.PhotoImage(pil_image)
            image_label = ttk.Label(frame, image=tk_image)
            image_label.image = tk_image 
        except FileNotFoundError:
            image_label = ttk.Label(frame, text=f"Image not found:\n{image_path}")
            tk_image = None
        except Exception as e:
            image_label = ttk.Label(frame, text=f"Error loading image:\n{e}")
            tk_image = None
            debug_log(message=f"🔴 ERROR loading image: {e}")

        image_label.pack(side=tk.LEFT)

        self.topic_widgets[path] = {"widget": image_label}
        
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"✅ SUCCESS! The image for '{label}' has been rendered!",
**_get_log_args()
                


            )
        return frame