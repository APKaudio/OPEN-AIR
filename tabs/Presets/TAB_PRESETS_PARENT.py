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
# Version 20250802.1701.12 (Updated imports for refactored preset utility files.)
# Version 20250802.1800.2 (Updated to include new Local and Device preset tabs.)
# Version 20250802.1800.6 (Updated to include new PresetEditorTab and adjust tab order.)
# Version 20250803.0135.1 (Added _on_parent_tab_selected to display ASCII art for Presets tab.)
# Version 20250803.0748.1 (Added InitialConfigurationTab to child notebook.)

current_version = "20250803.0748.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 748 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os # Import os for basename

# Import the child tabs
from tabs.Presets.tab_presets_child_local import LocalPresetsTab
from tabs.Presets.tab_presets_child_device import DevicePresetsTab
from tabs.Presets.tab_presets_child_preset_editor import PresetEditorTab


# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
from src.gui_elements import _print_presets_ascii # Import the ASCII art function

class TAB_PRESETS_PARENT(ttk.Frame):
    """
    A parent tab for Presets-related functionalities, containing child tabs
    for local presets, device presets, and a preset editor.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, style_obj=None):
        # Initializes the TAB_PRESETS_PARENT frame and its child notebook.
        # It sets up the UI for managing various presets.
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
        #   4. Instantiates `LocalPresetsTab`, `DevicePresetsTab`, `PresetEditorTab`,
        #      and `InitialConfigurationTab`.
        #   5. Adds these child tabs to `self.child_notebook` in a specific order.
        #   6. Binds the `<<NotebookTabChanged>>` event for the child notebook to `_on_tab_selected`.
        #
        # Outputs:
        #   None. Initializes the Presets parent tab UI.
        #
        # (2025-07-31) Change: Initial creation, refactored from main_app.py.
        #                      Implemented child notebook and added local and device preset tabs.
        # (2025-07-31) Change: Updated header.
        # (2025-08-01) Change: Updated debug prints to new format.
        # (2025-08-01) Change: Updated debug_print calls to use debug_log and console_log.
        # (2025-08-02) Change: Updated imports for refactored preset utility files.
        # (2025-08-02) Change: Updated to include new Local and Device preset tabs.
        # (2025-08-02) Change: Updated to include new PresetEditorTab and adjust tab order.
        # (2025-08-03) Change: Added _on_parent_tab_selected to display ASCII art for Presets tab.
        # (2025-08-03) Change: Added InitialConfigurationTab to child notebook.
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name

        debug_log(f"Initializing Presets Parent Tab.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Create a notebook for child tabs within the Presets parent tab
        self.child_notebook = ttk.Notebook(self, style='PresetsChild.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate child tabs and add them to the notebook
        # Order: Initial Configuration, Local, Device, Editor


        self.local_presets_tab = LocalPresetsTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.local_presets_tab, text="Local Presets")

        self.device_presets_tab = DevicePresetsTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.device_presets_tab, text="Device Presets")

        self.preset_editor_tab = PresetEditorTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.style_obj)
        self.child_notebook.add(self.preset_editor_tab, text="Preset Editor")

        # Bind the tab change event for the child notebook
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"Presets Parent Tab initialized with child tabs. Version: {current_version}. Get those presets ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        # Handles tab change events within the child notebook of the Presets tab.
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
        Handles tab change events within the child notebook of the Presets tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Presets Child Tab changed. Version: {current_version}. Time to update the display!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        # Get the currently selected tab widget
        selected_child_tab_id = self.child_notebook.select()
        selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)

        # If the selected child tab has an _on_tab_selected method, call it
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
            debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_name()}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Active child tab {selected_child_tab_widget.winfo_name()} has no _on_tab_selected method. Skipping update.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)

    def _on_parent_tab_selected(self, event):
        # Function Description: Handles the event when the Presets parent tab is selected in the main notebook.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the tab selection.
        #
        # Process of this function:
        #   1. Logs a debug message indicating the Presets parent tab has been selected.
        #   2. Calls the `_print_presets_ascii` function to display the Presets-specific ASCII art in the console.
        #   3. Ensures that if there's an active child tab, its `_on_tab_selected` method is also called to refresh its state.
        #
        # Outputs of this function:
        #   None. Displays ASCII art and potentially refreshes the active child tab.
        #
        # (2025-08-03) Change: Initial creation to display ASCII art when the parent tab is selected.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Presets Parent Tab selected. Version: {current_version}. Time to load up some settings! 💾",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function,
                    special=True)


        # Also ensure the currently visible child tab gets its _on_tab_selected called
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
                debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_name()}.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log(f"Active child tab {selected_child_tab_widget.winfo_name()} has no _on_tab_selected method. What the hell?!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
