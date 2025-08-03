# tabs/Console/ConsoleTab.py
#
# This file defines the ConsoleTab, a Tkinter Frame that provides the application's
# console output area and controls for debug logging. It includes a scrolled text
# widget for displaying messages, and checkboxes to manage various debug flags,
# including a button to clear the debug log file. This tab is designed to be
# placed directly in the main application's right-hand column.
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
# Version 20250802.0157.1 (Added last config save time display field.)
# Version 20250803.0145.1 (Added clear applications console function and button.)
# Version 20250803.0148.1 (Registered _clear_applications_console_action with console_logic.set_clear_console_func.)

current_version = "20250803.0148.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 75 * 6 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import sys # For TextRedirector
import os # For os.path.basename

# Import debug_log and the specific debug control functions from debug_logic
from src.debug_logic import (
    debug_log,
    set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode,
    set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode,
    clear_debug_log_file # Import the new clear log function
)
# CORRECTED: Import console_log and set_gui_console_redirector, set_clear_console_func from src.console_logic
from src.console_logic import console_log, set_gui_console_redirector, set_clear_console_func
from src.gui_elements import TextRedirector # Import TextRedirector


class ConsoleTab(ttk.LabelFrame): # Changed to LabelFrame for title
    """
    A Tkinter LabelFrame that provides the application's console output area
    and controls for debug logging. This is intended for direct placement
    in the main application's right column.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        """
        Initializes the ConsoleTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state like Tkinter variables and file paths.
            **kwargs: Arbitrary keyword arguments for Tkinter LabelFrame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Initializing ConsoleTab...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        super().__init__(master, text="Application Console & Debug", padding="10 10 10 10", style='Dark.TLabelframe', **kwargs)
        self.app_instance = app_instance

        self._create_widgets()

        # FUCKING IMPORTANT: Set the console redirector here, after console_text is created.
        # This ensures all future print() and console_log/debug_log calls go to this widget.
        if self.app_instance.console_text: # Ensure the app_instance's console_text is set to this widget
            set_gui_console_redirector(TextRedirector(self.app_instance.console_text, "stdout"),
                                       TextRedirector(self.app_instance.console_text, "stderr"))
            console_log(f"Console output redirected to GUI. Version: {current_version}", function=current_function)
            debug_log(f"GUI console redirector set to ConsoleTab's scrolled text widget.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"ERROR: app_instance.console_text not set to ConsoleTab's widget. Console redirection failed!",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        # NEW: Register the clear console action with console_logic
        set_clear_console_func(self._clear_applications_console_action)


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Console tab.
        This includes the scrolled text area for output and debug control checkboxes.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Creating ConsoleTab widgets.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.grid_rowconfigure(0, weight=1) # Console text area
        self.grid_rowconfigure(1, weight=0) # Debug checkboxes
        self.grid_rowconfigure(2, weight=0) # Clear Applications Console button
        self.grid_rowconfigure(3, weight=0) # Clear Debug Log button
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Console ScrolledText
        # Set the app_instance's console_text reference to this widget
        self.app_instance.console_text = scrolledtext.ScrolledText(self, wrap="word", bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.app_instance.console_text.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        # The state will be managed by console_log itself when writing.


        # Debug Checkboxes Frame
        debug_checkbox_frame = ttk.Frame(self, style='Dark.TFrame')
        debug_checkbox_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        debug_checkbox_frame.grid_columnconfigure(0, weight=1)
        debug_checkbox_frame.grid_columnconfigure(1, weight=1)

        # General Debug Checkbox
        self.general_debug_checkbox = ttk.Checkbutton(debug_checkbox_frame, text="Enable General Debug",
                                                      variable=self.app_instance.general_debug_enabled_var,
                                                      command=self._toggle_general_debug_mode,
                                                      style='TCheckbutton')
        self.general_debug_checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        # Log VISA Commands Checkbox
        self.log_visa_commands_checkbox = ttk.Checkbutton(debug_checkbox_frame, text="Log VISA Commands",
                                                          variable=self.app_instance.log_visa_commands_enabled_var,
                                                          command=self._toggle_visa_logging_mode,
                                                          style='TCheckbutton')
        self.log_visa_commands_checkbox.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Debug to Terminal Checkbox
        self.debug_to_terminal_checkbox = ttk.Checkbutton(debug_checkbox_frame, text="Debug to Terminal",
                                                          variable=self.app_instance.debug_to_terminal_var,
                                                          command=self._toggle_debug_to_terminal_mode,
                                                          style='TCheckbutton')
        self.debug_to_terminal_checkbox.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        # Debug to File Checkbox
        self.debug_to_file_checkbox = ttk.Checkbutton(debug_checkbox_frame, text="Debug to File",
                                                      variable=self.app_instance.debug_to_file_var,
                                                      command=self._toggle_debug_to_file_mode,
                                                      style='TCheckbutton')
        self.debug_to_file_checkbox.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Include Console Messages in Debug File Checkbox
        self.include_console_messages_checkbox = ttk.Checkbutton(debug_checkbox_frame, text="Include Console Messages in Debug File",
                                                                 variable=self.app_instance.include_console_messages_to_debug_file_var,
                                                                 command=self._toggle_include_console_messages_to_debug_file_mode,
                                                                 style='TCheckbutton')
        self.include_console_messages_checkbox.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        # NEW: Last Config Save Time Label
        self.last_save_time_label = ttk.Label(debug_checkbox_frame,
                                              textvariable=self.app_instance.last_config_save_time_var,
                                              style='Dark.TLabel.Value') # Using the new style for value labels
        self.last_save_time_label.grid(row=2, column=1, padx=5, pady=2, sticky="e") # Placed beside the checkbox


        # NEW: Clear Applications Console Button
        self.clear_applications_console_button = ttk.Button(self, text="Clear Applications Console",
                                                            command=self._clear_applications_console_action,
                                                            style='Red.TButton')
        self.clear_applications_console_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        # Clear Debug Log File Button (moved to row 3)
        self.clear_debug_log_button = ttk.Button(self, text="Clear Debug Log File",
                                                 command=self._clear_debug_log_file_action,
                                                 style='Red.TButton')
        self.clear_debug_log_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        debug_log(f"ConsoleTab widgets created.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _toggle_general_debug_mode(self):
        """Toggles the global debug mode based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        # The console_log inside set_debug_mode will handle printing to GUI
        set_debug_mode(self.app_instance.general_debug_enabled_var.get())
        debug_log(f"Toggling general debug. Current state: {self.app_instance.general_debug_enabled_var.get()}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _toggle_visa_logging_mode(self):
        """Toggles the global VISA command logging based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        set_log_visa_commands_mode(self.app_instance.log_visa_commands_enabled_var.get())
        debug_log(f"Toggling VISA logging. Current state: {self.app_instance.log_visa_commands_enabled_var.get()}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _toggle_debug_to_terminal_mode(self):
        """Toggles whether debug messages go to terminal or GUI console."""
        current_function = inspect.currentframe().f_code.co_name
        set_debug_to_terminal_mode(self.app_instance.debug_to_terminal_var.get())
        debug_log(f"Toggling debug output to terminal. Current state: {self.app_instance.debug_to_terminal_var.get()}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _toggle_debug_to_file_mode(self):
        """Toggles whether debug messages are written to a file."""
        current_function = inspect.currentframe().f_code.co_name
        set_debug_to_file_mode(self.app_instance.debug_to_file_var.get(), self.app_instance.DEBUG_COMMANDS_FILE_PATH)
        debug_log(f"Toggling debug output to file. Current state: {self.app_instance.debug_to_file_var.get()}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _toggle_include_console_messages_to_debug_file_mode(self):
        """Toggles whether console messages are included in the debug file."""
        current_function = inspect.currentframe().f_code.co_name
        set_include_console_messages_to_debug_file_mode(self.app_instance.include_console_messages_to_debug_file_var.get())
        debug_log(f"Toggling inclusion of console messages to debug file. Current state: {self.app_instance.include_console_messages_to_debug_file_var.get()}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _clear_debug_log_file_action(self):
        """Action to clear the debug log file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting to clear debug log file: {self.app_instance.DEBUG_COMMANDS_FILE_PATH}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Pass the file path from app_instance
        clear_debug_log_file(self.app_instance.DEBUG_COMMANDS_FILE_PATH)
        console_log(f"Debug log file cleared.", function=current_function) # Added console message


    def _clear_applications_console_action(self):
        """Action to clear the applications console (ScrolledText widget)."""
        current_function = inspect.currentframe().f_code.co_name
        if self.app_instance.console_text:
            self.app_instance.console_text.delete("1.0", tk.END)
            console_log(f"Applications console cleared.", function=current_function)
            debug_log(f"Applications console (ScrolledText widget) cleared.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"ERROR: Cannot clear applications console, console_text widget not found. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)


    def _on_tab_selected(self, event):
        """
        No specific action needed for this tab on selection as it's a console display.
        However, if there were any dynamic updates needed (e.g., refreshing content),
        they would go here.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"ConsoleTab selected. No specific refresh action needed.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
