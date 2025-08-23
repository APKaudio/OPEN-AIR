# display/base_gui_component_rebuilt.py
#
# A reusable base class for GUI frames, now fully integrated with the centralized
# logging and MQTT orchestrator utilities and the new styling module.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.160000.1

import os
import inspect
import pathlib
import tkinter as tk
from tkinter import ttk
import json

# --- Module Imports ---
from configuration.logging import debug_log, console_log
from utils.mqtt_controller_util import MqttControllerUtility
from styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
# Dynamically get the file path relative to the project root for topic naming and logging
current_file_path = pathlib.Path(__file__).resolve()
# Assuming project root is two levels up from this file's location
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# Versioning
CURRENT_DATE = 20250824
CURRENT_TIME = 160000
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME * REVISION_NUMBER)


class BaseGUIFrame(ttk.Frame):
    """
    A reusable base class for GUI frames with common functionality for MQTT,
    logging, and styling.
    """
    def __init__(self, parent, mqtt_util, console_print_func, **kwargs):
        super().__init__(parent, **kwargs)

        self.current_file = current_file
        self.current_version = current_version
        self.mqtt_util = mqtt_util
        self.console_print_func = console_print_func
        self.current_topic_prefix = self._get_topic_prefix()

        # Apply styles immediately to affect all child widgets
        self._apply_styles(DEFAULT_THEME)

    def _get_topic_prefix(self):
        """
        A utility function to determine the MQTT topic root from the file path.
        e.g., 'tabs/Scanning/tab_scanning_child_bands.py' -> 'tabs/Scanning/tab_scanning_child_bands'
        """
        relative_path = pathlib.Path(self.current_file)
        topic = str(relative_path).replace(os.sep, '/')
        return os.path.splitext(topic)[0]

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Configure styles using the imported color palette
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["secondary"], foreground=colors["fg"])
        style.configure('TEntry', fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"])
        style.configure('TCombobox', fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"])
        style.configure('TCheckbutton', background=colors["bg"], foreground=colors["fg"])
        style.configure('TNotebook', background=colors["bg"])
        style.configure('TNotebook.Tab', background=colors["secondary"], foreground=colors["fg"])
        style.map('TNotebook.Tab', background=[('selected', colors["primary"])])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe.Label', background=colors["bg"], foreground=colors["fg"])
        style.configure('Treeview', background=colors["table_bg"], foreground=colors["table_fg"], fieldbackground=colors["table_bg"])
        style.configure('Treeview.Heading', background=colors["table_heading_bg"], foreground=colors["fg"])
        style.configure('ScrolledText', background=colors["entry_bg"], foreground=colors["entry_fg"], borderwidth=1)
        style.configure('Horizontal.TScale', background=colors["bg"], troughcolor=colors["secondary"])

    def _publish_value(self, element_name, value):
        """
        Publishes a value to a topic based on the file path and element name.
        """
        self.mqtt_util.publish_message(
            topic=self.current_topic_prefix,
            subtopic=element_name,
            value=value
        )