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
# Version 20250801.2335.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2335.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2335 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs - CORRECTED PATHS
from tabs.Scanning.tab_scanning_child_scan_configuration import ScanTab
from tabs.Scanning.tab_scanning_child_scan_meta_data import ScanMetaDataTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log


class TAB_SCANNING_PARENT(ttk.Frame):
    """
    A Tkinter Frame that serves as the parent tab for all Scanning-related functionalities.
    It contains a nested Notebook to organize child tabs like Scan Configuration and Scan Meta Data.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the TAB_SCANNING_PARENT.

        Inputs:
            master (tk.Widget): The parent widget (the ttk.Notebook).
            app_instance (App): The main application instance, used for accessing
                                shared state like Tkinter variables and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.

        Process of this function:
            1. Calls the superclass constructor.
            2. Stores app_instance and console_print_func.
            3. Creates a ttk.Notebook to hold child tabs.
            4. Instantiates ScanTab and ScanMetaDataTab.
            5. Adds these child tabs to the nested notebook.
            6. Binds the '<<NotebookTabChanged>>' event to _on_tab_change for the child notebook.

        Outputs of this function:
            None. Initializes the parent tab frame and its nested components.

        (2025-07-31) Change: Initial creation of TAB_SCANNING_PARENT.
        (2025-08-01) Change: Updated child_notebook style to 'ScanningChild.TNotebook'.
        (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing TAB_SCANNING_PARENT. Version: {current_version}. Getting ready to scan!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Configure grid to make the notebook expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the nested notebook for child tabs
        # The style is set in main_app._setup_styles to match the parent tab color
        self.child_notebook = ttk.Notebook(self, style='ScanningChild.TNotebook') # Updated style
        self.child_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Instantiate and add child tabs
        self.scan_configuration_tab = ScanTab(
            self.child_notebook,
            app_instance=self.app_instance,
            console_print_func=self.console_print_func
        )
        self.child_notebook.add(self.scan_configuration_tab, text="Scan Configuration")

        self.scan_meta_data_tab = ScanMetaDataTab(
            self.child_notebook,
            app_instance=self.app_instance,
            console_print_func=self.console_print_func
        )
        self.child_notebook.add(self.scan_meta_data_tab, text="Scan Meta Data")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        debug_log(f"TAB_SCANNING_PARENT initialized with child tabs. Version: {current_version}. Scan setup complete!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _on_tab_change(self, event):
        """
        Function Description:
        Handles tab change events within this parent's child Notebook.
        It calls the `_on_tab_selected` method on the newly selected child tab's
        widget if that method exists, allowing individual child tabs to refresh
        their content or state when they become active.

        Inputs to this function:
            event (tkinter.Event): The event object that triggered the tab change.

        Process of this function:
            1. Determines the currently selected tab within the child notebook.
            2. Retrieves the widget instance of the selected tab.
            3. Checks if the selected tab widget has an `_on_tab_selected` method.
            4. If the method exists, calls it.
            5. If the method does not exist, logs that it was not found.

        Outputs of this function:
            None. Triggers UI updates in the selected child tab.

        (2025-07-31) Change: Added to handle child tab changes.
        (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Child tab changed to {self.child_notebook.tab(self.child_notebook.select(), 'text')}. Version: {current_version}. Time to update!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        selected_tab_id = self.child_notebook.select()
        selected_tab_widget = self.child_notebook.nametowidget(selected_tab_id)

        if hasattr(selected_tab_widget, '_on_tab_selected'):
            selected_tab_widget._on_tab_selected(event)
            debug_log(f"Propagated _on_tab_selected to active child tab: {selected_tab_widget.winfo_class()}. Version: {current_version}. Looking good!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Active child tab {selected_tab_widget.winfo_class()} has no _on_tab_selected method. What the hell?! Version: {current_version}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _on_tab_selected(self, event):
        """
        Function Description:
        Callback for when this TAB_SCANNING_PARENT tab is selected in the main parent notebook.
        This ensures that when the parent tab is clicked, the currently visible child tab
        within this parent also gets its `_on_tab_selected` method called, allowing it to refresh.

        Inputs to this function:
            event (tkinter.Event): The event object that triggered the tab selection.

        Process of this function:
            1. Prints a debug message.
            2. Determines the currently selected child tab within its nested notebook.
            3. Calls the `_on_tab_selected` method on that child tab if it exists.

        Outputs of this function:
            None. Ensures child tab content is refreshed when the parent tab is activated.

        (2025-07-31) Change: Added to handle parent tab selection and propagate to active child.
        (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"TAB_SCANNING_PARENT selected. Version: {current_version}. Let's get these scan settings refreshed!",
                    file=__file__,
                    version=current_version,
                    function=current_function,
                    special=True) # Adding special flag as per your style

        # Ensure the currently visible child tab also gets its _on_tab_selected called
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
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
