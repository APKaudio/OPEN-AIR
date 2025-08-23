# display/DISPLAY_PARENT.py
#
# This file defines the DISPLAY_PARENT class, a container for the application's
# right-side display tabs, including the console and debug logs.
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
# Version 20250821.222000.1 (Refactored for print statements and safe access)

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

from .display_child_application_console import ConsoleTab
from .display_child_debug import DebugTab
from .display_child_scan_monitor import ScanMonitorTab
from .display_child_scan_view import ScanViewTab

# --- Version Information ---
current_version = "20250821.222000.1"
current_file = os.path.basename(__file__)

class DISPLAY_PARENT(ttk.Frame):
    """
    The main display container widget for the application's right pane.
    Manages the console, debug, and other display-related tabs.
    """
    def __init__(self, parent, app_instance, style_obj):
        super().__init__(parent)
        self.app_instance = app_instance
        self.style_obj = style_obj
        self.parent = parent

        self._create_widgets()

    def _create_widgets(self):
        """Creates the notebook and populates it with display tabs."""
        self.notebook = ttk.Notebook(self, style='Display.TNotebook')
        self.notebook.pack(expand=True, fill='both')

        self.console_tab = ConsoleTab(self.notebook, self.app_instance)
        self.debug_tab = DebugTab(self.notebook, self.app_instance)
        self.scan_monitor_tab = ScanMonitorTab(self.notebook, self.app_instance)
        self.scan_view_tab = ScanViewTab(self.notebook, self.app_instance)

        self.notebook.add(self.console_tab, text='Console')
        self.notebook.add(self.debug_tab, text='Debug')
        self.notebook.add(self.scan_monitor_tab, text='Scan Monitor')
        self.notebook.add(self.scan_view_tab, text='Scan View')

    def get_console_print_function(self):
        """
        Safely retrieves the function used to print text to the console tab.
        """
        if hasattr(self, 'console_tab') and hasattr(self.console_tab, 'console_output_widget'):
            return self.console_tab.console_output_widget.insert_and_scroll
        else:
            print("CRITICAL WARNING: GUI console widget not available for printing.")
            return lambda text: print(text)