# workers/worker_mqtt_data_flattening.py
#
# A utility module to flatten and pivot nested JSON data from MQTT payloads.
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
# Version 20250824.210000.5

import inspect
import os
import pathlib
import datetime
from collections import defaultdict
import json

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables (as per your instructions) ---
CURRENT_DATE = 20250824
CURRENT_TIME = 210000
CURRENT_TIME_HASH = 210000
REVISION_NUMBER = 5
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"{os.path.basename(__file__)}"


class MqttDataFlattenerUtility:
    """
    Manages the flattening and pivoting of nested data structures from MQTT payloads
    into a format suitable for GUI display or CSV export.
    """
    def __init__(self, print_to_gui_func):
        self._print_to_gui_console = print_to_gui_func
        self.current_class_name = self.__class__.__name__
        self.data_buffer = {}

    def _rebuild_nested_from_dict(self, target_dict: dict, path_list: list, value: any):
        """
        Helper function to rebuild a nested dictionary from a list of keys.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🛠️🔵 Rebuilding nested dictionary from path: {path_list}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )

        current = target_dict
        for i, key in enumerate(path_list):
            if i == len(path_list) - 1:
                # Attempt to parse payload as JSON, otherwise keep as string
                try:
                    current[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    current[key] = value
            else:
                current = current.setdefault(key, {})

    def _flatten_data(self, data: dict, parent_key: str = '', sep: str = '/') -> dict:
        """
        Flattens a nested dictionary recursively.
        """
        items = {}
        for k, v in data.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_data(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items

    def _pivot_flattened_data(self, flattened_data: dict, truncation_prefix: str) -> list:
        """
        Pivots the flattened data into a list of rows for display based on the presence of '_'.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        pivoted_rows = []
        rows_by_topic = defaultdict(dict)
        
        for key, value in flattened_data.items():
            topic_parts = key.split('/')
            
            # Find the index of the first underscore, if it exists
            underscore_index = -1
            for i, part in enumerate(topic_parts):
                if '_' in part:
                    underscore_index = i
                    break
            
            if underscore_index != -1:
                # If an underscore is found, use that part as the pivoting point
                base_topic_parts = topic_parts[:underscore_index]
                base_topic = '/'.join(base_topic_parts)
                column_key = '/'.join(topic_parts[underscore_index:])
            else:
                # If no underscore, group by the full topic path for individual entries
                base_topic = key
                column_key = 'Value'
            
            # Log the processing logic for this key
            debug_log(
                message=f"🔍 Processed key '{key}'. Nodes: {len(topic_parts)}. Underscore found at depth: {underscore_index}. Base topic: '{base_topic}'. Column key: '{column_key}'.",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )

            rows_by_topic[base_topic][column_key] = value
        
        # The order of the columns needs to be consistent
        standard_headers = []

        for topic, values_dict in rows_by_topic.items():
            row_dict = {}
            full_topic = topic
            
            # FIX: Properly handle the Parameter column by stripping the prefix
            if topic.startswith(truncation_prefix):
                parameter = topic[len(truncation_prefix):]
            else:
                parameter = topic
                
            row_dict["Topic"] = full_topic
            row_dict["Parameter"] = parameter
            
            # Handle the rest of the columns, including the dynamically pivoted ones
            for header in standard_headers[2:]:
                row_dict[header] = values_dict.pop(header, "N/A")

            # Add any remaining keys from the pivoted data
            row_dict.update(values_dict)
            
            pivoted_rows.append(row_dict)

        # Log the final pivoted output
        debug_log(
            message=f"📊 Final pivoted output returned to GUI: {json.dumps(pivoted_rows, indent=4)}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
            
        return pivoted_rows

    def flatten_and_pivot_data(self, data: dict, topic_prefix: str) -> list:
        """
        Main entry point for data flattening and pivoting.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Unlocking the mysteries of nested data! Prepare for a glorious flattening! We got the data! 🎣",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )

        try:
            # Rebuild the nested data from the flat topic:payload pairs
            rebuilt_data = {}
            for topic, payload in data.items():
                self._rebuild_nested_from_dict(rebuilt_data, topic.split('/'), payload)
            
            # Now, flatten and pivot the rebuilt data
            flattened_data = self._flatten_data(rebuilt_data)
            pivoted_rows = self._pivot_flattened_data(flattened_data, topic_prefix)
            
            console_log(f"✅ Successfully processed {len(pivoted_rows)} commands into a beautiful table.")
            return pivoted_rows
        
        except Exception as e:
            console_log(f"❌ Failed to parse MQTT data. Error: {e}")
            debug_log(
                message=f"❌🔴 Oh, dear! The data wrangling has gone terribly awry! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            return []

    def process_mqtt_message_and_pivot(self, topic: str, payload: str, topic_prefix: str) -> list:
        """
        Receives and buffers a single MQTT message. Returns pivoted data only when a full
        transaction is detected.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🛠️🔵 Processing single MQTT message. Buffering: '{topic}' with payload '{payload}'",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )

        self.data_buffer[topic] = payload

        # Heuristic to detect the end of a message series.
        if topic.endswith('validated_value') or len(self.data_buffer) > 15: # Arbitrary number for demonstration
            console_log("Received a complete transaction. Now processing the buffer...")
            rebuilt_data = {}
            for t, p in self.data_buffer.items():
                self._rebuild_nested_from_dict(rebuilt_data, t.split('/'), p)

            flattened_data = self._flatten_data(rebuilt_data)
            pivoted_rows = self._pivot_flattened_data(flattened_data, topic_prefix)
            self.data_buffer = {} # Clear the buffer after processing
            return pivoted_rows
        
        return []
