# workers/builder/dynamic_gui_create_directional_buttons.py

import tkinter as tk
from tkinter import ttk
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
import os

class DirectionalButtonsCreatorMixin:
    def _create_directional_buttons(self, parent_frame, label, config, path):
        """Creates a set of directional buttons (up, down, left, right)."""
        current_function_name = "_create_directional_buttons"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to chart the course for directional buttons for '{label}'.",
**_get_log_args()
                


            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).grid(row=0, column=1, pady=(0, 5))

        # Create buttons
        up_button = ttk.Button(frame, text="⬆")
        down_button = ttk.Button(frame, text="⬇")
        left_button = ttk.Button(frame, text="⬅")
        right_button = ttk.Button(frame, text="➡")

        up_button.grid(row=1, column=1)
        left_button.grid(row=2, column=0)
        right_button.grid(row=2, column=2)
        down_button.grid(row=3, column=1)

        # Commands (these would typically publish MQTT messages)
        def _move_up():
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"Move Up for {path}", file=os.path.basename(__file__), function="_move_up")
            # self.mqtt_util.publish(path + "/up", 1)

        def _move_down():
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"Move Down for {path}", file=os.path.basename(__file__), function="_move_down")
            # self.mqtt_util.publish(path + "/down", 1)

        def _move_left():
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"Move Left for {path}", file=os.path.basename(__file__), function="_move_left")
            # self.mqtt_util.publish(path + "/left", 1)

        def _move_right():
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"Move Right for {path}", file=os.path.basename(__file__), function="_move_right")
            # self.mqtt_util.publish(path + "/right", 1)

        up_button.config(command=_move_up)
        down_button.config(command=_move_down)
        left_button.config(command=_move_left)
        right_button.config(command=_move_right)

        self.topic_widgets[path] = {
            "widget": frame,
            "buttons": {
                "up": up_button,
                "down": down_button,
                "left": left_button,
                "right": right_button
            }
        }
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"✅ SUCCESS! The directional buttons for '{label}' are pointing the way!",
**_get_log_args()
                


            )
        return frame