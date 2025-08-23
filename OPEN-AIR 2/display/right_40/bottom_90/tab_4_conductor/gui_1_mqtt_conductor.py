# tabs/conductor/gui_mqtt_conductor.py
#
# This file defines a GUI component for managing and testing an MQTT broker and client.
# It handles starting/stopping the mosquitto broker and provides an interface for
# publishing and subscribing to topics.
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
# Version 20250822.213000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import sys
import pathlib

# --- Module Imports ---
# 🏡 We need to add the parent directory to the path so our code can find the 'styling'
# and 'configuration' modules, as they are siblings to the 'display' directory.
if str(pathlib.Path(__file__).resolve().parent.parent.parent) not in sys.path:
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))

# Now that the path is set, we can confidently import our logging module!
from configuration.logging import debug_log, console_log
from styling.style import THEMES, DEFAULT_THEME

# MQTT libraries for client and process management.
import paho.mqtt.client as mqtt

# --- Global Scope Variables ---
# ⏰ As requested, the version is now hardcoded to the time this file was generated.
# The version strings and numbers below are static and will not change at runtime.
# This represents the date (YYYYMMDD) of file creation.
CURRENT_DATE = 20250822
# This represents the time (HHMMSS) of file creation.
CURRENT_TIME = 213000
# This is a numeric hash of the time, useful for unique IDs.
CURRENT_TIME_HASH = 213000
# Our project's current revision number, which is manually incremented.
REVISION_NUMBER = 1
# Assembling the full version string as per the protocol (W.X.Y).
current_version = "20250822.213000.1"
# Creating a unique integer hash for the current version for internal tracking.
current_version_hash = (CURRENT_DATE * CURRENT_TIME_HASH * REVISION_NUMBER)
# Getting the name of the current file to use in our logs, ensuring it's always accurate.
current_file = f"{os.path.basename(__file__)}"

# --- Constant Variables (No Magic Numbers) ---
# MQTT Broker settings
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
BROKER_TIMEOUT = 60

# Text for UI elements
START_BROKER_TEXT = "Start Mosquitto"
STOP_BROKER_TEXT = "Stop Mosquitto"
CHECK_STATUS_TEXT = "Check Status"
CONNECT_MQTT_TEXT = "Connect MQTT"
SHOW_TOPICS_TEXT = "Show Topics"
PUBLISH_FRAME_TEXT = "Publish Message"
TOPIC_LABEL_TEXT = "Topic:"
MESSAGE_LABEL_TEXT = "Message:"
PUBLISH_BUTTON_TEXT = "Publish"

# Logging messages and colors
BROKER_RUNNING_MSG = "Broker is running"
BROKER_NOT_RUNNING_MSG = "Broker is not running"
BROKER_ALREADY_RUNNING_MSG = "Mosquitto is already running!"
FAILED_TO_START_BROKER_MSG = "Failed to start mosquitto process: "
BROKER_STOPPED_MSG = "Broker stopped"
NOT_CONNECTED_MSG = "Not connected to broker."


