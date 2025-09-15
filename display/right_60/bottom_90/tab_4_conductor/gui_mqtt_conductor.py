# display/right_40/bottom_90/tab_4_conductor/gui_mqtt_conductor.py
#
# A comprehensive GUI component for managing and testing an MQTT broker and client.
# This file now integrates with the MqttControllerUtility to handle all broker and client logic.
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
# Version 20250914.223648.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import json
import paho.mqtt.client as mqtt
from collections import defaultdict
from itertools import filterfalse

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"display/right_40/bottom_90/tab_4_conductor/{os.path.basename(__file__)}"

# --- Constant Variables (No Magic Numbers) ---
SERVER_STATUS_FRAME_TEXT = "Server Status"
PUBLISH_FRAME_TEXT = "Publish Message"
SUBSCRIPTIONS_FRAME_TEXT = "Live Subscriptions"
CLIENTS_FRAME_TEXT = "Connected Clients"
TOPIC_LABEL_TEXT = "Topic:"
SUBTOPIC_LABEL_TEXT = "Subtopic:"
VALUE_LABEL_TEXT = "Value:"
PUBLISH_BUTTON_TEXT = "Publish"
CLEAR_BUTTON_TEXT = "Clear Log"
COLUMNS = ("Topic", "Message")
SERVER_STATUS_TEXT = "Status:"
SERVER_ADDRESS_TEXT = "Broker Address:"
SERVER_VERSION_TEXT = "Version:"
SERVER_UPTIME_TEXT = "Uptime:"
SERVER_MESSAGE_COUNT_TEXT = "Messages:"
CLIENT_COUNT_TEXT = "Clients:"
FILTER_LABEL_TEXT = "Filter Topics:"
STATUS_RUNNING_TEXT = "Running"
STATUS_STOPPED_TEXT = "Stopped"


