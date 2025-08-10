# display/display_child_debug.py
#
# This file defines the DebugTab, a Tkinter Frame that provides the application's
# debug control settings. It includes checkboxes to manage various debug flags
# and a button to clear the debug log file. This tab is designed to be a child
# of the new TAB_DISPLAY_PARENT.
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
# Version 20250810.152700.3 (FIXED: Corrected the __init__ signature to match the new parent caller.)

current_version = "20250810.152700.3" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250810 * 152700 * 3 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Import debug_log and the specific debug control functions from debug_logic
from display.debug_logic import ( # CORRECTED: Import from src, not display
    debug_log,
    set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode,
    set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode,
    clear_debug_log_file # Import the new clear log function
)
from display.console_logic import console_log # CORRECTED: Import from src, not display

class DebugTab(ttk.Frame):
    """
    A Tkinter Frame that provides the debug control settings for the application.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the DebugTab, creating a dedicated frame for debug control settings.
        # It sets up checkboxes to manage various debug flags and a button to clear the debug log.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance
        #                          to access shared variables and methods.
        #   **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing DebugTab...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance

        self._create_widgets()
        
        debug_log(f"DebugTab initialized. The debug controls are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges the widgets for the Debug tab.
        # This includes checkboxes for various debug flags and a button to clear the debug log file.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating DebugTab widgets.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # General Debug Checkbox
        self.general_debug_checkbox = ttk.Checkbutton(self, text="Enable General Debug",
                                                      variable=self.app_instance.general_debug_enabled_var,
                                                      command=self._toggle_general_debug_mode,
                                                      style='TCheckbutton')
        self.general_debug_checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        # Log VISA Commands Checkbox
        self.log_visa_commands_checkbox = ttk.Checkbutton(self, text="Log VISA Commands",
                                                          variable=self.app_instance.log_visa_commands_enabled_var,
                                                          command=self._toggle_visa_logging_mode,
                                                          style='TCheckbutton')
        self.log_visa_commands_checkbox.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Debug to Terminal Checkbox
        self.debug_to_terminal_checkbox = ttk.Checkbutton(self, text="Debug to Terminal",
                                                          variable=self.app_instance.debug_to_terminal_var,
                                                          command=self._toggle_debug_to_terminal_mode,
                                                          style='TCheckbutton')
        self.debug_to_terminal_checkbox.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        # Debug to File Checkbox
        self.debug_to_file_checkbox = ttk.Checkbutton(self, text="Debug to File",
                                                      variable=self.app_instance.debug_to_file_var,
                                                      command=self._toggle_debug_to_file_mode,
                                                      style='TCheckbutton')
        self.debug_to_file_checkbox.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Include Console Messages in Debug File Checkbox
        self.include_console_messages_checkbox = ttk.Checkbutton(self, text="Include Console Messages in Debug File",
                                                                 variable=self.app_instance.include_console_messages_to_debug_file_var,
                                                                 command=self._toggle_include_console_messages_to_debug_file_mode,
                                                                 style='TCheckbutton')
        self.include_console_messages_checkbox.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        # Last Config Save Time Label
        self.last_save_time_label = ttk.Label(self,
                                              textvariable=self.app_instance.last_config_save_time_var,
                                              style='Dark.TLabel.Value')
        self.last_save_time_label.grid(row=2, column=1, padx=5, pady=2, sticky="e")
        
        # Clear Debug Log File Button
        self.clear_debug_log_button = ttk.Button(self, text="Clear Debug Log File",
                                                 command=self._clear_debug_log_file_action,
                                                 style='Red.TButton')
        self.clear_debug_log_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        debug_log(f"DebugTab widgets created.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_general_debug_mode(self):
        """Toggles the global debug mode based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        set_debug_mode(self.app_instance.general_debug_enabled_var.get())
        debug_log(f"Toggling general debug. Current state: {self.app_instance.general_debug_enabled_var.get()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_visa_logging_mode(self):
        """Toggles the global VISA command logging based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        set_log_visa_commands_mode(self.app_instance.log_visa_commands_enabled_var.get())
        debug_log(f"Toggling VISA logging. Current state: {self.app_instance.log_visa_commands_enabled_var.get()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_debug_to_terminal_mode(self):
        """Toggles whether debug messages go to terminal or GUI console."""
        current_function = inspect.currentframe().f_code.co_name
        set_debug_to_terminal_mode(self.app_instance.debug_to_terminal_var.get())
        debug_log(f"Toggling debug output to terminal. Current state: {self.app_instance.debug_to_terminal_var.get()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_debug_to_file_mode(self):
        """Toggles whether debug messages are written to a file."""
        current_function = inspect.currentframe().f_code.co_name
        set_debug_to_file_mode(self.app_instance.debug_to_file_var.get(), self.app_instance.DEBUG_COMMANDS_FILE_PATH)
        debug_log(f"Toggling debug output to file. Current state: {self.app_instance.debug_to_file_var.get()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_include_console_messages_to_debug_file_mode(self):
        """Toggles whether console messages are included in the debug file."""
        current_function = inspect.currentframe().f_code.co_name
        set_include_console_messages_to_debug_file_mode(self.app_instance.include_console_messages_to_debug_file_var.get())
        debug_log(f"Toggling inclusion of console messages to debug file. Current state: {self.app_instance.include_console_messages_to_debug_file_var.get()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _clear_debug_log_file_action(self):
        """Action to clear the debug log file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting to clear debug log file: {self.app_instance.DEBUG_COMMANDS_FILE_PATH}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        clear_debug_log_file(self.app_instance.DEBUG_COMMANDS_FILE_PATH)
        console_log(f"Debug log file cleared.", function=current_function)

    def _on_tab_selected(self, event):
        """
        No specific action needed for this tab on selection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"DebugTab selected. No specific refresh action needed.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