class MqttConductorFrame(ttk.Frame):
    """
    A GUI frame for controlling and monitoring a local MQTT broker.

    This class encapsulates the UI elements for starting/stopping the Mosquitto
    broker and provides a simple client for publishing and subscribing to topics.
    """
    # ⚠️ PROTOCOL NOTE: This class currently contains both GUI logic and business logic
    # for interacting with the MQTT broker. For future refactoring, this logic
    # should be moved to a dedicated utility file to adhere to the separation of
    # concerns principle.
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the MQTT Conductor Frame.

        Args:
            parent: The parent widget for this frame.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🐐🟢 Initializing the '{self.__class__.__name__}' GUI frame.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            super().__init__(parent, *args, **kwargs)

            # Instance variables to manage the state of the broker and client.
            self.mosquitto_process = None
            self.mqtt_client = None
            self.topics_seen = set()
            
            # Apply the theme from our style.py file.
            self.theme_colors = self._apply_styles(theme_name=DEFAULT_THEME)

            self.create_widgets()

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        
        Args:
            theme_name (str): The name of the theme to apply.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to apply styling.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            colors = THEMES.get(theme_name, THEMES["dark"])
            style = ttk.Style(self)
            style.theme_use("clam")
            
            style.configure('TFrame', background=colors["bg"])
            style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
            style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
            style.configure('TButton', background=colors["accent"], foreground=colors["text"])
            style.configure('TEntry', fieldbackground=colors["primary"], foreground=colors["fg"])
            style.configure('ScrolledText', background=colors["primary"], foreground=colors["fg"])

            console_log("✅ Celebration of success!")
            return colors
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return THEMES["dark"]

    def create_widgets(self):
        """
        Creates all the UI widgets for the tab.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to create widgets.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # Main button frame for broker controls
            button_frame = ttk.Frame(self)
            button_frame.pack(pady=10, padx=10, fill=tk.X)
            for i in range(5):
                button_frame.columnconfigure(i, weight=1)

            # Broker control buttons
            self.start_btn = ttk.Button(master=button_frame, text=START_BROKER_TEXT, command=self.start_mosquitto)
            self.start_btn.grid(row=0, column=0, padx=5, sticky="ew")

            self.stop_btn = ttk.Button(master=button_frame, text=STOP_BROKER_TEXT, command=self.stop_mosquitto)
            self.stop_btn.grid(row=0, column=1, padx=5, sticky="ew")

            self.status_btn = ttk.Button(master=button_frame, text=CHECK_STATUS_TEXT, command=self.check_status)
            self.status_btn.grid(row=0, column=2, padx=5, sticky="ew")

            # MQTT client controls
            self.connect_btn = ttk.Button(master=button_frame, text=CONNECT_MQTT_TEXT, command=self.connect_mqtt)
            self.connect_btn.grid(row=0, column=3, padx=5, sticky="ew")

            self.topics_btn = ttk.Button(master=button_frame, text=SHOW_TOPICS_TEXT, command=self.show_topics)
            self.topics_btn.grid(row=0, column=4, padx=5, sticky="ew")

            # Publish frame
            self.pub_frame = ttk.LabelFrame(master=self, text=PUBLISH_FRAME_TEXT)
            self.pub_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)

            self.topic_label = ttk.Label(master=self.pub_frame, text=TOPIC_LABEL_TEXT)
            self.topic_label.grid(row=0, column=0, padx=5)
            self.topic_entry = ttk.Entry(master=self.pub_frame, width=20)
            self.topic_entry.grid(row=0, column=1, padx=5)

            self.msg_label = ttk.Label(master=self.pub_frame, text=MESSAGE_LABEL_TEXT)
            self.msg_label.grid(row=0, column=2, padx=5)
            self.msg_entry = ttk.Entry(master=self.pub_frame, width=30)
            self.msg_entry.grid(row=0, column=3, padx=5)

            self.pub_btn = ttk.Button(master=self.pub_frame, text=PUBLISH_BUTTON_TEXT, command=self.publish_message)
            self.pub_btn.grid(row=0, column=4, padx=5)

            # Log display
            self.log_text = scrolledtext.ScrolledText(master=self, wrap=tk.WORD, width=80, height=20, background=self.theme_colors['primary'], foreground=self.theme_colors['fg'])
            self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            console_log("✅ Celebration of success!")
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    # --- Broker and MQTT Methods ---
    def start_mosquitto(self):
        """Starts the Mosquitto broker process if it's not already running."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to start the broker.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            if self.mosquitto_process and self.mosquitto_process.poll() is None:
                console_log(f"⚠️ {BROKER_ALREADY_RUNNING_MSG}")
                return
            
            self.mosquitto_process = subprocess.Popen(["mosquitto"])
            console_log("✅ Broker started successfully!")
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {FAILED_TO_START_BROKER_MSG}{e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def stop_mosquitto(self):
        """Stops the Mosquitto broker process if it's running."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to stop the broker.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            if self.mosquitto_process and self.mosquitto_process.poll() is None:
                self.mosquitto_process.terminate()
                self.mosquitto_process = None
                console_log(f"✅ {BROKER_STOPPED_MSG}")
            else:
                console_log(f"⚠️ {BROKER_NOT_RUNNING_MSG}")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def check_status(self):
        """Checks and reports the status of the Mosquitto broker."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to check broker status.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            if self.mosquitto_process and self.mosquitto_process.poll() is None:
                console_log(f"✅ {BROKER_RUNNING_MSG}")
            else:
                console_log(f"❌ {BROKER_NOT_RUNNING_MSG}")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the MQTT client connects to the broker."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🔵 MQTT client connected with rc={rc}. Subscribing to all topics!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        client.subscribe("#")
        self.log_text.insert(tk.END, f"Connected to broker with rc={rc}\n")

    def on_message(self, client, userdata, msg):
        """Callback for when an MQTT message is received."""
        topic = msg.topic
        payload = msg.payload.decode()
        self.topics_seen.add(topic)
        self.log_text.insert(tk.END, f"[{topic}] {payload}\n")

    def connect_mqtt(self):
        """Connects the MQTT client to the broker in a separate thread."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to connect MQTT client.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.connect(host=BROKER_ADDRESS, port=BROKER_PORT, keepalive=BROKER_TIMEOUT)
            
            thread = threading.Thread(target=self.mqtt_client.loop_forever, daemon=True)
            thread.start()
            console_log("✅ MQTT client connection initiated in a background thread.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def show_topics(self):
        """Displays a list of all topics seen by the MQTT client."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"�🟢 Entering '{current_function_name}' to display topics.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            if self.topics_seen:
                topics_str = "\n".join(sorted(self.topics_seen))
                console_log(f"Observed Topics:\n{topics_str}")
            else:
                console_log("⚠️ No topics observed yet.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def publish_message(self):
        """Publishes a message to a topic via the MQTT client."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to publish a message.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            topic = self.topic_entry.get()
            msg = self.msg_entry.get()
            if self.mqtt_client:
                self.mqtt_client.publish(topic, msg)
                self.log_text.insert(tk.END, f"Published to {topic}: {msg}\n")
                console_log(f"✅ Published message to topic '{topic}'.")
            else:
                console_log(f"❌ {NOT_CONNECTED_MSG}")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
