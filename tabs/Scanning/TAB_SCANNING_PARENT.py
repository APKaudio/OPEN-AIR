# tabs/Scanning/TAB_SCANNING_PARENT.py
#
# This file defines the parent tab for Scanning-related functionalities.
# It acts as a container for child tabs such as "Scan Configuration" and "Scan Meta Data".
# This structure allows for better organization of the GUI and logical grouping of features.
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
# Version 20250801.2335.3 (Fixed TclError: unknown option "-style_obj" by removing it from kwargs for child tabs.)
# Version 20250803.0132.1 (Added _on_parent_tab_selected to display ASCII art for Scanning tab.)

current_version = "20250803.0132.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 132 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs - CORRECTED PATHS
from tabs.Scanning.tab_scanning_child_scan_configuration import ScanTab
from tabs.Scanning.tab_scanning_child_scan_meta_data import ScanMetaDataTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
from src.gui_elements import _print_scan_ascii # Import the ASCII art function

class TAB_SCANNING_PARENT(ttk.Frame):
    """
    A parent tab for Scanning-related functionalities, containing child tabs
    for scan configuration and scan metadata.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, style_obj=None):
        # Initializes the TAB_SCANNING_PARENT frame and its child notebook.
        # It sets up the UI for scan configuration and metadata management.
        #
        # Inputs:
        #   parent_notebook (ttk.Notebook): The top-level notebook widget this tab belongs to.
        #   app_instance (App): The main application instance, providing access to shared data and methods.
        #   console_print_func (function): Function to print messages to the GUI console.
        #   style_obj (ttk.Style, optional): The ttk.Style object from the main app.
        #
        # Process:
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores references to `app_instance`, `console_print_func`, and `style_obj`.
        #   3. Creates `self.child_notebook` to hold the scan-specific sub-tabs.
        #   4. Instantiates `ScanTab` and `ScanMetaDataTab`.
        #   5. Adds these child tabs to `self.child_notebook`.
        #   6. Binds the `<<NotebookTabChanged>>` event for the child notebook to `_on_tab_selected`.
        #
        # Outputs:
        #   None. Initializes the Scanning parent tab UI.
        #
        # (2025-07-31) Change: Initial creation, refactored from main_app.py.
        #                      Implemented child notebook and added scan configuration and metadata tabs.
        # (2025-07-31) Change: Updated header.
        # (2025-08-01) Change: Updated debug prints to new format.
        # (2025-08-01) Change: Updated debug_print calls to use debug_log and console_log.
        # (2025-08-01) Change: Fixed TclError: unknown option "-style_obj" by removing it from kwargs for child tabs.
        # (2025-08-03) Change: Added _on_parent_tab_selected to display ASCII art for Scanning tab.
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing Scanning Parent Tab.",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Create a notebook for child tabs within the Scanning parent tab
        self.child_notebook = ttk.Notebook(self, style='ScanningChild.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate child tabs and add them to the notebook
        self.scan_config_tab = ScanTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.scan_config_tab, text="Scan Configuration")

        self.scan_meta_data_tab = ScanMetaDataTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.scan_meta_data_tab, text="Scan Meta Data")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"Scanning Parent Tab initialized with child tabs. Version: {current_version}. Ready to scan!",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        # Handles tab change events within the child notebook of the Scanning tab.
        # It propagates the selection event to the active child tab.
        #
        # Inputs:
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Determines the currently selected child tab.
        #   3. Retrieves the widget instance of the selected child tab.
        #   4. If the selected child tab has an `_on_tab_selected` method, calls it.
        #      This allows individual child tabs to refresh their content or state
        #      when they become active.
        #
        # Outputs:
        #   None. Triggers content refreshes in child tabs.
        #
        # (2025-07-31) Change: Initial creation.
        # (2025-07-31) Change: Updated header.
        # (2025-08-01) Change: Updated debug prints to new format.
        # (2025-08-01) Change: Updated debug_print calls to use debug_log and console_log.
        """
        Handles tab change events within the child notebook of the Scanning tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"TAB_SCANNING_PARENT selected. Version: {current_version}. Let's get these scan settings refreshed!",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function,
                    special=True)

        # Ensure the currently visible child tab also gets its _on_tab_selected called
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
                debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_class()}. Version: {current_version}.",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?! Version: {current_version}.",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)

    def _on_parent_tab_selected(self, event):
        # Function Description: Handles the event when the Scanning parent tab is selected in the main notebook.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the tab selection.
        #
        # Process of this function:
        #   1. Logs a debug message indicating the Scanning parent tab has been selected.
        #   2. Calls the `_print_scan_ascii` function to display the Scanning-specific ASCII art in the console.
        #   3. Ensures that if there's an active child tab, its `_on_tab_selected` method is also called to refresh its state.
        #
        # Outputs of this function:
        #   None. Displays ASCII art and potentially refreshes the active child tab.
        #
        # (2025-08-03) Change: Initial creation to display ASCII art when the parent tab is selected.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scanning Parent Tab selected. Version: {current_version}. Time to get those scans rolling! 📈",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function,
                    special=True)
        _print_scan_ascii(self.console_print_func)

        # Also ensure the currently visible child tab gets its _on_tab_selected called
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
                debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_class()}. Version: {current_version}.",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?!",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)
