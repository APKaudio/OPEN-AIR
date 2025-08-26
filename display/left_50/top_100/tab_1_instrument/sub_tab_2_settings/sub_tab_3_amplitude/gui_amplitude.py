MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/instrument/Settings/Amplitude_Settings"
# display/gui_frequency.py
#
# A GUI component for displaying hierarchical MQTT data using dynamic labels and text boxes.
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
# Version 20250825.200730.3

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import json

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250825
CURRENT_TIME = 200730
REVISION_NUMBER = 3
current_version = "20250825.200730.3"
current_version_hash = 20250825 * 200730 * 3
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# --- No Magic Numbers (as per your instructions) ---

TOPIC_DELIMITER = "/"


class gui_file_paths(ttk.Frame):
    """
    A GUI component for displaying MQTT data in a dynamic, hierarchical layout.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the GUI, sets up the layout, and subscribes to the MQTT topic.
        
        Args:
            parent (tk.Widget): The parent widget for this frame.
            mqtt_util (MqttControllerUtility): The MQTT utility instance for communication.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🖥️🟢 Initializing the {self.__class__.__name__}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            super().__init__(parent, *args, **kwargs)
            self.pack(fill=tk.BOTH, expand=True)

            self.current_file = current_file
            self.current_version = current_version
            self.current_version_hash = current_version_hash
            self.mqtt_util = mqtt_util
            self.current_class_name = self.__class__.__name__
            self.topic_widgets = {}  # Dictionary to store widget references

            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])

            # --- Main Content Frame (everything above the status bar) ---
            content_frame = ttk.Frame(self)
            content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # A canvas to hold the dynamic content and allow scrolling
            self.canvas = tk.Canvas(content_frame, borderwidth=0, highlightthickness=0, background=colors["bg"])
            self.scroll_frame = ttk.Frame(self.canvas)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            
            scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            
            self.scroll_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")
                )
            )

            # This frame will hold the dynamic content
            self.main_frame = ttk.LabelFrame(self.scroll_frame, text="MQTT Data")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # --- Status Bar at the bottom ---
            status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

            file_parts = self.current_file.rsplit('/', 1)
            file_folder = file_parts[0] if len(file_parts) > 1 else ""
            file_name = file_parts[-1]

            status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
            status_label = ttk.Label(status_bar, text=status_text, anchor='w')
            status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.mqtt_util.add_subscriber(topic_filter=f"{MQTT_TOPIC_FILTER}/#", callback_func=self._on_commands_message)

            console_log("✅ Meta Data GUI initialized successfully!")

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

        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"], padding=colors["padding"] * 5, relief=colors["relief"], borderwidth=colors["border_width"] * 2)
        style.map('TButton', background=[('active', colors["secondary"])])
        
        # New styling for the entry widgets based on the new dictionary
        textbox_style = colors["textbox_style"]
        style.configure('Custom.TEntry',
                        font=(textbox_style["Textbox_Font"], textbox_style["Textbox_Font_size"]),
                        foreground=textbox_style["Textbox_Font_colour"],
                        background=textbox_style["Textbox_BG_colour"],
                        fieldbackground=textbox_style["Textbox_BG_colour"],
                        bordercolor=textbox_style["Textbox_border_colour"])


    def _on_entry_changed(self, event, topic, entry_widget):
        """
        Event handler for when a textbox's value changes and loses focus.
        It publishes the new value back to the corresponding MQTT topic.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        new_value = entry_widget.get()
        
        # Split the topic into the main topic and the subtopic
        topic_parts = topic.split(TOPIC_DELIMITER)
        main_topic = TOPIC_DELIMITER.join(topic_parts[:-1])
        subtopic = topic_parts[-1]
        
        debug_log(
            message=f"🖥️🔵 Textbox changed for topic '{topic}'. Publishing new value: '{new_value}'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # Pass the raw string value to the utility, letting it handle the JSON formatting.
            self.mqtt_util.publish_message(topic=main_topic, subtopic=subtopic, value=new_value)
            console_log(f"✅ Published updated value '{new_value}' to '{topic}'!")
        except Exception as e:
            console_log(f"❌ Error publishing message to {topic}: {e}")
            debug_log(
                message=f"❌🔴 Failed to publish new value! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_commands_message(self, topic, payload):
        """
        Processes an incoming MQTT message and dynamically updates the GUI layout.
        The function removes the topic filter, splits the remaining topic path, and
        either creates new nested LabelFrames and widgets or updates an existing Entry box.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🔵 Received MQTT message on topic '{topic}'. Processing message...",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # Safely parse the payload
            try:
                parsed_payload = json.loads(payload)
                value_to_display = parsed_payload.get("value", payload)
                # Strip the extra quotes if they exist
                if isinstance(value_to_display, str) and value_to_display.startswith('"') and value_to_display.endswith('"'):
                    value_to_display = value_to_display[1:-1]
            except json.JSONDecodeError:
                value_to_display = payload

            # Check if the widget for this topic already exists
            if topic in self.topic_widgets:
                entry_widget = self.topic_widgets[topic]
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, value_to_display)
                console_log(f"✅ Updated existing widget for '{topic}' with payload: '{value_to_display}'.")
                return

            # If it's a new topic, build the hierarchy
            topic_prefix = MQTT_TOPIC_FILTER
            topic_path = topic.replace(topic_prefix, "").strip(TOPIC_DELIMITER)
            nodes = topic_path.split(TOPIC_DELIMITER)
            
            current_frame = self.main_frame
            for i, node in enumerate(nodes):
                
                # Ignore the "Active" node as per your request
                if node == "Active":
                    continue
                
                is_last_node = (i == len(nodes) - 1)
                
                if not is_last_node:
                    # This is a parent node, find or create the LabelFrame
                    frame_name = f"frame_{node}"
                    if not hasattr(current_frame, frame_name):
                        new_frame = ttk.LabelFrame(current_frame, text=node.replace('_', ' ').title())
                        setattr(current_frame, frame_name, new_frame)
                        new_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
                        current_frame = new_frame
                    else:
                        current_frame = getattr(current_frame, frame_name)
                else:
                    # This is the end node, create a label and entry box
                    sub_frame = ttk.Frame(current_frame)
                    sub_frame.pack(fill=tk.X, expand=True, padx=5, pady=2)
                    
                    label_text = node.replace('_', ' ').title()
                    label = ttk.Label(sub_frame, text=label_text)
                    label.pack(side=tk.LEFT, padx=(5, 5))
                    
                    # Entry widget now uses the new custom style
                    entry = ttk.Entry(sub_frame, width=80, style="Custom.TEntry")
                    entry.insert(0, value_to_display)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
                    
                    # Bind the FocusOut event to the new entry
                    entry.bind("<FocusOut>", lambda e, t=topic, ew=entry: self._on_entry_changed(e, t, ew))
                    
                    # Store the entry widget for future updates
                    self.topic_widgets[topic] = entry
                    
                    console_log(f"✅ Added new widget for '{topic}' with payload: '{value_to_display}'.")

            # The scroll_frame needs to be updated after a new widget is added
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 The GUI construction has failed! A plague upon this error: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )