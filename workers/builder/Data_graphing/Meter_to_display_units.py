# display/Meter_to_display_units.py
#
# Meters for visualizing data (Horizontal and Vertical).
# Refactored to align with StateMirrorEngine standards for MQTT topology and payloads.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20251230.181522.1

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
import math
import orjson
import time
import inspect

from workers.mqtt.mqtt_publisher_service import publish_payload
from workers.utils.topic_utils import get_topic
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args
from workers.logger.logger import debug_logger

app_constants = Config.get_instance()

# Globals
current_version = "20251230.181522.1"
current_version_hash = 20251230 * 181522 * 1

class HorizontalMeterWithText(ttk.Frame):
    """
    A Tkinter widget that displays a numerical value with progress bars.
    Now publishes standard 'val' envelopes to the widget's root topic.
    """
    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None)
        self.state_mirror_engine = kwargs.pop('state_mirror_engine', None)
        super().__init__(parent, **kwargs)
        self.config = config
        self.base_mqtt_topic_from_path = base_mqtt_topic_from_path
        self.widget_id = widget_id
        
        # 🧪 Temporal Alignment: Fetch the GUID
        self.instance_id = "UNKNOWN_GUID"
        if self.state_mirror_engine and hasattr(self.state_mirror_engine, 'instance_id'):
            self.instance_id = self.state_mirror_engine.instance_id

        self.title_text = config.get('title', 'Meter')
        self.max_integer_value = config.get('max_integer_value', 100)
        
        # --- UI Construction ---
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.label_title = ttk.Label(self.header_frame, text=self.title_text, anchor="w")
        self.label_title.pack(side=tk.LEFT, padx=2)

        self.label_value = ttk.Label(self.header_frame, text="Value: --", anchor="e")
        self.label_value.pack(side=tk.RIGHT, padx=2)

        self.int_frame = ttk.Frame(self)
        self.int_frame.pack(side=tk.TOP, fill=tk.X, pady=(5,0))

        self.bar_graph_value1 = ttk.Progressbar(self.int_frame, orient="horizontal", length=200, mode="determinate")
        self.bar_graph_value1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.bar_graph_value1["maximum"] = self.max_integer_value

        self.label1 = ttk.Label(self.int_frame, text="Int: --", width=8, anchor="w")
        self.label1.pack(side=tk.RIGHT, padx=2)

        self.dec_frame = ttk.Frame(self)
        self.dec_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,5))

        self.bar_graph_value_dec = ttk.Progressbar(self.dec_frame, orient="horizontal", length=200, mode="determinate")
        self.bar_graph_value_dec.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.bar_graph_value_dec["maximum"] = 100

        self.label_dec = ttk.Label(self.dec_frame, text="Dec: --", width=8, anchor="w")
        self.label_dec.pack(side=tk.RIGHT, padx=2)
        
        # Initialize
        self.update_value(config.get('value_default', 0.0))

        # 📡 Subscribe to Updates
        if self.subscriber_router:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            update_topic_suffix = config.get('update_topic_suffix', "set_value")
            # Subscription topic usually includes a specific command suffix (like 'set_value')
            self.update_topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id, update_topic_suffix)
            self.subscriber_router.subscribe_to_topic(self.update_topic, self._on_value_mqtt_update)

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🧪 Meter '{self.widget_id}' initialized. GUID: {self.instance_id}",
                **_get_log_args()
            )

    def _on_value_mqtt_update(self, topic, payload):
        """Handles incoming MQTT messages, supporting both raw and enveloped data."""
        try:
            data = orjson.loads(payload)
            val = 0.0
            
            # 🕵️ Unwrap Standard Envelope
            if isinstance(data, dict):
                if 'val' in data:
                    # 🛑 Infinite Loop Protection
                    if data.get('instance_id') == self.instance_id:
                        return
                    val = float(data['val'])
                elif 'value' in data:
                    val = float(data['value'])
                else:
                    # Fallback if raw number sent as json
                    # This might fail if data is complex, but meters expect numbers
                    pass
            else:
                # Direct value
                val = float(data)

            self.update_value(val)
            
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error processing MQTT for {self.widget_id}: {e}", **_get_log_args())

    def update_value(self, new_value: float):
        # Update UI
        self.label_value.config(text=f"Value: {new_value:.3f}")
        truncated_value = math.trunc(new_value)
        decimal_part = abs(new_value - truncated_value) * 100
        self.bar_graph_value1["value"] = min(abs(truncated_value), self.max_integer_value)
        self.label1.config(text=f"Int: {truncated_value}")
        self.bar_graph_value_dec["value"] = decimal_part
        self.label_dec.config(text=f"Dec: {int(decimal_part)}")

        if new_value < 0:
            self.label_value.config(foreground="red")
        else:
            self.label_value.config(foreground="black")
        
        # 🚀 Publish Standardized State
        try:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            
            # FIXED: Publish to the Widget Root, not a subfolder (unless configured otherwise)
            # This aligns with standard Faders/Buttons.
            topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id)
            
            payload = {
                "val": new_value,
                "ts": time.time(),
                "instance_id": self.instance_id,
                "src": "HorizontalMeter"
            }
            publish_payload(topic, orjson.dumps(payload), retain=True)
            
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error publishing value for {self.widget_id}: {e}", **_get_log_args())

