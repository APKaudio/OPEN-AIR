# tabs/Markers/TAB_MARKERS_PARENT.py
#
# This file defines the parent tab for Marker-related functionalities.
# It acts as a container for child tabs such as "Markers Display" and "Report Converter".
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
# Version 20250802.0055.1 (Fixed TclError by not passing console_print_func to child tabs.)

# FUCKING DIAGNOSTIC PRINT: If you don't see this, the problem is before this file is fully loaded.
print(" Executing tabs/Markers/TAB_MARKERS_PARENT.py module...")

current_version = "20250802.0055.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 55 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs - CORRECTED PATHS
from tabs.Markers.tab_markers_child_display import MarkersDisplayTab
from tabs.Markers.tab_markers_child_import_and_edit import ReportConverterTab
# Updated imports for new logging functions
from src.debug_logic import debug_log # Changed from debug_print
from src.console_logic import console_log # Changed from console_print_func


class TAB_MARKERS_PARENT(ttk.Frame):
    """
    This class defines the parent tab for all Marker-related functionalities.
    It contains a child notebook to organize different marker sub-tabs.
    """
    def __init__(self, master, app_instance, console_print_func, **kwargs):
        """
        Initializes the TAB_MARKERS_PARENT frame.

        Inputs:
            master (tk.Widget): The parent widget (usually the main application's notebook).
            app_instance (App): The main application instance, used for accessing
                                 shared state and methods across tabs.
            console_print_func (function): The function to use for printing messages
                                           to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing TAB_MARKERS_PARENT. Version: {current_version}. Let's get this tab working!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func # Store for use within this parent tab

        # Configure grid for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a Notebook for child tabs
        self.child_notebook = ttk.Notebook(self, style='Child.TNotebook')
        self.child_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Instantiate child tabs and add them to the child notebook
        # IMPORTANT: Do NOT pass console_print_func to child tabs as a direct keyword argument
        # if their __init__ does not explicitly accept it and pass it to super().__init__.
        # Instead, they should import console_log directly.
        self.markers_display_tab = MarkersDisplayTab(
            self.child_notebook,
            app_instance=self.app_instance,
            headers=[], # Initial empty headers
            rows=[]     # Initial empty rows
        )
        self.child_notebook.add(self.markers_display_tab, text="Markers Display")

        self.report_converter_tab = ReportConverterTab(
            self.child_notebook,
            app_instance=self.app_instance
        )
        self.child_notebook.add(self.report_converter_tab, text="Report Converter")

        # Bind tab change event for child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_change)

        # Apply initial styling to child notebook tabs
        self._on_child_tab_change(None) # Call once to set initial colors


    def _on_child_tab_change(self, event):
        """
        Handles tab change events within the child notebook of the Markers tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Markers Child Tab changed. Version: {current_version}. Time to update the display!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Get the currently selected tab widget
        selected_child_tab_id = self.child_notebook.select()
        selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)

        # If the selected child tab has an _on_tab_selected method, call it
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
            debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_class()}. Version: {current_version}. Looking good!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?! Version: {current_version}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

