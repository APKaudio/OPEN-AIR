# tabs/Presets/TAB_PRESETS_PARENT.py
#
# This file defines the TAB_PRESETS_PARENT class, which serves as a container
# for all preset-related child tabs within the main application's two-layer
# tab structure. It manages the child notebook and the instantiation of
# individual preset management tabs.
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
# Version 20250802.1700.0 (Initial creation of correct TAB_PRESETS_PARENT class.)

current_version = "20250802.1700.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1700 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import child tabs for the Presets parent tab
# Assuming there will be a tab_presets_child_presets.py for the actual presets UI
from tabs.Presets.tab_presets_child_preset import PresetFilesTab # Placeholder for now

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

class TAB_PRESETS_PARENT(ttk.Frame):
    """
    A parent tab for Presets-related functionalities, containing child tabs
    for managing device presets (load, save, delete).
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, style_obj=None):
        # Initializes the TAB_PRESETS_PARENT frame and its child notebook.
        # It sets up the UI for preset management.
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
        #   3. Creates `self.child_notebook` to hold the preset-specific sub-tabs.
        #   4. Instantiates `PresetsTab`.
        #   5. Adds this child tab to `self.child_notebook`.
        #   6. Binds the `<<NotebookTabChanged>>` event for the child notebook to `_on_tab_selected`.
        #   7. Assigns child tab instances as attributes of `self`
        #      so they can be accessed from `main_app.py`.
        #
        # Outputs:
        #   None. Initializes the Presets parent tab UI.
        #
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing Presets Parent Tab.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Create a notebook for child tabs within the Presets parent tab
        self.child_notebook = ttk.Notebook(self, style='PresetsChild.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate PresetsTab and assign it as an attribute
        self.presets_tab = PresetFilesTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.presets_tab, text="Presets Management")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"Presets Parent Tab initialized with child tabs. Version: {current_version}. Ready to manage some presets!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        """
        Handles tab change events within the child notebook of the Presets tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Presets Child Tab changed. Version: {current_version}. Time to update the display!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Get the currently selected tab widget
        selected_child_tab_id = self.child_notebook.select()
        selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)

        # If the selected child tab has an _on_tab_selected method, call it
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
            debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_name()}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Active child tab {selected_child_tab_widget.winfo_name()} has no _on_tab_selected method. Skipping update.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

