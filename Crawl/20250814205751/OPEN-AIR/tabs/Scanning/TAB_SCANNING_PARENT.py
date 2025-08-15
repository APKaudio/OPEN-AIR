# tabs/Scanning/TAB_SCANNING_PARENT.py
#
# This file defines the parent tab for Scanning-related functionalities.
# It acts as a container for child tabs such as "Scan Configuration",
# "Scan Bands", and "Scan Meta Data".
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
# Version 20250810.160100.3 (UPDATED: Added the new 'Scan Bands' tab and reordered the tabs.)

current_version = "20250810.160100.3"
current_version_hash = 20250810 * 160100 * 3 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Import the child tabs
from tabs.Scanning.tab_scanning_child_scan_configuration import ScanTab
from tabs.Scanning.tab_scanning_child_scan_meta_data import ScanMetaDataTab
from tabs.Scanning.tab_scanning_child_bands import BandsTab # NEW: Import the new BandsTab

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

class TAB_SCANNING_PARENT(ttk.Frame):
    """
    A parent tab for Scanning-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        # This function description tells me what this function does
        # Initializes the parent tab for scanning. It sets up the notebook
        # and creates instances of the child tabs: Scan Configuration, BandsTab,
        # and Scan Meta Data.
        #
        # Inputs to this function
        #   parent (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance.
        #   console_print_func (function): A function for printing to the console.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing TAB_SCANNING_PARENT.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Scanning.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.scan_config_tab = ScanTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.scan_config_tab, text="Scan Configuration")

        # NEW: Add the new BandsTab here
        self.scan_bands_tab = BandsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.scan_bands_tab, text="Bands")

        self.scan_meta_data_tab = ScanMetaDataTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.scan_meta_data_tab, text="Scan Meta Data")

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)
        
        debug_log(f"TAB_SCANNING_PARENT initialized. Tabs are set up and ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_child_tab_selected(self, event):
        # This function description tells me what this function does
        # Handles tab change events within this parent's child notebook by
        # delegating the event to the currently active child tab.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Outputs of this function
        #   None. Triggers a method call on a child tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Child tab selected in Scanning Parent. Checking for tab handler.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)


    def _on_parent_tab_selected(self, event):
        # This function description tells me what this function does
        # Handles the event when this parent tab is selected by delegating
        # the event to the currently active child tab.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object from the parent notebook.
        #
        # Outputs of this function
        #   None.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scanning Parent tab selected. Initializing child tab handlers.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        self._on_child_tab_selected(event)