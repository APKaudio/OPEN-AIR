import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
import math
import orjson
import time # Import time for timestamp in MQTT payload

from workers.mqtt.mqtt_publisher_service import publish_payload
from workers.utils.topic_utils import get_topic
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args
from workers.logger.logger import debug_logger # Added import for debug_logger

app_constants = Config.get_instance()

class HorizontalMeterWithText(ttk.Frame):
    """
    A Tkinter widget inspired by a Visual Basic control, displaying a numerical value
    split into integer and decimal parts, visualized with progress bars and labels.
    """
    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None) # Extract subscriber_router from kwargs
        super().__init__(parent, **kwargs)
        self.config = config
        self.base_mqtt_topic_from_path = base_mqtt_topic_from_path
        self.widget_id = widget_id
        
        self.title_text = config.get('title', 'Meter')
        self.max_integer_value = config.get('max_integer_value', 100) # Default max for integer bar
        
        # Frame for Title and Value Display
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.label_title = ttk.Label(self.header_frame, text=self.title_text, anchor="w")
        self.label_title.pack(side=tk.LEFT, padx=2)

        self.label_value = ttk.Label(self.header_frame, text="Value: --", anchor="e")
        self.label_value.pack(side=tk.RIGHT, padx=2)

        # Frame for Integer Part (BarGraphValue1)
        self.int_frame = ttk.Frame(self)
        self.int_frame.pack(side=tk.TOP, fill=tk.X, pady=(5,0))

        self.bar_graph_value1 = ttk.Progressbar(self.int_frame, orient="horizontal", length=200, mode="determinate")
        self.bar_graph_value1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.bar_graph_value1["maximum"] = self.max_integer_value # Set maximum for integer part

        self.label1 = ttk.Label(self.int_frame, text="Int: --", width=8, anchor="w")
        self.label1.pack(side=tk.RIGHT, padx=2)

        # Frame for Decimal Part (BarGraphValueDec)
        self.dec_frame = ttk.Frame(self)
        self.dec_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,5))

        self.bar_graph_value_dec = ttk.Progressbar(self.dec_frame, orient="horizontal", length=200, mode="determinate")
        self.bar_graph_value_dec.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.bar_graph_value_dec["maximum"] = 100 # Decimal part is scaled to 100

        self.label_dec = ttk.Label(self.dec_frame, text="Dec: --", width=8, anchor="w")
        self.label_dec.pack(side=tk.RIGHT, padx=2)
        
        self.update_value(config.get('value_default', 0.0))

        # MQTT Subscription for updates
        if self.subscriber_router:
            update_topic_suffix = config.get('update_topic_suffix', "set_value")
            self.update_topic = get_topic(self.base_mqtt_topic_from_path, self.widget_id, update_topic_suffix)
            self.subscriber_router.subscribe_to_topic(self.update_topic, self._on_value_mqtt_update)
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"🔗 HorizontalMeterWithText '{self.widget_id}' subscribed to MQTT topic: {self.update_topic}",
                    **_get_log_args()
                )

    def _on_value_mqtt_update(self, topic, payload):
        """Callback for MQTT messages to update the meter's value."""
        try:
            payload_data = orjson.loads(payload)
            new_value = payload_data.get("value")
            if new_value is not None:
                self.update_value(float(new_value))
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"📥 HorizontalMeterWithText '{self.widget_id}' updated to {new_value} from MQTT topic: {topic}",
                        **_get_log_args()
                    )
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ Error processing MQTT update for HorizontalMeterWithText '{self.widget_id}': {e}. Payload: {payload}",
                    **_get_log_args()
                )

    def update_value(self, new_value: float):
        """Updates the meter display with a new numerical value."""
        self.label_value.config(text=f"Value: {new_value:.3f}")

        truncated_value = math.trunc(new_value)
        decimal_part = abs(new_value - truncated_value) * 100

        # Update integer part
        self.bar_graph_value1["value"] = min(abs(truncated_value), self.max_integer_value) # Ensure not to exceed max
        self.label1.config(text=f"Int: {truncated_value}")

        # Update decimal part
        self.bar_graph_value_dec["value"] = decimal_part
        self.label_dec.config(text=f"Dec: {int(decimal_part)}")

        # Handle "right to left" for negative numbers (visual cue by color)
        if new_value < 0:
            self.label_value.config(foreground="red")
            self.label1.config(foreground="red")
            self.label_dec.config(foreground="red")
        else:
            self.label_value.config(foreground="black") # Assuming default foreground is black
            self.label1.config(foreground="black")
            self.label_dec.config(foreground="black")
        
        # Publish the new value to MQTT
        if self.subscriber_router and app_constants.ENABLE_BUILDER_STATUS_PUBLISH:
            try:
                publish_topic = get_topic(self.base_mqtt_topic_from_path, self.widget_id, "value")
                payload = {
                    "value": new_value,
                    "timestamp": time.time()
                }
                publish_payload(publish_topic, orjson.dumps(payload), retain=True)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"📢 HorizontalMeterWithText '{self.widget_id}' published value {new_value} to {publish_topic}",
                        **_get_log_args()
                    )
            except Exception as e:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"❌ Error publishing HorizontalMeterWithText value for '{self.widget_id}': {e}",
                        **_get_log_args()
                    )


