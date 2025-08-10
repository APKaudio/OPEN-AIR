# display/display_child_debug.py
#
# This file defines the DebugTab, a Tkinter Frame that provides the application's
# debug control settings. It includes checkboxes to manage various debug flags,
# a button to clear the debug log file, and two ScrolledText widgets to display
# the contents of the debug log files in real-time.
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
# Version 20250810.160100.5 (UPDATED: Restructured log display to use a vertical PanedWindow for stackable and resizable log viewers.)

current_version = "20250810.160100.5"
current_version_hash = 20250810 * 160100 * 5 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os

# Import debug_log and the specific debug control functions from debug_logic
from display.debug_logic import (
    debug_log,
    set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode,
    set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode,
    clear_debug_log_file,
    DEBUG_FILE_PATH
)
from display.console_logic import console_log

class DebugTab(ttk.Frame):
    """
    A Tkinter Frame that provides the debug control settings for the application.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the DebugTab, creating a dedicated frame for debug control settings.
        # It sets up checkboxes to manage various debug flags, a button to clear the debug log,
        # and two ScrolledText widgets to display the contents of the debug log files.
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
        self.polling_id = None
        self.last_software_log_size = 0
        self.last_visa_log_size = 0

        self._create_widgets()
        
        debug_log(f"DebugTab initialized. The debug controls and log viewers are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges the widgets for the Debug tab.
        # This includes checkboxes for various debug flags, a button to clear the debug log file,
        # and two ScrolledText widgets to display the log file contents.
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
        self.grid_rowconfigure(5, weight=1)

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

        # Separator for visual distinction
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        
        # PanedWindow for resizable log display windows
        log_paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        log_paned_window.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Frame for Software Log
        software_log_frame = ttk.Frame(log_paned_window)
        log_paned_window.add(software_log_frame, weight=1)
        software_log_frame.grid_columnconfigure(0, weight=1)
        software_log_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(software_log_frame, text="Software Debug Log", style='Dark.TLabel.Value').grid(row=0, column=0, sticky="ew", pady=(0, 2))
        self.software_log_text = scrolledtext.ScrolledText(software_log_frame, wrap="word", height=10, bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.software_log_text.grid(row=1, column=0, sticky="nsew")
        self.software_log_text.config(state=tk.DISABLED)

        # Frame for VISA Log
        visa_log_frame = ttk.Frame(log_paned_window)
        log_paned_window.add(visa_log_frame, weight=1)
        visa_log_frame.grid_columnconfigure(0, weight=1)
        visa_log_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(visa_log_frame, text="VISA Commands Log", style='Dark.TLabel.Value').grid(row=0, column=0, sticky="ew", pady=(0, 2))
        self.visa_log_text = scrolledtext.ScrolledText(visa_log_frame, wrap="word", height=10, bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.visa_log_text.grid(row=1, column=0, sticky="nsew")
        self.visa_log_text.config(state=tk.DISABLED)

        debug_log(f"DebugTab widgets created. Log viewers are a go!",
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
        debug_log(f"Attempting to clear debug log files.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        # Determine log file paths based on app_instance variables
        software_log_path = os.path.join(self.app_instance.DATA_FOLDER_PATH, 'DEBUG_SOFTWARE.log')
        visa_log_path = os.path.join(self.app_instance.DATA_FOLDER_PATH, 'DEBUG_VISA_COMMANDS.log')

        clear_debug_log_file(software_log_path)
        clear_debug_log_file(visa_log_path)
        
        console_log(f"Debug log files cleared. Fucking finally!", function=current_function)
        
        # Manually clear the display widgets to ensure they update immediately
        self.software_log_text.config(state=tk.NORMAL)
        self.software_log_text.delete("1.0", tk.END)
        self.software_log_text.config(state=tk.DISABLED)
        self.visa_log_text.config(state=tk.NORMAL)
        self.visa_log_text.delete("1.0", tk.END)
        self.visa_log_text.config(state=tk.DISABLED)
        
        self.last_software_log_size = 0
        self.last_visa_log_size = 0


    def _read_and_display_log(self, text_widget, file_path):
        """Reads a file and displays its content in a scrolled text widget."""
        current_function = inspect.currentframe().f_code.co_name
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                text_widget.config(state=tk.NORMAL)
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, content)
                text_widget.config(state=tk.DISABLED)
                text_widget.see(tk.END)
        except Exception as e:
            debug_log(f"ERROR: Failed to read log file {file_path}: {e}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _check_log_files(self):
        """Checks for new content in the log files and updates the displays."""
        current_function = inspect.currentframe().f_code.co_name
        # Determine log file paths based on app_instance variables
        software_log_path = os.path.join(self.app_instance.DATA_FOLDER_PATH, 'DEBUG_SOFTWARE.log')
        visa_log_path = os.path.join(self.app_instance.DATA_FOLDER_PATH, 'DEBUG_VISA_COMMANDS.log')

        try:
            if os.path.exists(software_log_path):
                current_size = os.path.getsize(software_log_path)
                if current_size != self.last_software_log_size:
                    self.last_software_log_size = current_size
                    self._read_and_display_log(self.software_log_text, software_log_path)
            
            if os.path.exists(visa_log_path):
                current_size = os.path.getsize(visa_log_path)
                if current_size != self.last_visa_log_size:
                    self.last_visa_log_size = current_size
                    self._read_and_display_log(self.visa_log_text, visa_log_path)
        except Exception as e:
            debug_log(f"ERROR: An error occurred while checking log files: {e}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        
        self.polling_id = self.after(500, self._check_log_files)

    def _on_tab_selected(self, event):
        # This function description tells me what this function does
        # Placeholder for actions to be taken when the Debug tab is selected.
        # Starts log monitoring when the tab becomes active.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object.
        #
        # Outputs of this function
        #   None.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"DebugTab selected. Initializing log monitoring.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        software_log_path = os.path.join(self.app_instance.DATA_FOLDER_PATH, 'DEBUG_SOFTWARE.log')
        visa_log_path = os.path.join(self.app_instance.DATA_FOLDER_PATH, 'DEBUG_VISA_COMMANDS.log')
        
        self._read_and_display_log(self.software_log_text, software_log_path)
        self._read_and_display_log(self.visa_log_text, visa_log_path)
        
        self._start_log_monitoring()

    def _start_log_monitoring(self):
        """Starts the periodic check of log files."""
        current_function = inspect.currentframe().f_code.co_name
        if not self.polling_id:
            self.polling_id = self.after(500, self._check_log_files)
            debug_log(f"Log file monitoring started. �",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
    
    def _stop_log_monitoring(self):
        """Stops the periodic check of log files."""
        current_function = inspect.currentframe().f_code.co_name
        if self.polling_id:
            self.after_cancel(self.polling_id)
            self.polling_id = None
            debug_log(f"Log file monitoring stopped. Phew.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
