# workers/builder/dynamic_gui_create_image_display.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from workers.mqtt.setup.config_reader import app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
import os
from workers.setup.path_initializer import GLOBAL_PROJECT_ROOT

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

        image_path_relative = config.get("image_path", "")
        image_path_absolute = os.path.join(GLOBAL_PROJECT_ROOT, image_path_relative)

        try:
            pil_image = Image.open(image_path_absolute)
            tk_image = ImageTk.PhotoImage(pil_image)
            image_label = ttk.Label(frame, image=tk_image)
            image_label.image = tk_image 
        except FileNotFoundError:
            image_label = ttk.Label(frame, text=f"Image not found:\n{image_path_relative}", wraplength=150)
            tk_image = None
            # Create a placeholder image
            try:
                # Ensure the directory exists before saving the placeholder
                os.makedirs(os.path.dirname(image_path_absolute), exist_ok=True)
                placeholder_image = Image.new('RGB', (100, 100), color = 'black')
                placeholder_image.save(image_path_absolute)
                debug_log(message=f"☑️ INFO: Created placeholder image at {image_path_absolute}")
            except Exception as e:
                debug_log(message=f"🔴 ERROR creating placeholder image: {e}")

        except Exception as e:
            image_label = ttk.Label(frame, text=f"Error loading image:\n{e}", wraplength=150)
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