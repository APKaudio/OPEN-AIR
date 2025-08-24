#gui_frequency.py

#
# A base class for common GUI components, re-written to work with the centralized orchestrator.
# This version corrects the styling of tables and entry widgets for a more cohesive look.
#
# This updated version adds new features for connecting sliders and textboxes
# via MQTT, organized into "Start/Stop" and "Center/Span" groups.
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
# Version 20250823.001500.20

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json
import paho.mqtt.client as mqtt
import threading
import time

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

# Mocking missing modules for a self-contained example
# In a real-world scenario, you would have these files in your project.
def debug_log(message, file, version, function, console_print_func):
    """Mocks the debug_log function for standalone execution."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [DEBUG] {function} ({file}): {message}"
    console_print_func(log_message)

def console_log(message):
    """Mocks the console_log function."""
    print(message)

class MqttControllerUtility:
    """Mocks the MqttControllerUtility for a self-contained example."""
    def __init__(self, print_to_gui_func, log_treeview_func):
        self.print_to_gui = print_to_gui_func
        self.log_treeview = log_treeview_func
        self._subscriptions = {}
        self.is_connected = False
        self.mock_topic_data = {
            "display/base_gui_component.py/frequency/start": 100.0,
            "display/base_gui_component.py/frequency/stop": 200.0,
            "display/base_gui_component.py/frequency/center": 150.0,
            "display/base_gui_component.py/frequency/span": 100.0,
        }

    def connect_mqtt(self):
        """Mock connection that starts a thread to simulate message traffic."""
        console_log("MOCK: Attempting to connect to MQTT...")
        self.is_connected = True
        console_log("MOCK: Connected to MQTT!")
        # Start a thread to simulate receiving messages
        self.message_thread = threading.Thread(target=self._simulate_messages, daemon=True)
        self.message_thread.start()

    def _simulate_messages(self):
        """Simulates receiving mock MQTT messages."""
        while True:
            for topic, value in self.mock_topic_data.items():
                payload = json.dumps({"value": value})
                if topic in self._subscriptions:
                    self._subscriptions[topic](topic, payload)
            time.sleep(2) # Send messages every 2 seconds

    def publish_message(self, topic, subtopic, value):
        """Mocks publishing a message."""
        full_topic = f"{topic}/{subtopic}"
        console_log(f"MOCK: Publishing message to '{full_topic}' with value '{value}'")
        self.mock_topic_data[full_topic] = value
        
        # Immediately call the callback to simulate real-time updates
        payload = json.dumps({"value": value})
        if full_topic in self._subscriptions:
            self._subscriptions[full_topic](full_topic, payload)

    def add_subscriber(self, topic_filter, callback_func):
        """Mocks adding a subscriber."""
        console_log(f"MOCK: Subscribing to topic filter '{topic_filter}'")
        # For simplicity, we'll store the callback directly under the full topic.
        # In a real app, this would handle wildcards more robustly.
        for topic in self.mock_topic_data:
            if topic.startswith(topic_filter.replace("/#", "/")):
                self._subscriptions[topic] = callback_func

class THEMES:
    """Mocks the THEMES dictionary."""
    dark = {
        "bg": "#2e2e2e",
        "fg": "#ffffff",
        "table_bg": "#444444",
        "table_fg": "#ffffff",
        "table_border": "#555555",
        "table_heading_bg": "#666666",
        "entry_bg": "#3c3c3c",
        "entry_fg": "#ffffff",
        "border_width": 1,
        "relief": "flat",
    }
    light = {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "table_bg": "#e0e0e0",
        "table_fg": "#000000",
        "table_border": "#cccccc",
        "table_heading_bg": "#dddddd",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "border_width": 1,
        "relief": "flat",
    }
    
DEFAULT_THEME = "dark"

# --- Global Scope Variables ---
CURRENT_DATE = 20250823
CURRENT_TIME = 1500
CURRENT_TIME_HASH = 1500
REVISION_NUMBER = 20
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
            # --- Function logic goes here ---
            super().__init__(parent, *args, **kwargs)
            self.pack(fill=tk.BOTH, expand=True)

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
                text="Publish Custom",
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

# --- New Classes for your Specific GUI ---
class FrequencyFrame(BaseGUIFrame):
    """
    A specialized GUI frame for frequency controls, inheriting from the base class.
    This frame contains sliders and text boxes for 'Start/Stop' and 'Center/Span'
    which are synchronized via MQTT.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        # Call the parent's constructor to set up the basic GUI and MQTT
        super().__init__(parent, mqtt_util, *args, **kwargs)

        # Remove the default label from the base class and add our own.
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget("text").startswith("Application Frame"):
                widget.destroy()
                break

        frame_label = ttk.Label(self, text="Frequency Controls", font=("Arial", 16))
        frame_label.pack(pady=10)

        # Create a container frame for the controls
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # --- Section 1: Start and Stop Frequency ---
        start_stop_frame = ttk.LabelFrame(controls_frame, text="Start/Stop Frequency")
        start_stop_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # State variables for start/stop
        self.start_value = tk.DoubleVar(value=100.0)
        self.stop_value = tk.DoubleVar(value=200.0)

        # Start Frequency Slider and Entry
        self._create_slider_entry_pair(
            parent=start_stop_frame,
            label_text="Start (MHz):",
            value_var=self.start_value,
            topic="frequency/start",
            min_val=0,
            max_val=1000
        )

        # Stop Frequency Slider and Entry
        self._create_slider_entry_pair(
            parent=start_stop_frame,
            label_text="Stop (MHz):",
            value_var=self.stop_value,
            topic="frequency/stop",
            min_val=0,
            max_val=1000
        )

        # --- Section 2: Center and Span Frequency ---
        center_span_frame = ttk.LabelFrame(controls_frame, text="Center/Span Frequency")
        center_span_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # State variables for center/span
        self.center_value = tk.DoubleVar(value=150.0)
        self.span_value = tk.DoubleVar(value=100.0)

        # Center Frequency Slider and Entry
        self._create_slider_entry_pair(
            parent=center_span_frame,
            label_text="Center (MHz):",
            value_var=self.center_value,
            topic="frequency/center",
            min_val=0,
            max_val=1000
        )

        # Span Frequency Slider and Entry
        self._create_slider_entry_pair(
            parent=center_span_frame,
            label_text="Span (MHz):",
            value_var=self.span_value,
            topic="frequency/span",
            min_val=0,
            max_val=1000
        )

        # The base class already subscribes to a topic. We will handle those messages here.
        # We also need to add our custom subscriptions. The base class already does this for us.

    def _create_slider_entry_pair(self, parent, label_text, value_var, topic, min_val, max_val):
        """Helper method to create a label, slider, and entry pair."""
        pair_frame = ttk.Frame(parent)
        pair_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pair_frame, text=label_text).pack(side=tk.LEFT, padx=(0, 5))

        # Textbox that reflects the slider's value
        entry = ttk.Entry(pair_frame, textvariable=value_var, style="Custom.TEntry")
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        entry.bind("<KeyRelease>", lambda e: self._on_entry_change(value_var, topic, entry.get()))

        # Slider that reflects the textbox's value
        slider = ttk.Scale(pair_frame, from_=min_val, to=max_val, variable=value_var,
                           command=lambda val: self._on_slider_change(value_var, topic))
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 5))
        
    def _on_slider_change(self, value_var, topic):
        """Callback for when a slider is moved. Publishes the value via MQTT."""
        current_function_name = inspect.currentframe().f_code.co_name
        value = value_var.get()
        debug_log(
            message=f"Slider changed for '{topic}'. New value: {value}",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        self.mqtt_util.publish_message(topic=self.current_file, subtopic=topic, value=value)

    def _on_entry_change(self, value_var, topic, entry_text):
        """
        Callback for when a user types in a textbox.
        Updates the slider and publishes the value via MQTT.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            value = float(entry_text)
            value_var.set(value)
            debug_log(
                message=f"Textbox changed for '{topic}'. New value: {value}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            self.mqtt_util.publish_message(topic=self.current_file, subtopic=topic, value=value)
        except ValueError:
            # Handle non-numeric input gracefully
            console_log(f"Invalid input: '{entry_text}' is not a number. Please enter a valid number.")
            debug_log(
                message=f"Invalid input received for '{topic}'. Not a number.",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            pass # The entry widget will keep the old text.

    def _on_mqtt_message(self, topic, payload):
        """
        Overrides the base class's MQTT callback to update the sliders and entries
        in addition to logging the message.
        """
        # Call the parent's method to handle the logging to the table
        super()._on_mqtt_message(topic, payload)

        try:
            message_content = json.loads(payload)["value"]
            if topic.endswith("frequency/start"):
                self.start_value.set(message_content)
            elif topic.endswith("frequency/stop"):
                self.stop_value.set(message_content)
            elif topic.endswith("frequency/center"):
                self.center_value.set(message_content)
            elif topic.endswith("frequency/span"):
                self.span_value.set(message_content)
        except (json.JSONDecodeError, KeyError) as e:
            console_log(f"Error parsing MQTT payload: {e}")
            pass # Ignore messages that don't conform to our expected format

# --- Main application entry point for testing ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("INSTRUMENT") # Main window title
    
    # We now must manually create and pass the MQTT utility instance for the standalone test.
    mqtt_utility = MqttControllerUtility(print_to_gui_func=console_log, log_treeview_func=lambda *args: None)
    mqtt_utility.connect_mqtt()

    # The main frame for the instrument.
    instrument_frame = ttk.Frame(root, style="TFrame")
    instrument_frame.pack(fill=tk.BOTH, expand=True)

    # The Frequency frame as a child of the instrument frame.
    frequency_frame = FrequencyFrame(parent=instrument_frame, mqtt_util=mqtt_utility)
    
    root.mainloop()

