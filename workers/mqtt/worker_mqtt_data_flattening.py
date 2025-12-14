# workers/worker_mqtt_data_flattening.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20250825.151032.21

import os
import inspect
import json

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command

# --- Global Scope Variables ---
CURRENT_DATE = 20250825
CURRENT_TIME = 151032
CURRENT_TIME_HASH = 151032
REVISION_NUMBER = 21
current_version = "20250825.151032.21"
current_version_hash = 63895914278400
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = True


class MqttDataFlattenerUtility:
    """
    Manages the buffering and flattening of incoming MQTT messages based on dynamic
    topic identifiers.
    """
    def __init__(self, print_to_gui_func):
        self._print_to_gui_console = print_to_gui_func
        self.data_buffer = {}
        self.current_class_name = self.__class__.__name__
        self.last_unique_identifier = None
        self.FLUSH_COMMAND = "FLUSH_BUFFER"

    def clear_buffer(self):
        """
        Clears the internal data buffer.
        """
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🔍 The data buffer has been wiped clean. A fresh start for our experiments!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.clear_buffer",
                console_print_func=self._print_to_gui_console
            )
        self.data_buffer = {}
        self.last_unique_identifier = None

    def process_mqtt_message_and_pivot(self, topic: str, payload: str, topic_prefix: str) -> list:
        """
        Processes a single MQTT message. It triggers flattening when it detects the
        start of a new data set based on the unique identifier.

        Args:
            topic (str): The MQTT topic of the message.
            payload (str): The JSON payload of the message.
            topic_prefix (str): The root topic to be used for filtering.

        Returns:
            list: A list of dictionaries representing the flattened, pivoted data,
                  or an empty list if not all messages have been received.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        # Check for the manual flush command
        if payload == self.FLUSH_COMMAND:
            if self.data_buffer:
                return self._flush_buffer()
            else:
                if Local_Debug_Enable:
                    debug_log(
                        message="🛠️🟡 Flush command received, but buffer is empty. Nothing to do.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=self._print_to_gui_console
                    )
                return []
        
        try:
            data = json.loads(payload)
            
            # --- Corrected logic for 'Active' status check ---
            if topic.endswith('/Active') and isinstance(data, dict) and data.get('value') == 'false':
                console_log(f"🟡 Skipping transaction for '{topic}' because 'Active' is false.")
                self.clear_buffer()
                return []
            
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔵 Received data for '{topic}'. Storing in buffer. Payload: {payload}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )

            # Extract the unique data set identifier (the second-to-last node)
            relative_topic = topic.replace(f"{topic_prefix}/", "", 1)
            identifier_path = relative_topic.rsplit('/', 1)[0]
            
            # This is the primary trigger for a new data set.
            if self.last_unique_identifier and identifier_path != self.last_unique_identifier:
                return self._flush_buffer(new_topic=topic, new_data=data, new_identifier=identifier_path)

            
            # If this is the very first message, set the first key name and buffer it
            if self.last_unique_identifier is None:
                self.last_unique_identifier = identifier_path

            # Add the message to the buffer
            self.data_buffer[topic] = data

            return []
            
        except json.JSONDecodeError as e:
            console_log(f"❌ Error decoding JSON payload for topic '{topic}': {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 The JSON be a-sailing to its doom! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )
            self.clear_buffer()
            return []
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 Arrr, the code be capsized! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )
            self.clear_buffer()
            return []

    def _flush_buffer(self, new_topic=None, new_data=None, new_identifier=None):
        """
        Processes and flattens the current buffer.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        if Local_Debug_Enable:
            debug_log(
                message="🛠️🟢 Processing buffer and commencing pivoting and flattening!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
        
        flattened_data = {}
        flattened_data['Parameter'] = self.last_unique_identifier
        
        for t, p in self.data_buffer.items():
            data_key = t.rsplit('/', 1)[-1]
            
            value = None
            if isinstance(p, dict) and 'value' in p:
                value = p['value']
            elif isinstance(p, str):
                value = p
            
            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                value = value.strip('"')
            
            if value is not None:
                flattened_data[data_key] = value

        self.clear_buffer()
        
        if new_topic and new_data:
            self.data_buffer[new_topic] = new_data
            self.last_unique_identifier = new_identifier
        
        if Local_Debug_Enable:
            debug_log(
                message="🛠️✅ Behold! I have transmogrified the data! The final payload is below.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
        
        console_log(json.dumps(flattened_data, indent=2))
        return [flattened_data]