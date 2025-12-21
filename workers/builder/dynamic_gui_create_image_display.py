# workers/builder/dynamic_gui_create_image_display.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageDisplayCreatorMixin:
    def _create_image_display(self, parent_frame, label, config, path):
        """Creates an image display widget."""
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
            print(f"Error loading image: {e}")


        image_label = ttk.Label(frame, image=tk_image)
        image_label.image = tk_image # Keep a reference to avoid garbage collection
        image_label.pack(side=tk.LEFT)

        self.topic_widgets[path] = {"widget": image_label}