class VerticalMeter(ttk.Frame):
    """
    A Tkinter widget to simulate a 4-channel vertical meter display.
    Placeholder for actual plotting, uses labels for values.
    """
    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None) # Extract subscriber_router from kwargs
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
        
        self.update_values([config.get('value_default', 0.0)] * num_channels)

        # MQTT Subscription for updates
        if self.subscriber_router:
            update_topic_suffix = config.get('update_topic_suffix', "set_values")
            self.update_topic = get_topic(self.base_mqtt_topic_from_path, self.widget_id, update_topic_suffix)
            self.subscriber_router.subscribe_to_topic(self.update_topic, self._on_values_mqtt_update)
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"🔗 VerticalMeter '{self.widget_id}' subscribed to MQTT topic: {self.update_topic}",
                    **_get_log_args()
                )

    def _on_values_mqtt_update(self, topic, payload):
        """Callback for MQTT messages to update the meter's values."""
        try:
            payload_data = orjson.loads(payload)
            new_values = payload_data.get("values")
            if isinstance(new_values, list):
                self.update_values([float(v) for v in new_values])
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"📥 VerticalMeter '{self.widget_id}' updated to {new_values} from MQTT topic: {topic}",
                        **_get_log_args()
                    )
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ Error processing MQTT update for VerticalMeter '{self.widget_id}': {e}. Payload: {payload}",
                    **_get_log_args()
                )

    def update_values(self, new_values: List[float]):
        """Updates the display with new values for each channel."""
        for i, value in enumerate(new_values):
            if i < len(self.channel_labels):
                self.channel_labels[i].config(text=f"Ch {i+1}: {value:.2f}")

        # Publish the new values to MQTT
        if self.subscriber_router and app_constants.ENABLE_BUILDER_STATUS_PUBLISH:
            try:
                publish_topic = get_topic(self.base_mqtt_topic_from_path, self.widget_id, "values")
                payload = {
                    "values": new_values,
                    "timestamp": time.time()
                }
                publish_payload(publish_topic, orjson.dumps(payload), retain=True)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"📢 VerticalMeter '{self.widget_id}' published values {new_values} to {publish_topic}",
                        **_get_log_args()
                    )
            except Exception as e:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"❌ Error publishing VerticalMeter values for '{self.widget_id}': {e}",
                        **_get_log_args()
                    )

# Example usage (for testing purposes)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Meter Display Test")

    # Horizontal Meter Test
    h_meter_config = {
        "id": "h_meter_test",
        "title": "Voltage Level",
        "value_default": 123.456,
        "max_integer_value": 200
    }
    h_meter = HorizontalMeterWithText(root, config=h_meter_config, padx=10, pady=10)
    h_meter.pack(side=tk.LEFT, fill=tk.Y, expand=False)

    def update_h_meter(value):
        h_meter.update_value(float(value))

    h_slider = ttk.Scale(root, from_=-200, to=200, command=update_h_meter, orient=tk.HORIZONTAL, length=200)
    h_slider.set(h_meter_config['value_default'])
    h_slider.pack(side=tk.TOP, padx=10, pady=5)
    
    # Vertical Meter Test
    v_meter_config = {
        "id": "v_meter_test",
        "num_channels": 4,
        "value_default": 0.0
    }
    v_meter = VerticalMeter(root, config=v_meter_config, padx=10, pady=10)
    v_meter.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

    channel_values = [tk.DoubleVar(value=0.0) for _ in range(v_meter_config['num_channels'])]

    def update_v_meter(*args):
        current_values = [var.get() for var in channel_values]
        v_meter.update_values(current_values)

    for i, var in enumerate(channel_values):
        var.trace_add("write", update_v_meter)
        ttk.Scale(root, from_=-10, to=10, variable=var, orient=tk.VERTICAL, length=100).pack(side=tk.RIGHT, padx=5)

    root.mainloop()