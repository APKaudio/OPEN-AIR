# display/display_child_debug.py
#
# This file defines the DebugTab, a Tkinter Frame that provides the application's
# debug control settings. It includes a master control button, checkboxes to manage
# various debug flags, a button to clear debug logs, a button to open the data folder,
# and two ScrolledText widgets to display the contents of the debug log files in real-time.
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
# Version 20250814.224000.1 (FIXED: The Debug toggle button's initial state is now correctly set based on the config.ini file, resolving a UI synchronization bug. All checkbox toggles now explicitly call save_config to persist changes.)

current_version = "20250814.224000.1"
current_version_hash = 20250814 * 224000 * 1

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import inspect
import os
import subprocess
import sys
import threading
import time

# Import debug_log and the specific debug control functions from debug_logic
from display.debug_logic import (
    debug_log,
    set_debug_mode, set_log_visa_commands_mode,
    set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode,
    clear_debug_log_file, set_log_truncation_mode, set_include_visa_messages_to_debug_file_mode,
    DEBUG_FILE_PATH, VISA_FILE_PATH
)
from display.console_logic import console_log
from src.settings_and_config.config_manager import save_config

class DebugTab(ttk.Frame):
    """
    A Tkinter Frame that provides the debug control settings for the application.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the DebugTab, creating a dedicated frame for debug control settings.
        # It sets up a master toggle button, checkboxes for various debug flags,
        # buttons for file management, and two ScrolledText widgets to display
        # the contents of the debug log files in real-time.
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
        self.read_log_thread = None
        self.stop_thread = threading.Event()

        self._create_widgets()
        
        debug_log(f"DebugTab initialized. The debug controls and log viewers are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges the widgets for the Debug tab.
        # This includes a master debug toggle button, checkboxes for various debug flags,
        # buttons to clear logs and open the data folder, and two ScrolledText widgets
        # to display the log file contents.
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
        self.grid_rowconfigure(2, weight=1)
        
        # --- Master Debug Control Frame ---
        master_control_frame = ttk.LabelFrame(self, text="Master Debug Control", style='Dark.TLabelframe')
        master_control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        master_control_frame.grid_columnconfigure(0, weight=1)
        
        # Master debug toggle button
        self.toggle_debug_button = ttk.Button(master_control_frame, text="Enable Debug", command=self._toggle_debug_mode, style='Blue.TButton')
        self.toggle_debug_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # NEW: Set initial state of the button based on the config variable
        if self.app_instance.general_debug_enabled_var.get():
            self.toggle_debug_button.config(text="Disable Debug", style='Red.TButton')
        else:
            self.toggle_debug_button.config(text="Enable Debug", style='Blue.TButton')


        # --- PanedWindow for resizable log display windows ---
        log_paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        log_paned_window.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Frame for Software Log
        software_log_frame = ttk.LabelFrame(log_paned_window, text="Software Debug Log")
        log_paned_window.add(software_log_frame, weight=1)
        software_log_frame.grid_columnconfigure(0, weight=1)
        software_log_frame.grid_rowconfigure(2, weight=1)

        # File logging controls for software log
        file_log_controls_frame = ttk.Frame(software_log_frame, style='Dark.TFrame')
        file_log_controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        file_log_controls_frame.grid_columnconfigure(0, weight=1)
        
        self.debug_to_file_checkbox = ttk.Checkbutton(file_log_controls_frame, text="Log to File",
                                                      variable=self.app_instance.debug_to_file_var,
                                                      command=self._toggle_debug_to_file_mode,
                                                      style='TCheckbutton')
        self.debug_to_file_checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.include_console_messages_checkbox = ttk.Checkbutton(file_log_controls_frame, text="Include Console Messages",
                                                                 variable=self.app_instance.include_console_messages_to_debug_file_var,
                                                                 command=self._toggle_include_console_messages_to_debug_file_mode,
                                                                 style='TCheckbutton')
        self.include_console_messages_checkbox.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.include_visa_messages_to_debug_file_checkbox = ttk.Checkbutton(file_log_controls_frame, text="Include VISA Messages into Debug File",
                                                                           variable=self.app_instance.include_visa_messages_to_debug_file_var,
                                                                           command=self._toggle_include_visa_messages_to_debug_file_mode,
                                                                           style='TCheckbutton')
        self.include_visa_messages_to_debug_file_checkbox.grid(row=2, column=0, padx=5, pady=2, sticky="w")


        self.log_truncation_checkbox = ttk.Checkbutton(file_log_controls_frame, text="Truncate Long Numeric Messages",
                                                       variable=self.app_instance.log_truncation_enabled_var,
                                                       command=self._toggle_log_truncation_mode,
                                                       style='TCheckbutton')
        self.log_truncation_checkbox.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        
        self.clear_debug_log_button = ttk.Button(software_log_frame, text="Clear Debug Log File",
                                                 command=self._clear_debug_log_file_action,
                                                 style='Red.TButton')
        self.clear_debug_log_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.software_log_text = scrolledtext.ScrolledText(software_log_frame, wrap="word", height=10, bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.software_log_text.grid(row=2, column=0, sticky="nsew")
        self.software_log_text.config(state=tk.DISABLED)

        # Frame for VISA Log
        visa_log_frame = ttk.LabelFrame(log_paned_window, text="VISA Commands Log")
        log_paned_window.add(visa_log_frame, weight=1)
        visa_log_frame.grid_columnconfigure(0, weight=1)
        visa_log_frame.grid_rowconfigure(1, weight=1)

        # VISA logging control
        visa_log_controls_frame = ttk.Frame(visa_log_frame, style='Dark.TFrame')
        visa_log_controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        visa_log_controls_frame.grid_columnconfigure(0, weight=1)

        self.log_visa_commands_checkbox = ttk.Checkbutton(visa_log_frame, text="Log VISA Commands",
                                                          variable=self.app_instance.log_visa_commands_enabled_var,
                                                          command=self._toggle_visa_logging_mode,
                                                          style='TCheckbutton')
        self.log_visa_commands_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.visa_log_text = scrolledtext.ScrolledText(visa_log_frame, wrap="word", height=10, bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.visa_log_text.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.visa_log_text.config(state=tk.DISABLED)

        # --- Bottom Buttons ---
        bottom_button_frame = ttk.Frame(self, style='Dark.TFrame')
        bottom_button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        bottom_button_frame.grid_columnconfigure(0, weight=1)
        
        self.open_data_folder_button = ttk.Button(bottom_button_frame, text="Open Data Folder", command=self._open_data_folder_action, style='Blue.TButton')
        self.open_data_folder_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Last Config Save Time Label
        self.last_save_time_label = ttk.Label(bottom_button_frame,
                                              textvariable=self.app_instance.last_config_save_time_var,
                                              style='Dark.TLabel.Value')
        self.last_save_time_label.grid(row=1, column=0, padx=5, pady=2, sticky="e")

        debug_log(f"DebugTab widgets created. Log viewers are a go!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_debug_mode(self):
        """Toggles the global debug mode and updates the button's appearance."""
        current_function = inspect.currentframe().f_code.co_name
        current_state = self.app_instance.general_debug_enabled_var.get()
        new_state = not current_state
        self.app_instance.general_debug_enabled_var.set(new_state)
        set_debug_mode(new_state)
        # Force a config save
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)

        if new_state:
            self.toggle_debug_button.config(text="Disable Debug", style='Red.TButton')
            console_log("Debug mode is now ENABLED. The microscope is on! 🔬", function=current_function)
        else:
            self.toggle_debug_button.config(text="Enable Debug", style='Green.TButton')
            console_log("Debug mode is now DISABLED. Back to normal. 🤫", function=current_function)
        
    def _toggle_visa_logging_mode(self):
        """Toggles the global VISA command logging based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        new_state = self.app_instance.log_visa_commands_enabled_var.get()
        set_log_visa_commands_mode(new_state)
        # Force a config save
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)

        debug_log(f"Toggling VISA logging. Current state: {new_state}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_debug_to_file_mode(self):
        """Toggles whether debug messages are written to a file."""
        current_function = inspect.currentframe().f_code.co_name
        new_state = self.app_instance.debug_to_file_var.get()
        set_debug_to_file_mode(new_state)
        # Force a config save
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)
        
        debug_log(f"Toggling debug output to file. Current state: {new_state}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_include_console_messages_to_debug_file_mode(self):
        """Toggles whether console messages are included in the debug file."""
        current_function = inspect.currentframe().f_code.co_name
        new_state = self.app_instance.include_console_messages_to_debug_file_var.get()
        set_include_console_messages_to_debug_file_mode(new_state)
        # Force a config save
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)
        
        debug_log(f"Toggling inclusion of console messages to debug file. Current state: {new_state}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_log_truncation_mode(self):
        """Toggles whether log messages are truncated."""
        current_function = inspect.currentframe().f_code.co_name
        new_state = self.app_instance.log_truncation_enabled_var.get()
        set_log_truncation_mode(new_state)
        # Force a config save
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)
        
        debug_log(f"Toggling log truncation. Current state: {new_state}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _toggle_include_visa_messages_to_debug_file_mode(self):
        """Toggles whether console messages are included in the debug file."""
        current_function = inspect.currentframe().f_code.co_name
        new_state = self.app_instance.include_visa_messages_to_debug_file_var.get()
        set_include_visa_messages_to_debug_file_mode(new_state)
        # Force a config save
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)

        debug_log(f"Toggling inclusion of VISA messages to debug file. Current state: {new_state}",
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
        
        clear_debug_log_file(DEBUG_FILE_PATH)
        clear_debug_log_file(VISA_FILE_PATH)
        
        console_log(f"Debug log files cleared. Fucking finally!", function=current_function)
        
        # Clear the display widgets immediately without waiting for the poller
        self.software_log_text.config(state=tk.NORMAL)
        self.software_log_text.delete("1.0", tk.END)
        self.software_log_text.config(state=tk.DISABLED)
        self.visa_log_text.config(state=tk.NORMAL)
        self.visa_log_text.delete("1.0", tk.END)
        self.visa_log_text.config(state=tk.DISABLED)
        
        # Reset file pointers
        self.last_software_log_size = 0
        self.last_visa_log_size = 0


    def _open_data_folder_action(self):
        """Opens the main DATA folder in the file explorer."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Opening DATA folder...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        data_path = self.app_instance.DATA_FOLDER_PATH
        if os.path.exists(data_path):
            try:
                if sys.platform == "win32":
                    os.startfile(data_path)
                elif sys.platform == "darwin": # macOS
                    subprocess.Popen(["open", data_path])
                else: # Linux
                    subprocess.Popen(["xdg-open", data_path])
                console_log(f"✅ Opened data folder: {data_path}", function=current_function)
            except Exception as e:
                console_log(f"❌ Failed to open data folder: {e}", function=current_function)
        else:
            console_log(f"❌ Data folder not found at: {data_path}", function=current_function)

    def _read_and_display_log(self, text_widget, file_path, start_pos):
        """Reads new lines from a file starting from a given position."""
        if not os.path.exists(file_path):
            return start_pos
        
        new_content = ""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(start_pos)
                new_content = f.read()
        except Exception as e:
            debug_log(f"ERROR: Failed to read from log file {file_path}: {e}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
            return start_pos

        if new_content:
            text_widget.config(state=tk.NORMAL)
            text_widget.insert(tk.END, new_content)
            text_widget.config(state=tk.DISABLED)
            text_widget.see(tk.END)
        
        return start_pos + len(new_content)

    def _check_log_files(self):
        """Checks for new content in the log files and updates the displays."""
        if self.stop_thread.is_set():
            return

        # Check for new content in the software log
        try:
            current_size = os.path.getsize(DEBUG_FILE_PATH)
            if current_size > self.last_software_log_size:
                self.last_software_log_size = self._read_and_display_log(self.software_log_text, DEBUG_FILE_PATH, self.last_software_log_size)
            elif current_size < self.last_software_log_size: # File was cleared
                self.software_log_text.config(state=tk.NORMAL)
                self.software_log_text.delete("1.0", tk.END)
                self.software_log_text.config(state=tk.DISABLED)
                self.last_software_log_size = current_size
        except FileNotFoundError:
            pass
        except Exception as e:
            debug_log(f"ERROR: An error occurred while checking software log file: {e}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)

        # Check for new content in the VISA log
        try:
            current_size = os.path.getsize(VISA_FILE_PATH)
            if current_size > self.last_visa_log_size:
                self.last_visa_log_size = self._read_and_display_log(self.visa_log_text, VISA_FILE_PATH, self.last_visa_log_size)
            elif current_size < self.last_visa_log_size: # File was cleared
                self.visa_log_text.config(state=tk.NORMAL)
                self.visa_log_text.delete("1.0", tk.END)
                self.visa_log_text.config(state=tk.DISABLED)
                self.last_visa_log_size = current_size
        except FileNotFoundError:
            pass
        except Exception as e:
            debug_log(f"ERROR: An error occurred while checking VISA log file: {e}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
        
        self.after(500, self._check_log_files)

    def _on_tab_selected(self, event):
        # This function description tells me what this function does
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
        
        # Populate initial log content and set file size pointers
        self.software_log_text.config(state=tk.NORMAL)
        self.software_log_text.delete("1.0", tk.END)
        self.visa_log_text.config(state=tk.NORMAL)
        self.visa_log_text.delete("1.0", tk.END)
        
        self.last_software_log_size = self._read_and_display_log(self.software_log_text, DEBUG_FILE_PATH, 0)
        self.last_visa_log_size = self._read_and_display_log(self.visa_log_text, VISA_FILE_PATH, 0)

        self.software_log_text.config(state=tk.DISABLED)
        self.visa_log_text.config(state=tk.DISABLED)

        # Start the polling loop for live updates
        self.after(500, self._check_log_files)
    
