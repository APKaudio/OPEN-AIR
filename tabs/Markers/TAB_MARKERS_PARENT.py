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
# Version 20250803.0134.1 (Added _on_parent_tab_selected to display ASCII art for Markers tab.)
# Version 20250803.0140.1 (Fixed TypeError: 'function' object is not iterable in MarkersDisplayTab by explicitly passing None for headers and rows.)
# Version 20250803.0143.1 (Modified _on_parent_tab_selected to always select the first child tab.)

# FUCKING DIAGNOSTIC PRINT: If you don't see this, the problem is before this file is fully loaded.
print(" Executing tabs/Markers/TAB_MARKERS_PARENT.py module...")

current_version = "20250803.0143.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 143 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs
from tabs.Markers.tab_markers_child_display import MarkersDisplayTab
from tabs.Markers.tab_markers_child_import_and_edit import ReportConverterTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
from src.gui_elements import _print_marks_ascii # Import the ASCII art function

class TAB_MARKERS_PARENT(ttk.Frame):
    """
    A parent tab for Marker-related functionalities, containing child tabs
    for marker display and report conversion.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, style_obj=None):
        # Initializes the TAB_MARKERS_PARENT frame and its child notebook.
        # It sets up the UI for marker management and reporting.
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
        #   3. Creates `self.child_notebook` to hold the marker-specific sub-tabs.
        #   4. Instantiates `MarkerDisplayTab` and `ReportConverterTab`.
        #   5. Adds these child tabs to `self.child_notebook`.
        #   6. Binds the `<<NotebookTabChanged>>` event for the child notebook to `_on_tab_selected`.
        #
        # Outputs:
        #   None. Initializes the Markers parent tab UI.
        #
        # (2025-07-31) Change: Initial creation, refactored from main_app.py.
        #                      Implemented child notebook and added marker display and report converter tabs.
        # (2025-07-31) Change: Updated header.
        # (2025-08-01) Change: Updated debug prints to new format.
        # (2025-08-01) Change: Updated debug_print calls to use debug_log and console_log.
        # (2025-08-02) Change: Fixed TclError by not passing console_print_func to child tabs.
        # (2025-08-03) Change: Added _on_parent_tab_selected to display ASCII art for Markers tab.
        # (2025-08-03) Change: Fixed TypeError: 'function' object is not iterable in MarkersDisplayTab by explicitly passing None for headers and rows.
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing Markers Parent Tab.",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Create a notebook for child tabs within the Markers parent tab
        self.child_notebook = ttk.Notebook(self, style='MarkersChild.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate child tabs and add them to the notebook
        # FIX: Explicitly pass headers=None and rows=None to MarkersDisplayTab
        self.marker_display_tab = MarkersDisplayTab(self.child_notebook, headers=None, rows=None, app_instance=self.app_instance, style_obj=self.style_obj)
        self.child_notebook.add(self.marker_display_tab, text="Markers Display")

        self.report_converter_tab = ReportConverterTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.report_converter_tab, text="Report Converter")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"Markers Parent Tab initialized with child tabs. Version: {current_version}. Ready for some marking!",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        # Handles tab change events within the child notebook of the Markers tab.
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
        # (2025-08-02) Change: Fixed TclError by not passing console_print_func to child tabs.
        """
        Handles tab change events within the child notebook of the Markers tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Markers Child Tab changed. Version: {current_version}. Time to update the display!",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Get the currently selected tab widget
        selected_child_tab_id = self.child_notebook.select()
        selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)

        # If the selected child tab has an _on_tab_selected method, call it
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
            debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_class()}. Version: {current_version}. Looking good!",
                        file=f"{__file__} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?! Version: {current_version}.",
                        file=f"{__file__} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _on_parent_tab_selected(self, event):
        # Function Description: Handles the event when the Markers parent tab is selected in the main notebook.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the tab selection.
        #
        # Process of this function:
        #   1. Logs a debug message indicating the Markers parent tab has been selected.
        #   2. Calls the `_print_marks_ascii` function to display the Markers-specific ASCII art in the console.
        #   3. Explicitly selects the first child tab in the `child_notebook`.
        #   4. Calls the `_on_tab_selected` method of the newly selected first child tab to refresh its state.
        #
        # Outputs of this function:
        #   None. Displays ASCII art and ensures the first child tab is active and refreshed.
        #
        # (2025-08-03) Change: Initial creation to display ASCII art when the parent tab is selected.
        # (2025-08-03) Change: Modified to always select the first child tab when the parent tab is selected.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Markers Parent Tab selected. Version: {current_version}. Time to mark some points! 📍",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function,
                    special=True)
        

        # Get the list of all child tab IDs
        child_tab_ids = self.child_notebook.tabs()
        if child_tab_ids:
            # Select the first child tab
            self.child_notebook.select(child_tab_ids[0])
            first_child_tab_widget = self.child_notebook.nametowidget(child_tab_ids[0])

            # Ensure the newly selected first child tab also gets its _on_tab_selected called
            if hasattr(first_child_tab_widget, '_on_tab_selected'):
                first_child_tab_widget._on_tab_selected(event)
                debug_log(f"Propagated _on_tab_selected to first child tab: {first_child_tab_widget.winfo_class()}. Version: {current_version}. Looking good!",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log(f"First child tab {first_child_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?!",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            debug_log(f"No child tabs found in Markers Parent Tab. Nothing to select. Fucking useless!",
                        file=f"{__file__} - {current_version}",
                        version=current_version,
                        function=current_function)
