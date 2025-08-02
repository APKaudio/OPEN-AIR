# tabs/Instrument/TAB_INSTRUMENT_PARENT.py
#
# This file defines the TAB_INSTRUMENT_PARENT class, which serves as a container
# for all instrument-related child tabs within the main application's two-layer
# tab structure. It manages the child notebook and the instantiation of
# individual instrument configuration and control tabs.
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
# Version 20250802.0075.11 (Added style_obj argument to __init__ and passed it to child tabs.)

current_version = "20250802.0075.11" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 75 * 11 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect

# Import child tabs for the Instrument parent tab
from tabs.Instrument.tab_instrument_child_connection import InstrumentTab
from tabs.Instrument.tab_instrument_child_visa_interpreter import VisaInterpreterTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

class TAB_INSTRUMENT_PARENT(ttk.Frame):
    """
    A parent tab for Instrument-related functionalities, containing child tabs
    for connection settings, general settings, and device presets.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, style_obj=None): # Added style_obj
        # Initializes the TAB_INSTRUMENT_PARENT frame and its child notebook.
        # It sets up the UI for instrument control and configuration,
        # including connection management and device settings.
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
        #   3. Creates `self.child_notebook` to hold the instrument-specific sub-tabs.
        #   4. Instantiates `InstrumentConnectionTab`, `VisaInterpreterTab`.
        #   5. Adds these child tabs to `self.child_notebook`.
        #   6. Binds the `<<NotebookTabChanged>>` event for the child notebook to `_on_tab_selected`.
        #   7. Assigns child tab instances as attributes of `self`
        #      so they can be accessed from `main_app.py` (e.g., for `update_connection_status_logic`).
        #
        # Outputs:
        #   None. Initializes the Instrument parent tab UI.
        #
        # (2025-07-31) Change: Initial creation, refactored from main_app.py.
        #                      Implemented child notebook and added connection and settings tabs.
        # (2025-07-31) Change: Added InstrumentDevicePresetsTab.
        # (2025-07-31) Change: Updated header.
        # (2025-08-01) Change: Fixed AttributeError by exposing child tabs as attributes (self.instrument_connection_tab, self.instrument_settings_tab).
        #                     Updated debug prints to new format.
        # (2025-08-01) Change: Corrected import for InstrumentSettingsTab to use existing InstrumentTab.
        # (2025-08-01) Change: Removed import and instantiation of non-existent InstrumentDevicePresetsTab.
        # (2025-08-01) Change: Instantiated VisaInterpreterTab and assigned it as an attribute.
        # (2025-08-01) Change: Updated debug_print calls to use debug_log.
        # (2025-08-02) Change: Added style_obj argument to __init__ and passed it to child tabs.
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing Instrument Parent Tab.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Create a notebook for child tabs within the Instrument parent tab
        # The style is dynamically set by main_app's _on_parent_tab_change
        self.child_notebook = ttk.Notebook(self, style='InstrumentChild.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

         # Assuming InstrumentTab also contains the settings display/logic
        self.instrument_settings_tab = InstrumentTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj) # Pass style_obj
        self.child_notebook.add(self.instrument_settings_tab, text="Settings")

        # FUCKING IMPORTANT: Instantiate VisaInterpreterTab and assign it as an attribute
        self.visa_interpreter_tab = VisaInterpreterTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj) # Pass style_obj
        self.child_notebook.add(self.visa_interpreter_tab, text="VISA Interpreter")

        # Removed instantiation of InstrumentDevicePresetsTab as the module does not exist.
        # If this tab is intended, the file 'tab_instrument_child_device_presets.py'
        # needs to be created with the 'InstrumentDevicePresetsTab' class defined within it.
        # self.instrument_device_presets_tab = InstrumentDevicePresetsTab(self.child_notebook, self.app_instance, self.console_print_func)
        # self.child_notebook.add(self.instrument_device_presets_tab, text="Device Presets")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"Instrument Parent Tab initialized with child tabs. Version: {current_version}. Let's get this show on the road!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        # Handles tab change events within the child notebook of the Instrument tab.
        # It propagates the selection event to the newly selected child tab's
        # `_on_tab_selected` method, if it exists.
        #
        # Inputs:
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Determines the currently selected child tab.
        #   3. Retrieves the widget instance of the selected child tab.
        #   4. If the selected child tab widget has an `_on_tab_selected` method, calls it.
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
        Handles tab change events within the child notebook of the Instrument tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument Child Tab changed. Version: {current_version}. Time to update the display!",
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
            debug_log(f"Active child tab {selected_child_tab_widget.winfo_name()} has no _on_tab_selected method. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

