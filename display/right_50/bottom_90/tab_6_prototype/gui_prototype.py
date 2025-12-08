# display/base_gui_component.py
#
# A base class for common GUI components, re-written to work with the centralized orchestrator.
# This version corrects the styling of tables and entry widgets for a more cohesive look.
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
from workers.active.worker_active_logging import debug_log, console_log
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20251127
CURRENT_TIME = 0
CURRENT_TIME_HASH = 0
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
# Dynamically get the file path relative to the project root
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")


class BaseGUIFrame(ttk.Frame):
    """
    A reusable base class for GUI frames with common button-driven logging and MQTT functionality.
    This class is now designed as a self-contained "island" that manages its own MQTT state.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message="🖥️🟢 Initializing a new GUI frame from the base class. The blueprint is in hand!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            if 'config' in kwargs:
                kwargs.pop('config')
            # --- Function logic goes here ---
            super().__init__(parent, *args, **kwargs)

            # Fix for the bug: Assign global variables as instance attributes
            self.current_file = current_file
            self.current_version = current_version
            self.current_version_hash = current_version_hash

            # We now accept a shared MQTT utility instance from the orchestrator.
            self.mqtt_util = mqtt_util

            # We apply the style at the top of the __init__ to affect all child widgets.
            self._apply_styles(theme_name=DEFAULT_THEME)

            # Create a label for the frame
            frame_label = ttk.Label(self, text=f"Application Frame: {self.__class__.__name__}", font=("Arial", 16))
            frame_label.pack(pady=10)
            
            # --- New MQTT Section ---
            mqtt_frame = ttk.LabelFrame(self, text="MQTT Controls")
            mqtt_frame.pack(fill=tk.X, padx=10, pady=10)

            # Button 3: Publish Version
            self.publish_version_button = ttk.Button(
                mqtt_frame,
                text="Publish Version",
                command=self._publish_version_message
            )
            self.publish_version_button.pack(side=tk.LEFT, padx=5, pady=5)

            # Custom MQTT Publish
            self.custom_topic_entry = ttk.Entry(mqtt_frame, style="Custom.TEntry")
            self.custom_topic_entry.insert(0, f"Custom Message")
            self.custom_topic_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
            
            self.publish_custom_button = ttk.Button(
                mqtt_frame,
                command=self._publish_custom_message
            )
            self.publish_custom_button.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Subscription label
            self.mqtt_topic_var = tk.StringVar(value="Waiting for MQTT message...")
            self.subscription_label = ttk.Label(mqtt_frame, textvariable=self.mqtt_topic_var)
            self.subscription_label.pack(side=tk.LEFT, padx=5, pady=5)

            # We now register our callback with the central utility instead of overwriting the client's callback.
            parent_folder = str(pathlib.Path(self.current_file).parent)
            subscription_topic = f"{parent_folder.replace('\\', '/')}/#"
            self.mqtt_util.add_subscriber(topic_filter=subscription_topic, callback_func=self._on_mqtt_message)


            # --- New MQTT Message Log Table ---
            self.subscriptions_table_frame = ttk.Frame(self)
            self.subscriptions_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            self.subscriptions_table = ttk.Treeview(self.subscriptions_table_frame, columns=("Topic", "Message Content"), show="headings", style="Custom.Treeview")
            self.subscriptions_table.heading("Topic", text="Topic")
            self.subscriptions_table.heading("Message Content", text="Message Content")
            self.subscriptions_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            table_scrollbar = ttk.Scrollbar(self.subscriptions_table_frame, orient=tk.VERTICAL, command=self.subscriptions_table.yview)
            self.subscriptions_table.configure(yscrollcommand=table_scrollbar.set)
            table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # New frame for log buttons, placed at the bottom below the table.
            log_button_frame = ttk.Frame(self)
            log_button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

            # Button 1: Log
            self.log_button = ttk.Button(
                log_button_frame, 
                text="Log", 
                command=self.log_button_press
            )
            self.log_button.pack(side=tk.LEFT, padx=10, pady=10)
            
            # Button 2: Debug
            self.debug_button = ttk.Button(
                log_button_frame, 
                text="Debug", 
                command=self.debug_button_press
            )
            self.debug_button.pack(side=tk.LEFT, padx=10, pady=10)
            
            # --- New Status Bar at the bottom ---
            status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
            
            # Extract folder and file name from the dynamic path
            file_parts = self.current_file.rsplit('/', 1)
            file_folder = file_parts[0] if len(file_parts) > 1 else ""
            file_name = file_parts[-1]

            status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
            status_label = ttk.Label(status_bar, text=status_text, anchor='w')
            status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # General widget styling
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])

        # Table (Treeview) styling
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

        # Entry (textbox) styling
        style.configure('Custom.TEntry',
                        fieldbackground=colors["entry_bg"],
                        foreground=colors["entry_fg"],
                        bordercolor=colors["table_border"])
        
    def log_button_press(self):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Entry log
        debug_log(
            message="🖥️🟢 Entering 'log_button_press' from the GUI layer.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            console_log(f"Left button was clicked in {self.current_file}. Initiating a standard log entry.")
            console_log("✅ Log entry recorded successfully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def debug_button_press(self):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Entry log
        debug_log(
            message="🖥️🟢 Entering 'debug_button_press' from the GUI layer.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            debug_log(
                message="🔍🔵 The right button was clicked! Time for a deeper inspection!",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            console_log(f"✅ Debug entry recorded successfully in {self.current_file}!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_version_message(self):
        # Publishes the file's version to MQTT.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to publish the version.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # The topic is now the file path itself, and the subtopic is "version"
            topic = self.current_file
            message = self.current_version
            self.mqtt_util.publish_message(topic=topic, subtopic="version", value=message)
            console_log("✅ Version message published successfully!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_mqtt_message(self, topic, payload):
        # Callback for when an MQTT message is received.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🔵 Received MQTT message on topic '{topic}'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            message_content = json.loads(payload)["value"]
            self.subscriptions_table.insert('', 'end', values=(topic, message_content))
            self.subscriptions_table.yview_moveto(1) # Scroll to the bottom
            self.mqtt_topic_var.set(f"Last Message: {topic} -> {message_content}")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_custom_message(self):
        # Publishes a custom message from the wildcard text box.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to publish a custom message.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # The topic is the file path, and the subtopic is "textbox"
            topic = self.current_file
            subtopic = "textbox"
            message = self.custom_topic_entry.get()
            self.mqtt_util.publish_message(topic=topic, subtopic=subtopic, value=message)
            console_log(f"✅ Custom message published successfully to '{topic}/{subtopic}'!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Base Component Test")
    
    # We now must manually create and pass the MQTT utility instance for the standalone test.
    mqtt_utility = MqttControllerUtility(print_to_gui_func=console_log, log_treeview_func=lambda *args: None)
    mqtt_utility.connect_mqtt()

    app_frame = BaseGUIFrame(parent=root, mqtt_util=mqtt_utility)
    
    root.mainloop()