# workers/builder/dynamic_gui_create_animation_display.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
import os
from workers.setup.path_initializer import GLOBAL_PROJECT_ROOT # Import GLOBAL_PROJECT_ROOT

class AnimationDisplayCreatorMixin:
    def _create_animation_display(self, parent_frame, label, config, path):
        """Creates an animation display widget."""
        current_function_name = "_create_animation_display"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to animate the display for '{label}'.",
                **_get_log_args()
            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        gif_path_relative = config.get("gif_path", "")
        gif_path_absolute = os.path.join(GLOBAL_PROJECT_ROOT, gif_path_relative)
        
        frames = []
        try:
            with Image.open(gif_path_absolute) as im:
                for frame_img in ImageSequence.Iterator(im):
                    frames.append(ImageTk.PhotoImage(frame_img.copy()))
        except FileNotFoundError:
            debug_logger(message=f"🔴 GIF not found at {gif_path_absolute}. Creating placeholder.", **_get_log_args())
            try:
                # Ensure the directory exists before saving the placeholder
                os.makedirs(os.path.dirname(gif_path_absolute), exist_ok=True)
                
                # Create a simple static placeholder image (PNG)
                placeholder_image = Image.new('RGB', (100, 100), color = 'black')
                placeholder_filename = gif_path_absolute + ".png" # Save as PNG
                placeholder_image.save(placeholder_filename)
                
                # Load the placeholder as a single frame
                placeholder_tk_image = ImageTk.PhotoImage(placeholder_image)
                frames.append(placeholder_tk_image)
                debug_logger(message=f"☑️ INFO: Created placeholder image at {placeholder_filename}")
            except Exception as e_placeholder:
                debug_logger(message=f"🔴 ERROR creating placeholder image: {e_placeholder}", **_get_log_args())
                # If even placeholder creation fails, create a generic error label
                anim_label = ttk.Label(frame, text=f"[Animation Error]\n{e_placeholder}", fg="red", bg="black", wraplength=150)
                anim_label.pack(side=tk.LEFT)
                self.topic_widgets[path] = {"widget": anim_label, "frames": []}
                return frame # Exit early if critical failure
        except Exception as e:
            debug_logger(message=f"🔴 ERROR loading animation: {e}", **_get_log_args())
            # Fallback to an error label for other loading errors
            anim_label = ttk.Label(frame, text=f"[Animation Error]\n{e}", fg="red", bg="black", wraplength=150)
            anim_label.pack(side=tk.LEFT)
            self.topic_widgets[path] = {"widget": anim_label, "frames": []}
            return frame # Exit early if critical failure

        anim_label = ttk.Label(frame)
        anim_label.pack(side=tk.LEFT)
        
        if frames:
            anim_label.config(image=frames[0]) # Display the first frame or placeholder

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
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"🔴 ERROR updating animation frame: {e}", file=os.path.basename(__file__), function=current_function_name)

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"✅ SUCCESS! The animation for '{label}' is ready to roll!",
                **_get_log_args()
            )
        # self.mqtt_callbacks[path] = _update_frame
        return frame