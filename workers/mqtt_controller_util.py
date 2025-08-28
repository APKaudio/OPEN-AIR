# utils/mqtt_controller_util.py
#
# A utility module to handle the logic for interfacing with an external MQTT broker.
# This version refactors the client to centrally manage subscriptions and dispatch messages.
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
# Version 20250827.185300.1

import os
import inspect
import datetime
import paho.mqtt.client as mqtt
import threading
import json
import pathlib
import sys

# --- Module Imports ---
# Path manipulation is now handled by main.py
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables (as per your instructions) ---
current_version = "20250827.185300.1"
current_version_hash = (20250827 * 185300 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constant Variables (No Magic Numbers) ---
# MQTT Broker settings
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
BROKER_TIMEOUT = 60
# Logging messages and colors
BROKER_RUNNING_MSG = "Broker is running"
BROKER_NOT_RUNNING_MSG = "Broker is not running"
NOT_CONNECTED_MSG = "Not connected to broker."
NO_TOPIC_OR_VALUE_MSG = "Please enter a topic and a value."


class MqttControllerUtility:
    """
    Manages all communication logic for the MQTT broker and client.
    This class is the central point for all functions to push a message or subscribe to messages.
    It adheres to the "Utilities" layer principles of your protocol.
    """
    def __init__(self, print_to_gui_func, log_treeview_func):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🛠️🟢 Initializing the '{self.__class__.__name__}' utility class. Powering up the flux capacitor!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=print_to_gui_func
        )
        
        try:
            # --- Function logic goes here ---
            self.mqtt_client = None
            self._print_to_gui_console = print_to_gui_func
            self._log_to_treeview = log_treeview_func
            self.topics_seen = set()
            self._subscribers = {} # A new dictionary to hold subscribers and their callbacks

            console_log("✅ Celebration of success!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            
    def add_subscriber(self, topic_filter: str, callback_func):
        """Adds a callback function to be triggered for a specific topic filter."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 New subscriber added for topic filter: '{topic_filter}'.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=self._print_to_gui_console
        )
        self._subscribers[topic_filter] = callback_func
        # This is the single place we subscribe to a topic.
        self.mqtt_client.subscribe(topic_filter)
        debug_log(
            message=f"🛠️🟢 New subscriber added for topic filter: '{topic_filter}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.add_subscriber",
            console_print_func=self._print_to_gui_console
        )


    def check_status(self):
        """Checks and reports the status of the Mosquitto broker."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to check broker status.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            if self.mqtt_client.is_connected():
                console_log(f"✅ {BROKER_RUNNING_MSG}")
            else:
                console_log(f"❌ {BROKER_NOT_RUNNING_MSG}")
        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the MQTT client connects to the broker."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
      #  debug_log(
      #      message=f"🛠️🔵 MQTT client connected with rc={rc}. Subscribing to all topics!",
      #      file=current_file,
      #      version=current_version,
      #      function=f"{self.__class__.__name__}.{current_function_name}",
      #      console_print_func=self._print_to_gui_console
      #  )
        # We subscribe to a wildcard topic once to catch everything.
        client.subscribe("#")
        self._print_to_gui_console(f"Connected to broker with rc={rc}")

    def on_message(self, client, userdata, msg):
        """Callback for when an MQTT message is received."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # We process the message payload here for all listeners
        topic = msg.topic
        payload = msg.payload.decode()
        self.topics_seen.add(topic)
        
        # Now we dispatch the message to all registered subscribers.
        # FIX: Iterate over a copy of the dictionary to prevent RuntimeError.
        for topic_filter, callback_func in list(self._subscribers.items()):
            # The paho-mqtt library provides a topic_matches_sub function to check for wildcards.
            if mqtt.topic_matches_sub(topic_filter, topic):
                #debug_log(
                #    message=f"🛠️🔵 Dispatching message to subscriber for topic '{topic_filter}'.",
                #    file=current_file,
                #    version=current_version,
                #    function=f"{self.__class__.__name__}.on_message",
                #    console_print_func=self._print_to_gui_console
                #)
                callback_func(topic, payload)


    def connect_mqtt(self):
        """Connects the MQTT client to the broker in a separate thread."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to connect MQTT client.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.connect(host=BROKER_ADDRESS, port=BROKER_PORT, keepalive=BROKER_TIMEOUT)
            
            thread = threading.Thread(target=self.mqtt_client.loop_forever, daemon=True)
            thread.start()
            self._print_to_gui_console("✅ MQTT client connection initiated in a background thread.")

        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )

    def show_topics(self):
        """Displays a list of all topics seen by the MQTT client."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to display topics.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            if self.topics_seen:
                topics_str = "\n".join(sorted(self.topics_seen))
                self._print_to_gui_console(f"Observed Topics:\n{topics_str}")
            else:
                self._print_to_gui_console("⚠️ No topics observed yet.")

        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )

    def publish_message(self, topic: str, subtopic: str, value, retain=False):
        """Publishes a message to a topic via the MQTT client, with an optional retain flag."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        #debug_log(
        #    message=f"🛠️🟢 Entering '{current_function_name}' to publish a message.",
        #    file=current_file,
        #    version=current_version,
        #    function=f"{self.__class__.__name__}.{current_function_name}",
        #    console_print_func=self._print_to_gui_console
        #)
        try:
            if not topic or not value:
                self._print_to_gui_console(f"❌ {NO_TOPIC_OR_VALUE_MSG}")
                return

            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            payload = json.dumps({"value": value})

            if self.mqtt_client:
                # The key change is here: adding the `retain=retain` argument.
                self.mqtt_client.publish(full_topic, payload, retain=retain)
                self._print_to_gui_console(f"Published to {full_topic}: {payload} with retain={retain}")
#                console_log(f"✅ Published message to topic '{full_topic}' with retain flag set to '{retain}'.")
            else:
                self._print_to_gui_console(f"❌ {NOT_CONNECTED_MSG}")

        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )