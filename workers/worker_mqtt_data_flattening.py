# workers/worker_mqtt_data_flattening.py
#
# A utility module to process and flatten nested MQTT payloads into a format
# suitable for display in a flat table or export to CSV. It buffers incoming
# messages until a complete set is received, then pivots the data.
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
# Version 20250824.211334.6

import os
import inspect
import json

# --- Module Imports ---
from .worker_logging import debug_log, console_log

# --- Global Scope Variables (as per your instructions) ---
current_version = "20250824.211334.6"
current_version_hash = 25678125835296
current_file = f"{os.path.basename(__file__)}"


class MqttDataFlattenerUtility:
    """
    Manages the buffering and flattening of incoming MQTT messages.
    """
    def __init__(self, print_to_gui_func):
        self._print_to_gui_console = print_to_gui_func
        self.data_buffer = {}
        self.current_class_name = self.__class__.__name__

    def clear_buffer(self):
        """
        Clears the internal data buffer.
        """
        debug_log(
            message="🛠️🔍 The data buffer has been wiped clean. A fresh start for our experiments!",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.clear_buffer",
            console_print_func=self._print_to_gui_console
        )
        self.data_buffer = {}

    def process_mqtt_message_and_pivot(self, topic: str, payload: str, topic_prefix: str) -> list:
        """
        Processes a single MQTT message. If it's the last message in a set,
        it flattens the buffered data and returns a list of dictionaries.

        Args:
            topic (str): The MQTT topic of the message.
            payload (str): The JSON payload of the message.
            topic_prefix (str): The root topic to be used for filtering.

        Returns:
            list: A list of dictionaries representing the flattened, pivoted data,
                  or an empty list if not all messages have been received.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🔵 Received data for '{topic}'. Storing in buffer. Payload: {payload}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )

        try:
            data = json.loads(payload)
            self.data_buffer[topic] = data

            if topic.endswith('validated_value'):
                debug_log(
                    message=f"🛠️🟢 Full data set received. Commencing pivoting and flattening!",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )
                
                flattened_data = {}
                
                # Use a more robust approach to determine the parameter path and key-value pairs
                try:
                    # Strip the topic prefix
                    parameter_path_full = topic.replace(f"{topic_prefix}/", "", 1)
                    
                    # Split the path into parts, and the last part is the key (e.g., 'validated_value')
                    path_parts = parameter_path_full.rsplit('/', 1)
                    if len(path_parts) == 2:
                        parameter_path, final_key = path_parts
                        flattened_data['Parameter'] = parameter_path
                    else:
                        # Fallback in case of unexpected topic format
                        flattened_data['Parameter'] = parameter_path_full
                        final_key = ""

                    # Iterate through the buffered data and process each key-value pair
                    for t, p in self.data_buffer.items():
                        key = t.rsplit('/', 1)[-1]
                        
                        value = None
                        if isinstance(p, dict) and 'value' in p:
                            value = p['value']
                        elif isinstance(p, str):
                            value = p
                        
                        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                            value = value.strip('"')
                        
                        if value is not None:
                            flattened_data[key] = value

                except Exception as e:
                    console_log(f"❌ Error during data pivoting: {e}")
                    debug_log(
                        message=f"🛠️🔴 An unholy terror! An error has occurred during data pivoting! The error be: {e}",
                        file=current_file,
                        version=current_version,
                        function=f"{self.current_class_name}.{current_function_name}",
                        console_print_func=self._print_to_gui_console
                    )
                    self.clear_buffer()
                    return []
                
                self.clear_buffer()
                
                debug_log(
                    message="🛠️✅ Behold! I have transmogrified the data! The final payload is below.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )
                
                console_log(json.dumps(flattened_data, indent=2))

                return [flattened_data]
            
            return []
            
        except json.JSONDecodeError as e:
            console_log(f"❌ Error decoding JSON payload for topic '{topic}': {e}")
            debug_log(
                message=f"🛠️🔴 The JSON be a-sailing to its doom! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            return []
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            return []