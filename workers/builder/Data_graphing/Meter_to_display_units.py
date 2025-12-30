import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
import math
import orjson
import time

from workers.mqtt.mqtt_publisher_service import publish_payload
from workers.utils.topic_utils import get_topic
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args
from workers.logger.logger import debug_logger

app_constants = Config.get_instance()

class HorizontalMeterWithText(ttk.Frame):
    """
    A Tkinter widget that displays a numerical value with progress bars.
    """
    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None)
        self.state_mirror_engine = kwargs.pop('state_mirror_engine', None)
        super().__init__(parent, **kwargs)
        self.config = config
        self.base_mqtt_topic_from_path = base_mqtt_topic_from_path
        self.widget_id = widget_id
        
        self.title_text = config.get('title', 'Meter')
        self.max_integer_value = config.get('max_integer_value', 100)
        
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
        
        self.update_value(config.get('value_default', 0.0))

        if self.subscriber_router:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            update_topic_suffix = config.get('update_topic_suffix', "set_value")
            self.update_topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id, update_topic_suffix)
            self.subscriber_router.subscribe_to_topic(self.update_topic, self._on_value_mqtt_update)

    def _on_value_mqtt_update(self, topic, payload):
        try:
            data = orjson.loads(payload)
            self.update_value(float(data.get("value", 0.0)))
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            debug_logger(f"Error processing MQTT update for {self.widget_id}: {e}", **_get_log_args())

    def update_value(self, new_value: float):
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
        
        try:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id, "value")
            payload = {"value": new_value, "timestamp": time.time()}
            publish_payload(topic, orjson.dumps(payload), retain=True)
        except Exception as e:
            debug_logger(f"Error publishing value for {self.widget_id}: {e}", **_get_log_args())

class VerticalMeter(ttk.Frame):
    """
    A Tkinter widget to simulate a 4-channel vertical meter display.
    """
    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None)
        self.state_mirror_engine = kwargs.pop('state_mirror_engine', None)
        super().__init__(parent, **kwargs)
        self.config = config
        self.base_mqtt_topic_from_path = base_mqtt_topic_from_path
        self.widget_id = widget_id
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
        try:
            data = orjson.loads(payload)
            self.update_values([float(v) for v in data.get("values", [])])
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            debug_logger(f"Error processing MQTT update for {self.widget_id}: {e}", **_get_log_args())

    def update_values(self, new_values: List[float]):
        for i, value in enumerate(new_values):
            if i < len(self.channel_labels):
                self.channel_labels[i].config(text=f"Ch {i+1}: {value:.2f}")
        try:
            base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
            topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id, "values")
            payload = {"values": new_values, "timestamp": time.time()}
            publish_payload(topic, orjson.dumps(payload), retain=True)
        except Exception as e:
            debug_logger(f"Error publishing values for {self.widget_id}: {e}", **_get_log_args())

if __name__ == "__main__":
    # Example usage remains the same
    pass
