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
#
#
# Version 20250801.1030.1 (Updated header and imports for new folder structure)

current_version = "20250801.1030.1" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs - CORRECTED PATHS
from tabs.Markers.tab_markers_child_display import MarkersDisplayTab
from tabs.Markers.tab_markers_child_import_and_edit import ReportConverterTab
from utils.utils_instrument_control import debug_print


class TAB_MARKERS_PARENT(ttk.Frame):
    """
    A Tkinter Frame that serves as the parent tab for all Marker-related functionalities.
    It contains a nested Notebook to organize child tabs like Markers Display and Report Converter.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the TAB_MARKERS_PARENT.

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
            4. Instantiates MarkersDisplayTab and ReportConverterTab.
            5. Adds these child tabs to the nested notebook.
            6. Binds the '<<NotebookTabChanged>>' event to _on_tab_change for the child notebook.

        Outputs of this function:
            None. Initializes the parent tab frame and its nested components.

        (2025-07-31) Change: Initial creation of TAB_MARKERS_PARENT.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        # Configure grid to make the notebook expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the nested notebook for child tabs
        # The style is set in main_app._setup_styles to match the parent tab color
        self.child_notebook = ttk.Notebook(self, style='MarkersChild.TNotebook')
        self.child_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Instantiate and add child tabs
        self.markers_display_tab = MarkersDisplayTab(
            self.child_notebook,
            app_instance=self.app_instance,
            console_print_func=self.console_print_func
        )
        self.child_notebook.add(self.markers_display_tab, text="Markers Display")

        self.report_converter_tab = ReportConverterTab(
            self.child_notebook,
            app_instance=self.app_instance,
            console_print_func=self.console_print_func
        )
        self.child_notebook.add(self.report_converter_tab, text="Report Converter")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        debug_print(f"🚫🐛 [DEBUG] Initialized TAB_MARKERS_PARENT. Version: {current_version}",
                    file=f"tabs/TAB_MARKERS_PARENT.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name,
                    console_print_func=self.console_print_func)


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
        """
        selected_tab_id = self.child_notebook.select()
        selected_tab_widget = self.child_notebook.nametowidget(selected_tab_id)

        if hasattr(selected_tab_widget, '_on_tab_selected'):
            selected_tab_widget._on_tab_selected(event)
            debug_print(f"🚫🐛 [DEBUG] Child tab changed to {selected_tab_widget.winfo_class()}. Calling _on_tab_selected. Version: {current_version}",
                        file=f"tabs/TAB_MARKERS_PARENT.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name,
                        console_print_func=self.console_print_func)
        else:
            debug_print(f"🚫🐛 [DEBUG] Child tab changed to {selected_tab_widget.winfo_class()}. No _on_tab_selected method found. Version: {current_version}",
                        file=f"tabs/TAB_MARKERS_PARENT.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name,
                        console_print_func=self.console_print_func)

    def _on_tab_selected(self, event):
        """
        Function Description:
        Callback for when this TAB_MARKERS_PARENT tab is selected in the main parent notebook.
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
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/TAB_MARKERS_PARENT.py - {current_version}"
        debug_print(f"�🐛 [DEBUG] TAB_MARKERS_PARENT selected. Version: {current_version}",
                    file=current_file,
                    function=current_function,
                    console_print_func=self.console_print_func)

        # Ensure the currently visible child tab also gets its _on_tab_selected called
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
                debug_print(f"🚫🐛 [DEBUG] Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_class()}. Version: {current_version}",
                            file=current_file,
                            function=current_function,
                            console_print_func=self.console_print_func)
            else:
                debug_print(f"🚫🐛 [DEBUG] Active child tab {selected_child_tab_widget.winfo_class()} has no _on_tab_selected method. Version: {current_version}",
                            file=current_file,
                            function=current_function,
                            console_print_func=self.console_print_func)

