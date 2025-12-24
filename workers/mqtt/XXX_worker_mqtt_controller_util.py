# workers/worker_mqtt_controller_util.py
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
# Version 20250902.100615.5
# FIXED: The publish_message function now correctly handles boolean False values. The check
#        for a valid value has been updated to prevent False from being interpreted as a missing value.

import os
import inspect
import datetime
import paho.mqtt.client as mqtt
import threading
import orjson
import pathlib
import sys
import queue

# --- Module Imports ---
# Path manipulation is now handled by main.py
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.setup.app_constants import app_constants

print(f"DEBUG: Loading MqttControllerUtility from: {__file__}")

# --- Global Scope Variables (as per your instructions) ---
LOCAL_DEBUG_ENABLE = False




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
        
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢 Initializing the '{self.__class__.__name__}' utility class. Powering up the flux capacitor!",
              **_get_log_args()
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

            debug_log(message="✅ Celebration of success!", **_get_log_args())
        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}") # Always show errors
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    **_get_log_args()
                    
                )
            
    def add_subscriber(self, topic_filter: str, callback_func):
        """
        Stores a callback function for a given topic filter. Subscriptions are now
        processed in bulk after a successful connection.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # [A] First, we store the subscription request.
        self._subscribers[topic_filter] = callback_func
        
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢 Subscription request stored for topic filter: '{topic_filter}'.",
                **_get_log_args()
                
            )

        # [A] Only subscribe immediately if the client is already connected.
        if self.mqtt_client and self.mqtt_client.is_connected():
            self.mqtt_client.subscribe(topic_filter)
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🔍 Subscribed immediately to '{topic_filter}'.",
                    **_get_log_args()
                    
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
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🔵 MQTT client connected with rc={rc}. Subscribing to all topics!",
              **_get_log_args()
                
            )
        
        # [A] Subscribe to all stored topics on connection.
        if self._pending_subscriptions:
            for topic_filter in self._pending_subscriptions.keys():
                 client.subscribe(topic_filter)
            self._pending_subscriptions.clear()

        # We subscribe to a wildcard topic once to catch everything.
        client.subscribe("#")
        debug_log(message=f"✅ Connected to broker with rc={rc}", **_get_log_args()) # Informational

    def on_message(self, client, userdata, msg):
        """Callback for when an MQTT message is received."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        with self._pause_lock:
            if self._paused:
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"MQTT message for topic '{msg.topic}' received but processing is paused.",
                        **_get_log_args()
                        
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
                #    message=f"🟢️️️🔵 Dispatching message to subscriber for topic '{topic_filter}'.",
                #    file=current_file,
                #    version=current_version,
                #    function=f"{self.__class__.__name__}.on_message",
                #    
                #)
                callback_func(topic, payload)


    def connect_mqtt(self):
        """Connects the MQTT client to the broker in a separate thread."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢 ➡️➡️ '{current_function_name}' to connect MQTT client.",
              **_get_log_args()
                
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
            debug_log(message="✅ MQTT client connection initiated in a background thread.", **_get_log_args()) # Informational
        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}") # Always show errors
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    **_get_log_args()
                    
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
                    payload = orjson.dumps({"value": value})
                    self.mqtt_client.publish(full_topic, payload, retain=retain)
                    if app_constants.LOCAL_DEBUG_ENABLE: 
                        debug_log(message=f"Published to {full_topic}: {payload} with retain={retain}", **_get_log_args())
                else:
                    self._print_to_gui_console(f"❌ {NOT_CONNECTED_MSG}")
            except Exception as e:
                self._print_to_gui_console(f"❌ Error in _transmitter_thread: {e}")

    def show_topics(self):
        """Displays a list of all topics seen by the MQTT client."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢 ➡️➡️ '{current_function_name}' to display topics.",
              **_get_log_args()
                
            )
        try:
            if self.topics_seen:
                                debug_log(message=f"Observed Topics:\n{'\n'.join(sorted(self.topics_seen))}", **_get_log_args()) # Informational
            else:
                debug_log(message="⚠️ No topics observed yet.", **_get_log_args()) # Warning

        except Exception as e:
            self._print_to_gui_console(f"❌ Error in {current_function_name}: {e}") # Always show errors
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    **_get_log_args()
                    
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
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    **_get_log_args()
                    
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
            message=f"🟢️️️🟢 ➡️➡️ '{current_function_name}' to purge topics under '{base_topic}'.",
**_get_log_args()
            
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
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message="MQTT message processing paused.",
                    **_get_log_args()
                    
                )

    def resume(self):
        """
        Resumes the processing of incoming MQTT messages.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        with self._pause_lock:
            self._paused = False
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message="MQTT message processing resumed.",
                    **_get_log_args()
                    
                )