class VerticalMeter(ttk.Frame):
    """
    A Tkinter widget to simulate a 4-channel vertical meter display.
    Now publishes standard 'val' envelopes to the widget's root topic.
    """
    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None)
        self.state_mirror_engine = kwargs.pop('state_mirror_engine', None)
        super().__init__(parent, **kwargs)
        self.config = config
        self.base_mqtt_topic_from_path = base_mqtt_topic_from_path
        self.widget_id = widget_id
        
        # 🧪 Temporal Alignment
        self.instance_id = "UNKNOWN_GUID"
        if self.state_mirror_engine and hasattr(self.state_mirror_engine, 'instance_id'):
            self.instance_id = self.state_mirror_engine.instance_id
            
        self.channel_labels: List[ttk.Label] = []
        num_channels = config.get('num_channels', 4)

        for i in range(num_channels):
            label = ttk.Label(self, text=f"Ch {i+1}: --", anchor="w")
            label.pack(side=tk.TOP, fill=tk.X, pady=1)
            self.channel_labels.append(label)
        
        initial_values = [config.get('value_default', 0.0)] * num_channels
        self.update_values(initial_values)

        if self.subscriber_router:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            update_topic_suffix = config.get('update_topic_suffix', "set_values")
            self.update_topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id, update_topic_suffix)
            self.subscriber_router.subscribe_to_topic(self.update_topic, self._on_values_mqtt_update)

    def _on_values_mqtt_update(self, topic, payload):
        """Handles incoming MQTT messages, supporting both raw and enveloped data."""
        try:
            data = orjson.loads(payload)
            new_values = []

            # 🕵️ Unwrap Standard Envelope
            if isinstance(data, dict):
                if 'val' in data:
                     # 🛑 Infinite Loop Protection
                    if data.get('instance_id') == self.instance_id:
                        return
                    raw_val = data['val']
                    if isinstance(raw_val, list):
                        new_values = [float(v) for v in raw_val]
                elif 'values' in data:
                    new_values = [float(v) for v in data['values']]
            elif isinstance(data, list):
                new_values = [float(v) for v in data]

            if new_values:
                self.update_values(new_values)
                
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error processing MQTT update for {self.widget_id}: {e}", **_get_log_args())

    def update_values(self, new_values: List[float]):
        # Update UI
        for i, value in enumerate(new_values):
            if i < len(self.channel_labels):
                self.channel_labels[i].config(text=f"Ch {i+1}: {value:.2f}")
        
        # 🚀 Publish Standardized State
        try:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            
            # FIXED: Publish to Widget Root
            topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id)
            
            payload = {
                "val": new_values, # The list is now the main 'val'
                "ts": time.time(),
                "instance_id": self.instance_id,
                "src": "VerticalMeter"
            }
            publish_payload(topic, orjson.dumps(payload), retain=True)
            
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error publishing values for {self.widget_id}: {e}", **_get_log_args())

if __name__ == "__main__":
    # Example usage remains the same
    pass