class MqttConductorFrame(ttk.Frame):
    """
    A comprehensive GUI frame for controlling and monitoring a local MQTT broker.
    It provides a centralized view of broker status, topic activity, and connected clients.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the GUI, setting up layout and widgets.
        This version integrates with the main application's MqttControllerUtility.

        Args:
            parent: The parent widget for this frame.
            mqtt_util: A shared instance of MqttControllerUtility.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🐐🟢 Initializing the '{self.__class__.__name__}' GUI frame. This one's a masterpiece of form over function!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            super().__init__(parent, *args, **kwargs)
            self.mqtt_util = mqtt_util
            
            self._apply_styles(theme_name=DEFAULT_THEME)
            
            self.topics_in_table = defaultdict(lambda: None)
            self.clients_in_table = set()

            # FIX: Create widgets first before subscribing to prevent AttributeError.
            self._create_widgets()
            
            # Now subscribe to messages after the widgets exist.
            self.mqtt_util.log_to_table = self.log_to_table
            self.mqtt_util.print_to_gui_func = self.log_to_gui
            self.mqtt_util.add_subscriber(topic_filter="#", callback_func=self._on_message)
            self.mqtt_util.add_subscriber(topic_filter="$SYS/#", callback_func=self._on_sys_message)
            
            self.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            

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
        """Applies the specified theme to the GUI elements."""
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('Custom.Treeview',
                         background=colors["table_bg"],
                         foreground=colors["table_fg"],
                         fieldbackground=colors["table_bg"],
                         bordercolor=colors["table_border"],
                         borderwidth=colors["border_width"])
        style.configure('Custom.Treeview.Heading',
                         background=colors["table_heading_bg"],
                         foreground=colors["fg"],
                         relief=colors["relief"],
                         borderwidth=colors["border_width"])
        style.configure('Custom.TEntry',
                         fieldbackground=colors["entry_bg"],
                         foreground=colors["entry_fg"],
                         bordercolor=colors["table_border"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"], padding=5)

    def _create_widgets(self):
        """Creates all the UI widgets for the comprehensive conductor tab."""
        top_frame = ttk.Frame(master=self)
        top_frame.pack(side=tk.TOP, pady=10, padx=10, fill=tk.X, expand=False)
        center_frame = ttk.Frame(master=self)
        center_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        bottom_frame = ttk.Frame(master=self)
        bottom_frame.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X, expand=False)

        server_status_frame = ttk.LabelFrame(master=top_frame, text=SERVER_STATUS_FRAME_TEXT)
        server_status_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, expand=True)
        self.server_status_label = ttk.Label(master=server_status_frame, text=f"{SERVER_STATUS_TEXT} {STATUS_STOPPED_TEXT}")
        self.server_address_label = ttk.Label(master=server_status_frame, text=f"{SERVER_ADDRESS_TEXT} localhost")
        self.server_version_label = ttk.Label(master=server_status_frame, text=f"{SERVER_VERSION_TEXT} N/A")
        self.server_uptime_label = ttk.Label(master=server_status_frame, text=f"{SERVER_UPTIME_TEXT} N/A")
        self.server_message_count_label = ttk.Label(master=server_status_frame, text=f"{SERVER_MESSAGE_COUNT_TEXT} N/A")
        self.server_client_count_label = ttk.Label(master=server_status_frame, text=f"{CLIENT_COUNT_TEXT} N/A")
        self.server_status_label.pack(anchor=tk.W, padx=5, pady=2)
        self.server_address_label.pack(anchor=tk.W, padx=5, pady=2)
        self.server_version_label.pack(anchor=tk.W, padx=5, pady=2)
        self.server_uptime_label.pack(anchor=tk.W, padx=5, pady=2)
        self.server_message_count_label.pack(anchor=tk.W, padx=5, pady=2)
        self.server_client_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        server_controls_frame = ttk.Frame(master=top_frame)
        server_controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        # --- Bind buttons to the actual utility functions ---
        self.start_btn = ttk.Button(master=server_controls_frame, text="Start Broker", command=lambda: console_log("Mock: Start Broker"))
        self.stop_btn = ttk.Button(master=server_controls_frame, text="Stop Broker", command=lambda: console_log("Mock: Stop Broker"))
        self.check_status_btn = ttk.Button(master=server_controls_frame, text="Check Status", command=self._check_status_request)
        self.start_btn.pack(pady=2, padx=5, fill=tk.X)
        self.stop_btn.pack(pady=2, padx=5, fill=tk.X)
        self.check_status_btn.pack(pady=2, padx=5, fill=tk.X)

        publish_frame = ttk.LabelFrame(master=top_frame, text=PUBLISH_FRAME_TEXT)
        publish_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, expand=True)
        tk.Label(master=publish_frame, text=TOPIC_LABEL_TEXT).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.topic_entry = ttk.Entry(master=publish_frame, style="Custom.TEntry")
        self.topic_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.topic_entry.insert(0, f"conductor/test_message")

        tk.Label(master=publish_frame, text=VALUE_LABEL_TEXT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.value_entry = ttk.Entry(master=publish_frame, style="Custom.TEntry")
        self.value_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.value_entry.insert(0, "Test Payload")

        # --- Bind the publish button to the new _publish_custom_message method ---
        publish_btn = ttk.Button(master=publish_frame, text=PUBLISH_BUTTON_TEXT, command=self._publish_custom_message)
        publish_btn.grid(row=0, column=3, rowspan=2, padx=5, sticky="ew")

        subscriptions_frame = ttk.LabelFrame(master=center_frame, text=SUBSCRIPTIONS_FRAME_TEXT)
        subscriptions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.subscriptions_table = ttk.Treeview(master=subscriptions_frame, columns=COLUMNS, show="headings", style="Custom.Treeview")
        self.subscriptions_table.heading("Topic", text="Topic")
        self.subscriptions_table.heading("Message", text="Message Content")
        self.subscriptions_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar = ttk.Scrollbar(master=subscriptions_frame, orient=tk.VERTICAL, command=self.subscriptions_table.yview)
        self.subscriptions_table.configure(yscrollcommand=table_scrollbar.set)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        bottom_btn_frame = ttk.Frame(master=bottom_frame)
        bottom_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.log_btn = ttk.Button(master=bottom_btn_frame, text="Log", command=lambda: console_log("A sample log message from the Conductor."))
        self.debug_btn = ttk.Button(master=bottom_btn_frame, text="Debug", command=lambda: debug_log(message="A sample debug message.", file=current_file, version=current_version, function="_create_widgets", console_print_func=console_log))
        self.clear_btn = ttk.Button(master=bottom_btn_frame, text=CLEAR_BUTTON_TEXT, command=self._clear_log)
        self.log_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.debug_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def log_to_gui(self, message):
        """Allows the utility to log messages to the console."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🔵 Entering '{current_function_name}' to print a message to the GUI console.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        try:
            # The console_log function already exists globally.
            console_log(message)
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
            
    def log_to_table(self, topic: str, message: str):
        """Allows the utility to log messages to the table."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
    #    debug_log(
    #        message=f"🐐🔵 Entering '{current_function_name}' to add a message to the table.",
    #        file=current_file,
    #        version=current_version,
    #        function=current_function_name,
    #        console_print_func=console_log
    #    )
        try:
            self.subscriptions_table.insert('', 'end', values=(topic, message))
            self.subscriptions_table.yview_moveto(1) # Scroll to the bottom
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )

    def _publish_custom_message(self):
        """Publishes the message from the GUI's text boxes."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        #debug_log(
        #    message=f"🐐🟢 Entering '{current_function_name}' to publish a custom message.",
        #    file=current_file,
        #    version=current_version,
        #    function=current_function_name,
        #    console_print_func=console_log
        #)
        try:
            topic = self.topic_entry.get()
            value = self.value_entry.get()
            if not topic or not value:
                console_log("❌ Please enter a topic and a value.")
                return

            self.mqtt_util.publish_message(topic=topic, subtopic="", value=value)
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )

    def _clear_log(self):
        """Clears the contents of the subscriptions table."""
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Entering '{current_function_name}' to clear the log.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        try:
            self.subscriptions_table.delete(*self.subscriptions_table.get_children())

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )

    def _on_message(self, topic, payload):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
    #    debug_log(
    #        message=f"🐐🔵 Entering '{current_function_name}' to process a general MQTT message.",
    #        file=current_file,
    #        version=current_version,
    #        function=current_function_name,
    #        console_print_func=console_log
    #    )
        try:
            self.log_to_table(topic=topic, message=payload)

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )

    def _on_sys_message(self, topic, payload):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
       # debug_log(
       #     message=f"🔵 Entering '{current_function_name}' to process a system status message.",
       #     file=current_file,
       #     version=current_version,
       #     function=current_function_name,
       #     console_print_func=console_log
       # )
        try:
            if "$SYS/broker/version" in topic:
                self.server_version_label.config(text=f"{SERVER_VERSION_TEXT} {payload}")
            elif "$SYS/broker/uptime" in topic:
                self.server_uptime_label.config(text=f"{SERVER_UPTIME_TEXT} {payload}")
            elif "$SYS/broker/messages/sent" in topic:
                self.server_message_count_label.config(text=f"{SERVER_MESSAGE_COUNT_TEXT} {payload}")
            elif "$SYS/broker/clients/connected" in topic:
                self.server_client_count_label.config(text=f"{CLIENT_COUNT_TEXT} {payload}")
            
            self.server_status_label.config(text=f"{SERVER_STATUS_TEXT} {STATUS_RUNNING_TEXT}")
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )

    def _check_status_request(self):
        """
        Manually triggers a request for system information from the broker.
        """
        self.mqtt_util.publish_message(topic="$SYS/broker/version", subtopic="", value="", retain=False)
        self.mqtt_util.publish_message(topic="$SYS/broker/uptime", subtopic="", value="", retain=False)
        self.mqtt_util.publish_message(topic="$SYS/broker/messages/sent", subtopic="", value="", retain=False)
        self.mqtt_util.publish_message(topic="$SYS/broker/clients/connected", subtopic="", value="", retain=False)