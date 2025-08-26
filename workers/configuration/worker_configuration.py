MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/Application/#"
# agents/agent_configuration.py
#
# A standalone agent to subscribe to the MQTT topic "OPEN-AIR/program/configuration/Application/"
# and save all received JSON data to a local file named Config.json.
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
# Version 20250824.235500.1

# 📚 Standard Library Imports
import os
import inspect
import datetime
import threading
import time
import sys
import json
import paho.mqtt.client as mqtt

# 🚀 Project-Specific Imports
# Assuming the root directory is on the path, import from there
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)
except Exception as e:
    print(f"Error adding project root to sys.path: {e}")

from workers.mqtt_controller_util import MqttControllerUtility
from workers.worker_logging import debug_log, console_log


# --- Global Scope Variables ---
CURRENT_DATE = 20250824
CURRENT_TIME = 235500
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * int(CURRENT_TIME) * int(REVISION_NUMBER))
current_file = f"{os.path.basename(__file__)}"

# --- Constant Variables (No Magic Numbers) ---

CONFIG_FILE_NAME = "Config.json"

class ConfigurationAgent:
    """
    This agent subscribes to an MQTT topic and saves all received payloads to a local JSON file.
    """
    def __init__(self):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Configuration Agent is being initialized. Ready to receive data!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        # We need a mock for the app instance to use the existing utilities correctly.
        class MockAppInstance:
            def __init__(self):
                self.config = {}
        self.app_instance = MockAppInstance()
        self.mqtt_util = MqttControllerUtility(console_log, self.log_to_table)
        self.output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_NAME)
        self.data = {}
        
    def log_to_table(self, topic, payload):
        # A placeholder function to fulfill the requirement of MqttControllerUtility.
        # For this standalone script, we'll just log to the console.
        console_log(f"Received message on topic: {topic} with payload: {payload}")

    def on_connect(self, client, userdata, flags, rc):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🔵 MQTT client connected with rc={rc}. Subscribing to '{MQTT_TOPIC_FILTER}'!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        if rc == 0:
            client.subscribe(MQTT_TOPIC_FILTER)
            console_log(f"✅ Subscribed to topic: {MQTT_TOPIC_FILTER}")
        else:
            console_log(f"❌ Failed to connect to MQTT broker, return code {rc}.")

    def on_message(self, client, userdata, msg):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🔵 Received MQTT message on topic '{msg.topic}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # 1. Load existing data from the file if it exists
            if os.path.exists(self.output_file_path):
                with open(self.output_file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            
            # 2. Update data with new payload
            payload_data = json.loads(msg.payload.decode('utf-8'))
            self.data.update(payload_data)
            
            # 3. Save the updated data back to the file
            with open(self.output_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)

            console_log(f"✅ Successfully saved data from topic '{msg.topic}' to '{self.output_file_path}'.")
            debug_log(
                message=f"🐐💾 Saved data from topic '{msg.topic}' to file. The changes are locked in!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        except json.JSONDecodeError as e:
            console_log(f"❌ Failed to decode JSON payload from topic '{msg.topic}': {e}.")
            debug_log(
                message=f"🐐🔴 Arrr, the payload be gibberish! Error: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        except Exception as e:
            console_log(f"❌ An error occurred while processing the message: {e}.")
            debug_log(
                message=f"🐐🔴 An unexpected error occurred: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def run(self):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Starting agent's main loop. This is the big moment!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            client = mqtt.Client()
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            
            # We don't use the wrapper class's connect method here because we need
            # to provide our own callbacks.
            client.connect("localhost", 1883, 60)
            
            client.loop_forever()

        except Exception as e:
            console_log(f"❌ A critical error occurred in the agent's main loop: {e}.")
            debug_log(
                message=f"🐐🔴 A critical error occurred: {e}. The whole operation has been capsized!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

def main():
    """Main execution function for the standalone agent."""
    agent = ConfigurationAgent()
    agent.run()

if __name__ == "__main__":
    main()
