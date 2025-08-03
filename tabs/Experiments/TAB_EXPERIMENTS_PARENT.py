# tabs/Experiments/TAB_EXPERIMENTS_PARENT.py
#
# This file defines the parent tab for Experiment-related functionalities.
# It acts as a container for child tabs such as "Intermod" and "JSON API".
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
# Version 20250801.2200.1 (Refactored debug_print to use debug_log and console_log.)
# Version 20250803.0136.1 (Added _on_parent_tab_selected to display ASCII art for Experiments tab.)

current_version = "20250803.0136.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 136 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs - CORRECTED PATHS
from tabs.Experiments.tab_experiments_child_intermod import InterModTab
from tabs.Experiments.tab_experiments_child_JSON_api import JsonApiTab
from tabs.Experiments.tab_experiments_colouring import  ColouringTab # Importing the ColouringTab, if needed

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
from src.gui_elements import _print_xxx_ascii # Import the ASCII art function

class TAB_EXPERIMENTS_PARENT(ttk.Frame):
    """
    A parent tab for Experiment-related functionalities, containing child tabs
    for intermodulation analysis and JSON API interaction.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, style_obj=None):
        # Initializes the TAB_EXPERIMENTS_PARENT frame and its child notebook.
        # It sets up the UI for various experimental features.
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
        #   3. Creates `self.child_notebook` to hold the experiment-specific sub-tabs.
        #   4. Instantiates `InterModTab` and `JsonApiTab`.
        #   5. Adds these child tabs to `self.child_notebook`.
        #   6. Binds the `<<NotebookTabChanged>>` event for the child notebook to `_on_tab_selected`.
        #
        # Outputs:
        #   None. Initializes the Experiments parent tab UI.
        #
        # (2025-07-31) Change: Initial creation, refactored from main_app.py.
        #                      Implemented child notebook and added intermod and JSON API tabs.
        # (2025-07-31) Change: Updated header.
        # (2025-08-01) Change: Updated debug prints to new format.
        # (2025-08-01) Change: Updated debug_print calls to use debug_log and console_log.
        # (2025-08-03) Change: Added _on_parent_tab_selected to display ASCII art for Experiments tab.
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing Experiments Parent Tab.",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Create a notebook for child tabs within the Experiments parent tab
        self.child_notebook = ttk.Notebook(self, style='ExperimentsChild.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate child tabs and add them to the notebook
        self.intermod_tab = InterModTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.intermod_tab, text="Intermod")

        self.json_api_tab = JsonApiTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.json_api_tab, text="JSON API")

        self.json_api_tab = ColouringTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.json_api_tab, text="Colours")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"Experiments Parent Tab initialized with child tabs. Version: {current_version}. Let's get experimental!",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        # Handles tab change events within the child notebook of the Experiments tab.
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
        # (2025-08-01) Change: Updated debug_print calls to use debug_log.
        """
        Handles tab change events within the child notebook of the Experiments tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log(f"TAB_EXPERIMENTS_PARENT selected.",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function,
                    special=True) # Adding special flag as per your style

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
                debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?!",
                            file=f"{__file__} - {current_version}",
                            version=current_version,
                            function=current_function)

    def _on_parent_tab_selected(self, event):
        # Function Description: Handles the event when the Experiments parent tab is selected in the main notebook.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the tab selection.
        #
        # Process of this function:
        #   1. Logs a debug message indicating the Experiments parent tab has been selected.
        #   2. Calls the `_print_xxx_ascii` function to display the Experiments-specific ASCII art in the console.
        #   3. Ensures that if there's an active child tab, its `_on_tab_selected` method is also called to refresh its state.
        #
        # Outputs of this function:
        #   None. Displays ASCII art and potentially refreshes the active child tab.
        #
        # (2025-08-03) Change: Initial creation to display ASCII art when the parent tab is selected.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Experiments Parent Tab selected. Version: {current_version}. Time for some wild experiments! 🧪",
                    file=f"{__file__} - {current_version}",
                    version=current_version,
                    function=current_function,
                    special=True)


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
