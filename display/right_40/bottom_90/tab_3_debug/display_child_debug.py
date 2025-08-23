# display/display_child_debug.py
#
# This file defines the DebugTab, a Tkinter Frame that provides the application's
# debug control settings.
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
# Version 20250821.220500.1

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import inspect
import os
import subprocess
import sys
import threading
import time

from display.debug_logic import (
    debug_log,
    set_debug_mode, set_log_visa_commands_mode,
    set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode,
    clear_debug_log_file, set_log_truncation_mode, set_include_visa_messages_to_debug_file_mode,
    DEBUG_FILE_PATH, VISA_FILE_PATH
)
from display.console_logic import console_log
from settings_and_config.config_manager_save import save_program_config 

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = 20250821 * 220500 * 1

class DebugTab(ttk.Frame):
    """
    A Tkinter Frame that provides the debug control settings for the application.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
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
        
        self.software_log_lines = []
        
        self.log_filter_var = tk.StringVar(value="All")
        self.log_filter_map = {
            "All": None,
            "🐐 YAK": "🐐",
            "💾 Saves": "💾",
            "🖥️ displays": "🖥️",
            "🛠️ utilities": "🛠️"
        }

        self._create_widgets()
        
        self.app_instance.gui_debug = self.software_log_text
        
        debug_log(f"DebugTab initialized. The debug controls and log viewers are ready for action! 🛡️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating DebugTab widgets.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        master_control_frame = ttk.LabelFrame(self, text="Master Debug Control", style='Dark.TLabelframe')
        master_control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        master_control_frame.grid_columnconfigure(0, weight=1)
        
        self.toggle_debug_button = ttk.Button(master_control_frame, text="Enable Debug", command=self._toggle_debug_mode, style='Blue.TButton')
        self.toggle_debug_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        if self.app_instance.general_debug_enabled_var.get():
            self.toggle_debug_button.config(text="Disable Debug", style='Red.TButton')
        else:
            self.toggle_debug_button.config(text="Enable Debug", style='Blue.TButton')

        log_paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        log_paned_window.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        software_log_frame = ttk.LabelFrame(log_paned_window, text="Software Debug Log")
        log_paned_window.add(software_log_frame, weight=1)
        software_log_frame.grid_columnconfigure(0, weight=1)
        software_log_frame.grid_rowconfigure(3, weight=1)

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
        
        # --- DEFINITIVE FIX: Corrected variable name to use '_enabled_var' suffix ---
        self.include_visa_messages_to_debug_file_checkbox = ttk.Checkbutton(file_log_controls_frame, text="Include VISA Messages into Debug File",
                                                                              variable=self.app_instance.include_visa_messages_to_debug_file_enabled_var,
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

        filter_frame = ttk.Frame(software_log_frame)
        filter_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        filter_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Filter Log:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.log_filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.log_filter_var, state="readonly")
        self.log_filter_dropdown['values'] = list(self.log_filter_map.keys())
        self.log_filter_dropdown.current(0)
        self.log_filter_dropdown.bind("<<ComboboxSelected>>", self._filter_and_display_log)
        self.log_filter_dropdown.grid(row=0, column=1, sticky="ew")
        
        self.software_log_text = scrolledtext.ScrolledText(software_log_frame, wrap="word", height=10, bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.software_log_text.grid(row=3, column=0, sticky="nsew")
        self.software_log_text.config(state=tk.DISABLED)

        visa_log_frame = ttk.LabelFrame(log_paned_window, text="VISA Commands Log")
        log_paned_window.add(visa_log_frame, weight=1)
        visa_log_frame.grid_columnconfigure(0, weight=1)
        visa_log_frame.grid_rowconfigure(1, weight=1)

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

        bottom_button_frame = ttk.Frame(self, style='Dark.TFrame')
        bottom_button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        bottom_button_frame.grid_columnconfigure(0, weight=1)
        
        self.open_data_folder_button = ttk.Button(bottom_button_frame, text="Open Data Folder", command=self._open_data_folder_action, style='Blue.TButton')
        self.open_data_folder_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.last_save_time_label = ttk.Label(bottom_button_frame,
                                              textvariable=self.app_instance.last_config_save_time_var,
                                              style='Dark.TLabel.Value')
        self.last_save_time_label.grid(row=1, column=0, padx=5, pady=2, sticky="e")

        debug_log(f"DebugTab widgets created. Log viewers are a go! 🛡️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    
    def _filter_and_display_log(self, event=None):
        """Filters the log content based on the dropdown selection and updates the display."""
        selected_filter = self.log_filter_var.get()
        filter_emoji = self.log_filter_map.get(selected_filter)
        
        filtered_lines = []
        for line in self.software_log_lines:
            if filter_emoji is None or line.strip().startswith(filter_emoji):
                filtered_lines.append(line)
        
        self.software_log_text.config(state=tk.NORMAL)
        self.software_log_text.delete("1.0", tk.END)
        self.software_log_text.insert(tk.END, "".join(filtered_lines))
        self.software_log_text.config(state=tk.DISABLED)
        self.software_log_text.see(tk.END)

    def _toggle_debug_mode(self):
        """Toggles the global debug mode and updates the button's appearance."""
        current_state = self.app_instance.general_debug_enabled_var.get()
        new_state = not current_state
        self.app_instance.general_debug_enabled_var.set(new_state)
        set_debug_mode(new_state)
        save_program_config (config=self.app_instance.program_config)

        if new_state:
            self.toggle_debug_button.config(text="Disable Debug", style='Red.TButton')
            console_log("Debug mode is now ENABLED. The microscope is on! 🔬")
        else:
            self.toggle_debug_button.config(text="Enable Debug", style='Green.TButton')
            console_log("Debug mode is now DISABLED. Back to normal. 🤫")
        
    def _toggle_visa_logging_mode(self):
        """Toggles the global VISA command logging based on checkbox state."""
        new_state = self.app_instance.log_visa_commands_enabled_var.get()
        set_log_visa_commands_mode(new_state)
        save_program_config (config=self.app_instance.program_config)
        debug_log(f"Toggling VISA logging. Current state: {new_state}", file=f"{os.path.basename(__file__)}", version=current_version)

    def _toggle_debug_to_file_mode(self):
        """Toggles whether debug messages are written to a file."""
        new_state = self.app_instance.debug_to_file_var.get()
        set_debug_to_file_mode(new_state)
        save_program_config (config=self.app_instance.program_config)
        debug_log(f"Toggling debug output to file. Current state: {new_state}", file=f"{os.path.basename(__file__)}", version=current_version)

    def _toggle_include_console_messages_to_debug_file_mode(self):
        """Toggles whether console messages are included in the debug file."""
        new_state = self.app_instance.include_console_messages_to_debug_file_var.get()
        set_include_console_messages_to_debug_file_mode(new_state)
        save_program_config (config=self.app_instance.program_config)
        debug_log(f"Toggling inclusion of console messages to debug file. Current state: {new_state}", file=f"{os.path.basename(__file__)}", version=current_version)

    def _toggle_log_truncation_mode(self):
        """Toggles whether log messages are truncated."""
        new_state = self.app_instance.log_truncation_enabled_var.get()
        set_log_truncation_mode(new_state)
        save_program_config (config=self.app_instance.program_config)
        debug_log(f"Toggling log truncation. Current state: {new_state}", file=f"{os.path.basename(__file__)}", version=current_version)

    def _toggle_include_visa_messages_to_debug_file_mode(self):
        """Toggles whether VISA messages are included in the debug file."""
        new_state = self.app_instance.include_visa_messages_to_debug_file_enabled_var.get()
        set_include_visa_messages_to_debug_file_mode(new_state)
        save_program_config (config=self.app_instance.program_config)
        debug_log(f"Toggling inclusion of VISA messages to debug file. Current state: {new_state}", file=f"{os.path.basename(__file__)}", version=current_version)

    def _clear_debug_log_file_action(self):
        """Action to clear the debug log file."""
        debug_log(f"Attempting to clear debug log files.", file=f"{os.path.basename(__file__)}", version=current_version)
        clear_debug_log_file(DEBUG_FILE_PATH)
        clear_debug_log_file(VISA_FILE_PATH)
        console_log(f"Debug log files cleared. Fucking finally!")
        self.software_log_lines = []
        self.software_log_text.config(state=tk.NORMAL)
        self.software_log_text.delete("1.0", tk.END)
        self.software_log_text.config(state=tk.DISABLED)
        self.visa_log_text.config(state=tk.NORMAL)
        self.visa_log_text.delete("1.0", tk.END)
        self.visa_log_text.config(state=tk.DISABLED)
        self.last_software_log_size = 0
        self.last_visa_log_size = 0

    def _open_data_folder_action(self):
        """Opens the main DATA folder in the file explorer."""
        debug_log(f"Opening DATA folder...", file=f"{os.path.basename(__file__)}", version=current_version)
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'DATA')
        if os.path.exists(data_path):
            try:
                if sys.platform == "win32":
                    os.startfile(data_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", data_path])
                else:
                    subprocess.Popen(["xdg-open", data_path])
                console_log(f"✅ Opened data folder: {data_path}")
            except Exception as e:
                console_log(f"❌ Failed to open data folder: {e}")
        else:
            console_log(f"❌ Data folder not found at: {data_path}")

    def _read_new_log_content(self, file_path, start_pos):
        """Reads new lines from a file starting from a given position and returns them."""
        if not os.path.exists(file_path):
            return ""
        new_content = ""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(start_pos)
                new_content = f.read()
        except Exception as e:
            debug_log(f"ERROR: Failed to read from log file {file_path}: {e}", file=f"{os.path.basename(__file__)}", version=current_version)
            return ""
        return new_content

    def _check_log_files(self):
        """Checks for new content in the log files and updates the displays."""
        if self.stop_thread.is_set():
            return
        try:
            current_size = os.path.getsize(DEBUG_FILE_PATH)
            if current_size > self.last_software_log_size:
                new_content = self._read_new_log_content(DEBUG_FILE_PATH, self.last_software_log_size)
                if new_content:
                    self.software_log_lines.extend(new_content.splitlines(keepends=True))
                    self._filter_and_display_log()
                self.last_software_log_size = current_size
            elif current_size < self.last_software_log_size:
                self.software_log_lines = []
                self.last_software_log_size = current_size
                self._filter_and_display_log()
        except FileNotFoundError:
            pass
        except Exception as e:
            debug_log(f"ERROR: An error occurred while checking software log file: {e}", file=f"{os.path.basename(__file__)}", version=current_version)
        try:
            current_size = os.path.getsize(VISA_FILE_PATH)
            if current_size > self.last_visa_log_size:
                new_content = self._read_new_log_content(VISA_FILE_PATH, self.last_visa_log_size)
                if new_content:
                    self.visa_log_text.config(state=tk.NORMAL)
                    self.visa_log_text.insert(tk.END, new_content)
                    self.visa_log_text.config(state=tk.DISABLED)
                    self.visa_log_text.see(tk.END)
                self.last_visa_log_size = current_size
            elif current_size < self.last_visa_log_size:
                self.visa_log_text.config(state=tk.NORMAL)
                self.visa_log_text.delete("1.0", tk.END)
                self.visa_log_text.config(state=tk.DISABLED)
                self.last_visa_log_size = current_size
        except FileNotFoundError:
            pass
        except Exception as e:
            debug_log(f"ERROR: An error occurred while checking VISA log file: {e}", file=f"{os.path.basename(__file__)}", version=current_version)
        self.after(500, self._check_log_files)

    def _on_tab_selected(self, event):
        """Starts log monitoring when the tab becomes active."""
        debug_log(f"ConsoleTab selected. Initializing log monitoring.", file=f"{os.path.basename(__file__)}", version=current_version)
        try:
            with open(DEBUG_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                self.software_log_lines = f.readlines()
            self.last_software_log_size = os.path.getsize(DEBUG_FILE_PATH)
        except FileNotFoundError:
            self.software_log_lines = ["❌ Log file not found. It's an empty void of nothingness!"]
            self.last_software_log_size = 0
        try:
            with open(VISA_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                visa_content = f.read()
                self.visa_log_text.config(state=tk.NORMAL)
                self.visa_log_text.delete("1.0", tk.END)
                self.visa_log_text.insert(tk.END, visa_content)
            self.visa_log_text.config(state=tk.DISABLED)
            self.last_visa_log_size = os.path.getsize(VISA_FILE_PATH)
        except FileNotFoundError:
            self.visa_log_text.config(state=tk.NORMAL)
            self.visa_log_text.delete("1.0", tk.END)
            self.visa_log_text.insert(tk.END, "❌ VISA log file not found. It's an empty void of nothingness!")
            self.visa_log_text.config(state=tk.DISABLED)
            self.last_visa_log_size = 0
        self._filter_and_display_log()
        self.after(500, self._check_log_files)