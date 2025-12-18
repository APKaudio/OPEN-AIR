# workers/worker_mqtt_controller_util.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20250902.100615.5
# FIXED: The publish_message function now correctly handles boolean False values. The check
#        for a valid value has been updated to prevent False from being interpreted as a missing value.

import os
import inspect
import datetime
import paho.mqtt.client as mqtt
import threading
import json
import pathlib
import sys
import queue

# --- Module Imports ---
# Path manipulation is now handled by main.py
from display.logger import debug_log, console_log, log_visa_command

print(f"DEBUG: Loading MqttControllerUtility from: {__file__}")

# --- Global Scope Variables (as per your instructions) ---
current_version = "20251213.000000.1" # Updated version based on current date
current_version_hash = (20251213 * 0 * 1) # Updated hash
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\\\", "/")
Local_Debug_Enable = True




# --- Constant Variables (No Magic Numbers) ---
# MQTT Broker settings
#BROKER_ADDRESS = "44.44.44.159"
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
        
        if Local_Debug_Enable:
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
            # [A] New list to store pending subscriptions before connection is made.
            self._pending_subscriptions = {}
            self.publish_queue = queue.Queue()
            self._paused = False
            self._pause_lock = threading.Lock()

            console_log("✅ Celebration of success!")
        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}") # Always show errors
            if Local_Debug_Enable:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )
            
    def add_subscriber(self, topic_filter: str, callback_func):
        """
        Stores a callback function for a given topic filter. Subscriptions are now
        processed in bulk after a successful connection.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # [A] First, we store the subscription request.
        self._subscribers[topic_filter] = callback_func
        
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Subscription request stored for topic filter: '{topic_filter}'.",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=self._print_to_gui_console
            )

        # [A] Only subscribe immediately if the client is already connected.
        if self.mqtt_client and self.mqtt_client.is_connected():
            self.mqtt_client.subscribe(topic_filter)
            if Local_Debug_Enable:
                debug_log(
                    message=f"🔍 Subscribed immediately to '{topic_filter}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.add_subscriber",
                    console_print_func=self._print_to_gui_console
                )
        # [A] If not connected, add it to the pending list for later.
        else:
            self._pending_subscriptions[topic_filter] = callback_func

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the MQTT client connects to the broker.
        We now subscribe to all stored topics here.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🔵 MQTT client connected with rc={rc}. Subscribing to all topics!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
        
        # [A] Subscribe to all stored topics on connection.
        if self._pending_subscriptions:
            for topic_filter in self._pending_subscriptions.keys():
                 client.subscribe(topic_filter)
            self._pending_subscriptions.clear()

        # We subscribe to a wildcard topic once to catch everything.
        client.subscribe("#")
        console_log(f"✅ Connected to broker with rc={rc}") # Informational

    def on_message(self, client, userdata, msg):
        """Callback for when an MQTT message is received."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        with self._pause_lock:
            if self._paused:
                if Local_Debug_Enable:
                    debug_log(
                        message=f"MQTT message for topic '{msg.topic}' received but processing is paused.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=self._print_to_gui_console
                    )
                return # Do not process message if paused

        # We process the message payload here for all listeners
        topic = msg.topic
        payload = msg.payload.decode()
        self.topics_seen.add(topic)
        
        # Now we dispatch the message to all registered subscribers.
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
        if Local_Debug_Enable:
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
            
            receiver_thread = threading.Thread(target=self.mqtt_client.loop_forever, daemon=True)
            receiver_thread.start()

            transmitter_thread = threading.Thread(target=self._transmitter_thread, daemon=True)
            transmitter_thread.start()
            console_log("✅ MQTT client connection initiated in a background thread.") # Informational
        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}") # Always show errors
            if Local_Debug_Enable:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )

    def _transmitter_thread(self):
        """
        A thread that continuously gets messages from the publish queue and publishes them.
        """
        while True:
            try:
                topic, subtopic, value, retain = self.publish_queue.get()
                if self.mqtt_client and self.mqtt_client.is_connected():
                    full_topic = f"{topic}/{subtopic}" if subtopic else topic
                    payload = json.dumps({"value": value})
                    self.mqtt_client.publish(full_topic, payload, retain=retain)
                    if Local_Debug_Enable:
                        console_log(f"Published to {full_topic}: {payload} with retain={retain}")
                else:
                    self._print_to_gui_console(f"❌ {NOT_CONNECTED_MSG}")
            except Exception as e:
                self._print_to_gui_console(f"❌ Error in _transmitter_thread: {e}")

    def show_topics(self):
        """Displays a list of all topics seen by the MQTT client."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Entering '{current_function_name}' to display topics.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
        try:
            if self.topics_seen:
                                console_log(f"Observed Topics:\n{'\n'.join(sorted(self.topics_seen))}") # Informational
            else:
                console_log("⚠️ No topics observed yet.") # Warning

        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}") # Always show errors
            if Local_Debug_Enable:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )

    def publish_message(self, topic: str, subtopic: str, value, retain=False):
        """Puts a message into the publish queue."""
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            if not topic or (value is None and value != False and value != 0):
                self._print_to_gui_console(f"❌ {NO_TOPIC_OR_VALUE_MSG}")
                return
            self.publish_queue.put((topic, subtopic, value, retain))
        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )

    def subscribe_to_topic(self, topic, callback):
        # Subscribes to a given topic and registers a callback.
        # [A] The old logic here is no longer needed. The on_connect callback handles subscriptions.
        # [A] This method existed as a simple wrapper. The core logic has been moved to add_subscriber and on_connect.
        pass

    def purge_branch(self, base_topic):
        """Publishes a null, retained payload to all seen topics under a base topic."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to purge topics under '{base_topic}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            if self.mqtt_client and self.mqtt_client.is_connected():
                
                topics_to_purge = [t for t in self.topics_seen if t.startswith(base_topic)]
                
                if not topics_to_purge:
                    # Also try to purge the base topic itself just in case
                    self.mqtt_client.publish(base_topic, payload=b'', retain=True)
                
                for topic in topics_to_purge:
                    self.mqtt_client.publish(topic, payload=b'', retain=True)

                self._print_to_gui_console(f"✅ Purge signal sent for {len(topics_to_purge)} topics under '{base_topic}'.")

            else:
                self._print_to_gui_console(f"❌ {NOT_CONNECTED_MSG}")

        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}")

    def pause(self):
        """
        Pauses the processing of incoming MQTT messages.
        Messages will still be received by the client but not processed by the callbacks.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        with self._pause_lock:
            self._paused = True
            if Local_Debug_Enable:
                debug_log(
                    message="MQTT message processing paused.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )

    def resume(self):
        """
        Resumes the processing of incoming MQTT messages.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        with self._pause_lock:
            self._paused = False
            if Local_Debug_Enable:
                debug_log(
                    message="MQTT message processing resumed.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=self._print_to_gui_console
                )