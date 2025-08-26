# workers/worker_control_builder.py
#
# A worker utility that reads a JSON configuration, processes incoming MQTT data,
# and publishes a simplified, display-ready payload for the GUI.
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
#
# Version 20250826.002845.3

import os
import inspect
import datetime
import json

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility


# --- Global Scope Variables ---
CURRENT_DATE = 20250826
CURRENT_TIME = 2845
REVISION_NUMBER = 3
current_version = "20250826.002845.3"
current_version_hash = 20250826 * 2845 * 3
current_file = "workers/worker_control_builder.py"

# --- No Magic Numbers (as per your instructions) ---
TOPIC_DELIMITER = "/"
GUI_TOPIC_FILTER = "OPEN-AIR/gui"
CONFIG_TOPIC_FILTER = "OPEN-AIR/configuration"
PRESETS_SUBTOPIC = "presets"
CONFIG_FILE_PATH = "config/dataset_configuration_presets.json"


class ControlBuilderWorker:
    """
    Manages application configuration, listens for MQTT updates, and publishes
    simplified payloads for the GUI.
    """
    def __init__(self, mqtt_util):
        """
        Initializes the worker, loads the config, and sets up MQTT subscriptions.
        """
        self.mqtt_util = mqtt_util
        self.json_config = self._load_json_config(CONFIG_FILE_PATH)

        self.mqtt_util.add_subscriber(
            topic_filter=f"{CONFIG_TOPIC_FILTER}/{PRESETS_SUBTOPIC}/#",
            callback_func=self._on_config_message
        )
        console_log("✅ ControlBuilderWorker initialized and subscribed to config topics.")

    def _load_json_config(self, file_path):
        """Loads a JSON configuration file from disk."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            console_log(f"❌ Configuration file '{file_path}' not found.")
            return {}
        except json.JSONDecodeError as e:
            console_log(f"❌ Error decoding JSON in '{file_path}': {e}")
            return {}

    def _get_nested_value(self, data, path):
        """Traverses a dictionary to find a nested value given a path string."""
        if not path:
            return data
        
        nodes = path.split(TOPIC_DELIMITER)
        current = data
        for node in nodes:
            current = current.get(node)
            if current is None:
                return None
        return current

    def _on_config_message(self, topic, payload):
        """
        Callback for incoming MQTT messages on the configuration topic.
        Updates the in-memory config and publishes a simplified payload for the GUI.
        """
        topic_path = topic.replace(f"{CONFIG_TOPIC_FILTER}/{PRESETS_SUBTOPIC}", "").strip(TOPIC_DELIMITER)
        config_node = self._get_nested_value(self.json_config, topic_path)
        
        if not config_node:
            debug_log(f"🟡 No configuration node found for topic: '{topic}'", file=current_file, version=current_version)
            return

        try:
            new_value = json.loads(payload).get("value")
            
            # This logic needs to be more robust for nested values
            # For simplicity, we assume the payload only updates the 'value' key
            # Update the in-memory state
            if "Value" in config_node:
                config_node["Value"]["value"] = new_value
            elif "Value_dB" in config_node:
                config_node["Value_dB"]["value"] = new_value
            elif "Value_MHz" in config_node:
                config_node["Value_MHz"]["value"] = new_value
            elif "Value_toggle" in config_node:
                config_node["Value_toggle"]["value"] = new_value

            # Construct the simplified payload for the GUI
            simplified_payload = {
                "control_type": config_node["Value"].get("control_type") if "Value" in config_node else config_node["Value_dB"].get("control_type") if "Value_dB" in config_node else config_node["Value_MHz"].get("control_type") if "Value_MHz" in config_node else config_node["Value_toggle"].get("control_type") if "Value_toggle" in config_node else "_Label",
                "label": config_node["label"].get("value"),
                "value": new_value,
                "units": config_node["Value"].get("units", "") if "Value" in config_node else config_node["Value_dB"].get("units", "") if "Value_dB" in config_node else config_node["Value_MHz"].get("units", "") if "Value_MHz" in config_node else ""
            }
            
            # Publish to the new GUI topic
            gui_topic = f"{GUI_TOPIC_FILTER}/{PRESETS_SUBTOPIC}/{topic_path}"
            self.mqtt_util.publish_message(topic=gui_topic, value=json.dumps(simplified_payload))
            
            console_log(f"✅ Worker published simplified payload to '{gui_topic}'.")

        except Exception as e:
            debug_log(f"❌ Error processing config message for '{topic}': {e}", file=current_file, version=current_version)

    if __name__ == "__main__":
        class MockMqttController:
            def add_subscriber(self, topic_filter, callback_func):
                console_log(f"Mock subscribing to: {topic_filter}")
            def publish_message(self, topic, value, subtopic=None):
                console_log(f"Mock publishing to: {topic} with payload: {value}")
        
        class MockLogger:
            def debug_log(self, *args, **kwargs):
                pass
            def console_log(self, message):
                print(message)
        
        import sys
        sys.modules['workers.worker_logging'] = MockLogger
        
        mock_mqtt = MockMqttController()
        builder = ControlBuilderWorker(mqtt_util=mock_mqtt)
        
        mock_topic = f"{CONFIG_TOPIC_FILTER}/{PRESETS_SUBTOPIC}/PRESET_AMPLITUDE_REFERENCE_LEVEL/-120/Value_dB"
        mock_payload = '{"value": "-115"}'
        builder._on_config_message(mock_topic, mock_payload)