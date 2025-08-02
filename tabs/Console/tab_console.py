# tabs/Console/tab_console.py
#
# This file defines the ConsoleTab, a Tkinter Frame that provides a centralized
# display for application console messages and debug logs, along with controls
# for managing logging destinations (terminal, GUI, file) and verbosity.
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
# Version 20250802.0070.1 (Initial creation of ConsoleTab with logging controls.)

current_version = "20250802.0070.1"

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os

from src.debug_logic import debug_log, set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode, set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode
from src.console_logic import console_log, set_gui_console_redirector
from src.gui_elements import TextRedirector # For redirecting console output

class ConsoleTab(ttk.Frame):
    """
    A Tkinter Frame that serves as the application's console and debug control center.
    It displays log messages and provides checkboxes to control logging behavior.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        """
        Initializes the ConsoleTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state and Tkinter variables.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Initializing ConsoleTab...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance

        self._create_widgets()
        self._setup_logging_redirectors()
        self._set_initial_checkbox_states()


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Console tab.
        This includes the scrolled text area for the console output and
        the logging control checkboxes.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Creating ConsoleTab widgets.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Configure grid for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Console text area
        self.grid_rowconfigure(1, weight=0) # Checkboxes frame

        # --- Console Text Area ---
        console_frame = ttk.LabelFrame(self, text="Application Console", padding=(5,5,5,5), style='Dark.TLabelframe')
        console_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        self.console_text = scrolledtext.ScrolledText(console_frame, wrap="word", bg="#2b2b2b", fg="#cccccc", insertbackground="white", state=tk.DISABLED)
        self.console_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        # Store a reference to the console_text widget in app_instance for redirection
        self.app_instance.console_text = self.console_text


        # --- Checkboxes Frame ---
        checkbox_frame = ttk.Frame(self, padding=(5,5,5,5), style='Dark.TFrame')
        checkbox_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Configure columns for 4-column layout
        for i in range(4):
            checkbox_frame.grid_columnconfigure(i, weight=1)

        # Checkboxes (using app_instance's Tkinter variables for persistence)
        # Row 0
        self.debug_to_terminal_checkbox = ttk.Checkbutton(checkbox_frame, text="Debug to Terminal",
                                                           variable=self.app_instance.debug_to_terminal_var,
                                                           command=self._on_debug_to_terminal_change, style='TCheckbutton')
        self.debug_to_terminal_checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.debug_to_application_checkbox = ttk.Checkbutton(checkbox_frame, text="Debug to Application",
                                                              variable=self.app_instance.general_debug_enabled_var, # This controls debug_log to GUI
                                                              command=self._on_debug_to_application_change, style='TCheckbutton')
        self.debug_to_application_checkbox.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        self.debug_to_file_checkbox = ttk.Checkbutton(checkbox_frame, text="Debug to File",
                                                       variable=self.app_instance.debug_to_file_var,
                                                       command=self._on_debug_to_file_change, style='TCheckbutton')
        self.debug_to_file_checkbox.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # Row 1
        self.include_visa_checkbox = ttk.Checkbutton(checkbox_frame, text="Include VISA",
                                                      variable=self.app_instance.log_visa_commands_enabled_var,
                                                      command=self._on_include_visa_change, style='TCheckbutton')
        self.include_visa_checkbox.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.include_console_messages_checkbox = ttk.Checkbutton(checkbox_frame, text="Include Console Messages to Debug File",
                                                                 variable=self.app_instance.include_console_messages_to_debug_file_var,
                                                                 command=self._on_include_console_messages_change, style='TCheckbutton')
        self.include_console_messages_checkbox.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="w") # Span across remaining columns


    def _setup_logging_redirectors(self):
        """
        Sets up the TextRedirector for the GUI console using the console_text widget.
        This ensures all console_log messages appear in this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Setting up logging redirectors for ConsoleTab.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Redirect console_log output to this Text widget
        set_gui_console_redirector(TextRedirector(self.console_text, "stdout"))
        # Debug_log also needs to know where to send its GUI output (controlled by DEBUG_TO_TERMINAL)
        # It already uses _gui_console_stdout_redirector, which is now set.
        
        # Initial message to confirm console is active
        console_log("Application Console is ready.", function=current_function)


    def _set_initial_checkbox_states(self):
        """
        Ensures the checkboxes reflect the current state of the Tkinter variables
        which are loaded from config.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Setting initial checkbox states.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        # These are already bound to the Tkinter variables, so their state will
        # automatically reflect the variable's value. We just need to ensure
        # the underlying debug_logic flags are set correctly on startup.
        set_debug_mode(self.app_instance.general_debug_enabled_var.get())
        set_log_visa_commands_mode(self.app_instance.log_visa_commands_enabled_var.get())
        set_debug_to_terminal_mode(self.app_instance.debug_to_terminal_var.get())
        
        # For debug to file, we need the path
        debug_file_path = self.app_instance.DEBUG_COMMANDS_FILE_PATH
        set_debug_to_file_mode(self.app_instance.debug_to_file_var.get(), debug_file_path)
        set_include_console_messages_to_debug_file_mode(self.app_instance.include_console_messages_to_debug_file_var.get())

        # Update the state of the "Debug to Application" checkbox based on "Debug to Terminal"
        # If "Debug to Terminal" is checked, "Debug to Application" should be disabled and unchecked.
        # Otherwise, it should be enabled and reflect general_debug_enabled_var.
        self._update_debug_to_application_checkbox_state()


    def _update_debug_to_application_checkbox_state(self):
        """
        Updates the state of the "Debug to Application" checkbox based on
        the "Debug to Terminal" checkbox.
        """
        if self.app_instance.debug_to_terminal_var.get():
            self.debug_to_application_checkbox.config(state=tk.DISABLED)
            # When debug to terminal is ON, debug to app is effectively OFF for debug_log
            # Set general_debug_enabled_var to False if it's currently True and debug to terminal is ON
            # This ensures consistency without directly unchecking the box if the user had it checked.
            if self.app_instance.general_debug_enabled_var.get():
                self.app_instance.general_debug_enabled_var.set(False)
                set_debug_mode(False) # Ensure the actual debug mode is off for GUI output
        else:
            self.debug_to_application_checkbox.config(state=tk.NORMAL)
            # When debug to terminal is OFF, debug to app state is controlled by general_debug_enabled_var
            set_debug_mode(self.app_instance.general_debug_enabled_var.get())


    def _on_debug_to_terminal_change(self):
        """Callback for Debug to Terminal checkbox."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        is_checked = self.app_instance.debug_to_terminal_var.get()
        set_debug_to_terminal_mode(is_checked)
        debug_log(f"Debug to Terminal checkbox changed to: {is_checked}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self._update_debug_to_application_checkbox_state() # Update related checkbox


    def _on_debug_to_application_change(self):
        """Callback for Debug to Application checkbox."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        is_checked = self.app_instance.general_debug_enabled_var.get()
        set_debug_mode(is_checked)
        debug_log(f"Debug to Application checkbox changed to: {is_checked}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _on_debug_to_file_change(self):
        """Callback for Debug to File checkbox."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        is_checked = self.app_instance.debug_to_file_var.get()
        debug_file_path = self.app_instance.DEBUG_COMMANDS_FILE_PATH
        set_debug_to_file_mode(is_checked, debug_file_path)
        debug_log(f"Debug to File checkbox changed to: {is_checked}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _on_include_visa_change(self):
        """Callback for Include VISA checkbox."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        is_checked = self.app_instance.log_visa_commands_enabled_var.get()
        set_log_visa_commands_mode(is_checked)
        debug_log(f"Include VISA checkbox changed to: {is_checked}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _on_include_console_messages_change(self):
        """Callback for Include Console Messages to Debug File checkbox."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        is_checked = self.app_instance.include_console_messages_to_debug_file_var.get()
        set_include_console_messages_to_debug_file_mode(is_checked)
        debug_log(f"Include Console Messages to Debug File checkbox changed to: {is_checked}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        console_log("ConsoleTab selected. Ready for action!", function=current_function)
        debug_log(f"ConsoleTab selected. Refreshing initial states.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self._set_initial_checkbox_states() # Ensure states are synced on tab switch

