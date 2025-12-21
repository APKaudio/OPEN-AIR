# workers/builder/dynamic_gui_create_directional_buttons.py

import tkinter as tk
from tkinter import ttk

class DirectionalButtonsCreatorMixin:
    def _create_directional_buttons(self, parent_frame, label, config, path):
        """Creates a set of directional buttons (up, down, left, right)."""
        frame = ttk.Frame(parent_frame)
        frame.pack(padx=10, pady=5)

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
            print(f"Move Up for {path}")
            # self.mqtt_util.publish(path + "/up", 1)

        def _move_down():
            print(f"Move Down for {path}")
            # self.mqtt_util.publish(path + "/down", 1)

        def _move_left():
            print(f"Move Left for {path}")
            # self.mqtt_util.publish(path + "/left", 1)

        def _move_right():
            print(f"Move Right for {path}")
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
