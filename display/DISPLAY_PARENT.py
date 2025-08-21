# display/DISPLAY_PARENT.py
#
# This file defines the DISPLAY_PARENT class, which serves as a master container
# for all the display-related tabs in the right pane of the application.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.105600.2
# REFACTORED: Converted to use lazy imports to break circular dependency issues.
# FIXED: Added the `style_obj` parameter to the __init__ method.
# FIXED: Added the `change_display_tab` method to allow other modules to programmatically
#        switch the visible tab.
# FIXED: Resolved the `AttributeError` by removing the premature assignment of `gui_debug`
#        and `gui_console`. This is now handled by the child tab's initialization.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Import logging
from display.console_logic import console_log
from display.debug_logic import debug_log

# --- Version Information ---
w = 20250821
x_str = '105600'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 2
current_version = f"{w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


class DISPLAY_PARENT(ttk.Frame):
    """
    A parent container for all the display-related tabs in the application.
    """
    def __init__(self, parent, app_instance, style_obj):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=current_file, version=current_version, function=current_function)

        super().__init__(parent)
        self.app_instance = app_instance
        self.style_obj = style_obj
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # FIXED: Lazy imports to break circular dependencies
        from display.display_child_application_console import ConsoleTab
        from display.display_child_debug import DebugTab
        from display.display_child_scan_monitor import ScanMonitorTab
        from display.display_child_scan_view import ScanViewTab
        
        self.console_tab = ConsoleTab(self.notebook, self.app_instance)
        self.debug_tab = DebugTab(self.notebook, self.app_instance)
        self.scan_monitor_tab = ScanMonitorTab(self.notebook, self.app_instance)
        self.scan_view_tab = ScanViewTab(self.notebook, self.app_instance)

        self.notebook.add(self.console_tab, text="Console")
        self.notebook.add(self.debug_tab, text="Debug")
        self.notebook.add(self.scan_monitor_tab, text="Scan Monitor")
        self.notebook.add(self.scan_view_tab, text="Scan View")
        
        # REMOVED: Premature assignment of gui_console and gui_debug.
        # These will be set by the child tab's __init__ method after the widgets are created.
        
        debug_log(f"Exiting {current_function}",
                   file=current_file, version=current_version, function=current_function)
    
    def set_parent_notebook(self, notebook):
        # Function Description
        # This function sets the parent notebook for the child tabs.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=current_file, version=current_version, function=current_function)
        
        self.parent_notebook = notebook
        
        debug_log(f"Exiting {current_function}",
                    file=current_file, version=current_version, function=current_function)

    def change_display_tab(self, tab_name):
        # Function Description
        # This function programmatically changes the currently selected tab in the notebook.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🖥️🔵 Entering {current_function} to switch to tab: {tab_name}",
                  file=current_file, version=current_version, function=current_function)
        
        try:
            tab_names = [self.notebook.tab(tab, "text") for tab in self.notebook.tabs()]
            if tab_name in tab_names:
                tab_index = tab_names.index(tab_name)
                self.notebook.select(tab_index)
                debug_log(f"🖥️✅ Successfully changed display tab to: {tab_name}",
                          file=current_file, version=current_version, function=current_function)
                console_log(f"✅ Display tab changed to: {tab_name}", function=current_function)
            else:
                debug_log(f"🖥️❌ Failed to change display tab. Tab '{tab_name}' not found.",
                          file=current_file, version=current_version, function=current_function)
                console_log(f"❌ Error: Cannot change display tab. Tab '{tab_name}' does not exist.", function=current_function)
        except Exception as e:
            console_log(f"❌ Error changing display tab: {e}")
            debug_log(f"🖥️🔴 Arrr, the function be capsized! The error be: {e}",
                      file=current_file, version=current_version, function=current_function)
            
        debug_log(f"🖥️ ✅ Exiting {current_function}",
                  file=current_file, version=current_version, function=current_function)