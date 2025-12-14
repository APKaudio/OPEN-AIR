# display/right_50/bottom_90/tab_3_debug/gui_tab_3_debug.py
#
# A DEBUG tab component inheriting from the formal BaseGUIFrame.
# It provides logging controls and an MQTT table view for inspection.
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
# Version 20251127.000000.1
# MODIFIED: Inherits from the centralized BaseGUIFrame and uses clean attribute referencing.

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME
# FIXED: Import the formalized BaseGUIFrame
from display.right_50.bottom_90.prototype.base_gui_component_rebuilt import BaseGUIFrame


# --- Global Scope Variables (Protocol 4.4) ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parents[4] 
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")


class DebugTabGUIFrame(BaseGUIFrame):
    """
    A debug frame with logging and MQTT monitoring functionality.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, mqtt_util, *args, **kwargs)

        debug_log(
            message="🖥️🟢 Initializing the dedicated Debug Tab GUI. Time for deep inspection!",
            file=current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        # Overwrite inherited MQTT topic variable for local use
        self.mqtt_topic_var = tk.StringVar(value="Waiting for MQTT message...")
        
        self._create_widgets()
        
        # Now subscribe to messages after the widgets exist.
        parent_folder = str(pathlib.Path(self.current_file).parent)
        subscription_topic = f"{parent_folder.replace('\\', '/')}/#"
        self.mqtt_util.add_subscriber(topic_filter=subscription_topic, callback_func=self._on_mqtt_message)
        self.mqtt_util.add_subscriber(topic_filter="Open-Air/Recon/#", callback_func=self._on_mqtt_message)


        console_log("✅ Debug Tab GUI initialized successfully!")

    def _create_widgets(self):
        """Creates all the UI widgets for the comprehensive conductor tab."""
        
        # --- Log Buttons Frame ---
        log_button_frame = ttk.Frame(self)
        log_button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Button 1: Log
        ttk.Button(log_button_frame, text="Log", command=self.log_button_press).pack(side=tk.LEFT, padx=5)
        
        # Button 2: Debug
        ttk.Button(log_button_frame, text="Debug", command=self.debug_button_press).pack(side=tk.LEFT, padx=5)

        # Button 3: Publish Version
        ttk.Button(log_button_frame, text="Publish Version", command=self._publish_version_message).pack(side=tk.LEFT, padx=5)

        # Custom MQTT Publish Entry
        self.custom_topic_entry = ttk.Entry(log_button_frame, style="Custom.TEntry")
        self.custom_topic_entry.insert(0, f"Custom Message")
        self.custom_topic_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        ttk.Button(log_button_frame, text="Publish Custom", command=self._publish_custom_message).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(log_button_frame, textvariable=self.mqtt_topic_var).pack(side=tk.LEFT, padx=5)

        # --- MQTT Message Log Table ---
        self.subscriptions_table_frame = ttk.Frame(self)
        self.subscriptions_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.subscriptions_table = ttk.Treeview(self.subscriptions_table_frame, columns=("Topic", "Message Content"), show="headings", style="Custom.Treeview")
        self.subscriptions_table.heading("Topic", text="Topic")
        self.subscriptions_table.heading("Message Content", text="Message Content")
        self.subscriptions_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_scrollbar = ttk.Scrollbar(self.subscriptions_table_frame, orient=tk.VERTICAL, command=self.subscriptions_table.yview)
        self.subscriptions_table.configure(yscrollcommand=table_scrollbar.set)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Status Bar at the bottom ---
        status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        
        file_parts = self.current_file.rsplit('/', 1)
        file_folder = file_parts[0] if len(file_parts) > 1 else ""
        file_name = file_parts[-1]

        status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
        ttk.Label(status_bar, text=status_text, anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)

    def log_button_press(self):
        # Sends a standard log message.
        current_function_name = inspect.currentframe().f_code.co_name
        console_log(f"Log button pressed in {self.current_file}. Initiating standard log entry.")
        debug_log(
            message=f"🖥️🟢 Executing 'log_button_press' from the GUI layer.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

    def debug_button_press(self):
        # Sends a debug log message.
        current_function_name = inspect.currentframe().f_code.co_name
        console_log(f"Debug button pressed in {self.current_file}.")
        debug_log(
            message=f"🔍🔵 The debug button was clicked! Time for a deeper inspection!",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

    def _publish_version_message(self):
        # Publishes the file's version to MQTT.
        current_function_name = inspect.currentframe().f_code.co_name
        topic = self.current_file
        message = self.current_version
        self.mqtt_util.publish_message(topic=topic, subtopic="version", value=message)
        console_log("✅ Version message published successfully!")
        debug_log(
            message=f"🖥️🟢 Published version '{message}' to topic '{topic}/version'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )


    def _on_mqtt_message(self, topic, payload):
        # Callback for when an MQTT message is received.
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            # Safely parse the value from the payload dictionary
            message_content = json.loads(payload).get("value", payload)
            
            self.subscriptions_table.insert('', 'end', values=(topic, message_content))
            self.subscriptions_table.yview_moveto(1) # Scroll to the bottom
            self.mqtt_topic_var.set(f"Last Message: {topic} -> {message_content}")
            
        except Exception as e:
            debug_log(
                message=f"❌🔴 Error processing MQTT message in Debug Tab: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_custom_message(self):
        # Publishes a custom message from the wildcard text box.
        current_function_name = inspect.currentframe().f_code.co_name
        topic = self.current_file
        subtopic = "textbox"
        message = self.custom_topic_entry.get()
        self.mqtt_util.publish_message(topic=topic, subtopic=subtopic, value=message)
        console_log(f"✅ Custom message published successfully to '{topic}/{subtopic}'!")
        debug_log(
            message=f"🖥️🟢 Published custom message: '{message}'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )