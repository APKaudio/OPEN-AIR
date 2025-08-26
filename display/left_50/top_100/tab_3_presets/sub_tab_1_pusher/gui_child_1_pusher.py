# display/GUI_pusher.py
#
# A GUI component for displaying dynamically configured widgets.
# This version is a simple, self-configuring GUI that assumes a worker is providing
# clean, pre-processed JSON payloads.
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
# Version 20250826.002845.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import json

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250826
CURRENT_TIME = 2845
REVISION_NUMBER = 1
current_version = "20250826.002845.1"
current_version_hash = 20250826 * 2845 * 1
current_file = "display/GUI_pusher.py"

# --- No Magic Numbers (as per your instructions) ---
MQTT_TOPIC_FILTER = "OPEN-AIR/gui/presets"
TOPIC_DELIMITER = "/"


class GUI_pusher(ttk.Frame):
    """
    A GUI component that dynamically builds an interface from pre-processed MQTT payloads.
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
            self.topic_widgets = {}
            
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

            console_log("✅ GUI_pusher initialized successfully!")

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
        
        textbox_style = colors["textbox_style"]
        style.configure('Custom.TEntry',
                        font=(textbox_style["Textbox_Font"], textbox_style["Textbox_Font_size"]),
                        foreground=textbox_style["Textbox_Font_colour"],
                        background=textbox_style["Textbox_BG_colour"],
                        fieldbackground=textbox_style["Textbox_BG_colour"],
                        bordercolor=textbox_style["Textbox_border_colour"])
        
        style.configure('TCombobox',
                        fieldbackground=textbox_style["Textbox_BG_colour"],
                        background=colors["bg"],
                        foreground=textbox_style["Textbox_Font_colour"])
        style.map('TCombobox',
                  fieldbackground=[('readonly', textbox_style["Textbox_BG_colour"])],
                  selectbackground=[('readonly', textbox_style["Textbox_BG_colour"])],
                  selectforeground=[('readonly', textbox_style["Textbox_Font_colour"])])

    def _on_commands_message(self, topic, payload):
        """
        Processes an incoming MQTT message and dynamically updates the GUI.
        It expects a pre-processed payload containing all the metadata for a single widget.
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
            config = json.loads(payload)
            control_type = config.get("control_type")
            label_text = config.get("label", topic.split(TOPIC_DELIMITER)[-1]).replace('_', ' ').title()
            
            if topic in self.topic_widgets:
                widget = self.topic_widgets[topic]
                if control_type in ["_Value", "_Label", "_sliderValue", "_option"]:
                    widget.set(config.get("value"))
                elif control_type == "_toggle":
                    widget.set(config.get("value"))
                elif control_type == "_indicator":
                    widget.config(text="🟢" if config.get("value") == "active" else "🔴")
                console_log(f"✅ Updated existing widget for '{topic}'.")
                return

            self._create_widget(topic, config)
            console_log(f"✅ Created new widget for '{topic}'.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 The GUI construction has failed! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _create_widget(self, topic, config):
        """
        Creates a new widget based on the provided configuration.
        """
        control_type = config.get("control_type")
        label_text = config.get("label", topic.split(TOPIC_DELIMITER)[-1]).replace('_', ' ').title()
        value = config.get("value")
        
        parent_frame_text = topic.split(TOPIC_DELIMITER)[-2].replace('_', ' ').title()
        
        parent_frame = self._find_or_create_frame(self.main_frame, parent_frame_text)
        
        sub_frame = ttk.Frame(parent_frame)
        sub_frame.pack(fill=tk.X, expand=True, padx=5, pady=2)
        
        label = ttk.Label(sub_frame, text=label_text)
        label.pack(side=tk.LEFT, padx=(5, 5))
        
        widget = None
        if control_type == "_Value":
            widget = self._create_value_widget(sub_frame, topic, value)
        elif control_type == "_option":
            widget = self._create_option_widget(sub_frame, topic, value, config.get("options", []))
        
        if widget:
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            self.topic_widgets[topic] = widget
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _find_or_create_frame(self, parent, text):
        """Finds an existing frame by text or creates a new one."""
        frame_name = f"frame_{text.replace(' ', '_').lower()}"
        if not hasattr(parent, frame_name):
            new_frame = ttk.LabelFrame(parent, text=text)
            setattr(parent, frame_name, new_frame)
            new_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
            return new_frame
        return getattr(parent, frame_name)

    def _create_value_widget(self, parent, topic, value):
        """Creates a textbox widget."""
        entry = ttk.Entry(parent, width=80, style="Custom.TEntry")
        entry.insert(0, value)
        entry.bind("<FocusOut>", lambda e, t=topic, ew=entry: self._on_entry_changed(e, t, ew))
        return entry

    def _create_option_widget(self, parent, topic, value, options):
        """Creates a dropdown widget."""
        combobox = ttk.Combobox(parent, values=options, state='readonly')
        combobox.set(value)
        combobox.bind("<<ComboboxSelected>>", lambda e, t=topic, ew=combobox: self._on_commands_message(t, f'{{"value": "{ew.get()}"}}'))
        return combobox

