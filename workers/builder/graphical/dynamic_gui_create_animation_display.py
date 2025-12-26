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
    def _create_animation_display(self, parent_frame, label, config, path, state_mirror_engine, subscriber_router):
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
                return frame # Exit early if critical failure
        except Exception as e:
            debug_logger(message=f"🔴 ERROR loading animation: {e}", **_get_log_args())
            # Fallback to an error label for other loading errors
            anim_label = ttk.Label(frame, text=f"[Animation Error]\n{e}", fg="red", bg="black", wraplength=150)
            anim_label.pack(side=tk.LEFT)
            return frame # Exit early if critical failure

        anim_label = ttk.Label(frame)
        anim_label.pack(side=tk.LEFT)
        
        if frames:
            anim_label.config(image=frames[0]) # Display the first frame or placeholder

        def _update_frame(value):
            try:
                frame_index = int(value)
                if 0 <= frame_index < len(frames):
                    anim_label.config(image=frames[frame_index])
            except (ValueError, TypeError) as e:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"🔴 ERROR updating animation frame: {e}", file=os.path.basename(__file__), function=current_function_name)

        if path:
            self.topic_widgets[path] = _update_frame # Store the update callable

            # --- MQTT Subscription for incoming updates ---
            topic = get_topic("OPEN-AIR", self.tab_name, path) # Use self.tab_name from DynamicGuiBuilder
            subscriber_router.subscribe_to_topic(topic, self._on_animation_frame_update_mqtt)

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"✅ SUCCESS! The animation for '{label}' is ready to roll!",
                **_get_log_args()
            )
        return frame

    def _on_animation_frame_update_mqtt(self, topic, payload):
        import orjson # Imported here to avoid circular dependency or top-level import issues
        try:
            payload_data = orjson.loads(payload)
            value = payload_data.get('val')
            
            # Extract widget path from topic
            # topic is "OPEN-AIR/<tab_name>/<path>"
            expected_prefix = f"OPEN-AIR/{self.tab_name}/" # Assuming self.tab_name is available from DynamicGuiBuilder
            if topic.startswith(expected_prefix):
                widget_path = topic[len(expected_prefix):]
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"⚠️ Unexpected topic format for animation frame update: {topic}", **_get_log_args())
                return
            
            update_func = self.topic_widgets.get(widget_path)
            if update_func:
                update_func(value)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"🎞️ Animation '{widget_path}' frame updated to {value}", **_get_log_args())
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"⚠️ Animation update function not found for path: {widget_path}", **_get_log_args())

        except (orjson.JSONDecodeError, AttributeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"❌ Error processing animation MQTT update for {topic}: {e}. Payload: {payload}", **_get_log_args())