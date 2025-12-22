# workers/builder/dynamic_gui_create_animation_display.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log, console_log
import os

class AnimationDisplayCreatorMixin:
    def _create_animation_display(self, parent_frame, label, config, path):
        """Creates an animation display widget."""
        current_function_name = "_create_animation_display"
        if app_constants.Local_Debug_Enable:
            debug_log(message=f"Creating animation display for {label}", file=os.path.basename(__file__), function=current_function_name)

        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        gif_path = config.get("gif_path", "")
        
        frames = []
        try:
            with Image.open(gif_path) as im:
                for frame in ImageSequence.Iterator(im):
                    frames.append(ImageTk.PhotoImage(frame.copy()))
        except Exception as e:
            console_log(f"🔴 ERROR loading animation: {e}")
            if app_constants.Local_Debug_Enable:
                debug_log(message=f"🔴 ERROR loading animation: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)

        anim_label = ttk.Label(frame)
        anim_label.pack(side=tk.LEFT)
        
        if frames:
            anim_label.config(image=frames[0])

        self.topic_widgets[path] = {
            "widget": anim_label,
            "frames": frames
        }
        
        def _update_frame(value):
            try:
                frame_index = int(value)
                if 0 <= frame_index < len(frames):
                    anim_label.config(image=frames[frame_index])
            except (ValueError, TypeError) as e:
                if app_constants.Local_Debug_Enable:
                    debug_log(message=f"🔴 ERROR updating animation frame: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)

        # self.mqtt_callbacks[path] = _update_frame