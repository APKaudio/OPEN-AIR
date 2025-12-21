# workers/builder/dynamic_gui_create_progress_bar.py

import tkinter as tk
from tkinter import ttk

class ProgressBarCreatorMixin:
    def _create_progress_bar(self, parent_frame, label, config, path):
        """Creates a progress bar widget."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))

        min_val = config.get("min", 0)
        max_val = config.get("max", 100)
        units = config.get("units", "")
        
        progressbar = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=200,
            mode="determinate",
            maximum=max_val,
            value=config.get("value_default", min_val)
        )
        progressbar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        value_label = ttk.Label(frame, text=f"{progressbar['value']} {units}")
        value_label.pack(side=tk.LEFT, padx=(10, 0))

        self.topic_widgets[path] = {
            "widget": progressbar,
            "value_label": value_label,
            "units": units
        }
        
        # Add logic to handle incoming MQTT messages to update the progress bar
        def _update_progress(value):
            try:
                float_value = float(value)
                progressbar['value'] = float_value
                value_label['text'] = f"{float_value} {units}"
            except (ValueError, TypeError):
                pass # Or log an error

        self.mqtt_callbacks[path] = _update_progress
