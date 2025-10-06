# managers/manager_presets_span.py
#
# A manager for handling span preset buttons and publishing the selected value to the
# main span frequency control.
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
# Version 20250904.124751.1

import os
import inspect
import json
import pathlib

# Assume these are imported from a central logging utility and MQTT controller
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250904.124751.1"
current_version_hash = (20250904 * 124751 * 1)
current_file = f"{os.path.basename(__file__)}"


class SpanSettingsManager:
    """
    Manages the logic for span presets.
    """

    def __init__(self, mqtt_controller: MqttControllerUtility):
        # Initializes the manager and subscribes to relevant topics.
        current_function_name = inspect.currentframe().f_code.co_name

        self.mqtt_controller = mqtt_controller
        self.base_topic = "OPEN-AIR/configuration/instrument/frequency"
        self.span_presets_topic = f"{self.base_topic}/Presets/fields/SPAN/options"
        self.target_span_topic = f"{self.base_topic}/Settings/fields/span_freq_MHz/value"

        # Dictionary to store preset values dynamically
        self.preset_values = {}

        debug_log(
            message=f"🛠️🟢 Initializing SpanSettingsManager and setting up subscriptions.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        self._load_preset_values()
        self._subscribe_to_topics()

    def _load_preset_values(self):
        """
        Loads the preset values directly from the configuration file.
        This makes the manager self-sufficient and prevents timing issues.
        """
        try:
            # FIX: Replaced fragile os.path.join with a robust pathlib implementation.
            current_dir = pathlib.Path(__file__).parent
            config_file_path = current_dir.parent / "datasets" / "dataset_configuration_instrument_frequency.json"

            if not config_file_path.is_file():
                debug_log(
                    message=f"❌ Configuration file not found at '{config_file_path}'. Cannot load presets.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}._load_preset_values",
                    console_print_func=console_log
                )
                return

            with open(config_file_path, 'r') as f:
                config_data = json.load(f)

            span_options = config_data.get("Presets", {}).get("fields", {}).get("SPAN", {}).get("options", {})
            for key, option in span_options.items():
                self.preset_values[int(key)] = float(option.get('value'))

            debug_log(
                message=f"💾 Successfully loaded {len(self.preset_values)} span preset values.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._load_preset_values",
                console_print_func=console_log
            )

        except Exception as e:
            debug_log(
                message=f"🛠️🔴 Failed to load preset values from file. The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}._load_preset_values",
                console_print_func=console_log
            )


    def _subscribe_to_topics(self):
        # Subscribes to the preset topics.
        current_function_name = inspect.currentframe().f_code.co_name

        # Subscribe only to the 'selected' topics, as we no longer need the 'value' topics.
        for i in range(1, 8):
            self.mqtt_controller.add_subscriber(topic_filter=f"{self.span_presets_topic}/{i}/selected", callback_func=self._on_preset_message)

            debug_log(
                message=f"🔍 Subscribed to span preset topics for option {i}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_preset_message(self, topic, payload):
        # The main message processing callback for presets.
        current_function_name = inspect.currentframe().f_code.co_name

        try:
            parsed_payload = json.loads(payload)
            value = parsed_payload.get('value', payload)

            if topic.endswith("/selected") and str(value).lower() == 'true':
                self._update_span_from_preset(topic=topic)

            console_log("✅ Celebration of success! The span settings did synchronize!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The span preset logic has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _update_span_from_preset(self, topic):
        # Extracts the value from the preset topic and updates the main span topic.
        current_function_name = inspect.currentframe().f_code.co_name

        try:
            option_number = int(topic.split('/')[-2])
            new_span_value = self.preset_values.get(option_number)

            if new_span_value is not None:
                self._publish_update(topic=self.target_span_topic, value=new_span_value)
                debug_log(
                    message=f"🔁 Preset selected! Published new span value to '{self.target_span_topic}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            else:
                debug_log(
                    message=f"🟡 Warning: Preset value for option {option_number} has not been received yet.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

        except Exception as e:
            debug_log(
                message=f"🛠️🔴 Failed to apply preset from topic '{topic}'. The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_update(self, topic, value):
        # Publishes a message to the specified topic.
        current_function_name = inspect.currentframe().f_code.co_name

        rounded_value = round(value, 3)

        debug_log(
            message=f"💾 Publishing new value '{rounded_value}' to topic '{topic}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        self.mqtt_controller.publish_message(
            topic=topic,
            subtopic="",
            value=rounded_value,
            retain=False
        )