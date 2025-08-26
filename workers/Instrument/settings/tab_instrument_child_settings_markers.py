# tabs/Instrument/tab_instrument_child_settings_markers.py
#
# This file defines the MarkerSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's marker settings.
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
# Version 20250821.141300.1
# UPDATED: Added a new handler to save marker settings to the configuration file
#          after a successful update from the GUI.

current_version = "20250821.141300.1"
current_version_hash = 20250821 * 141300 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_marker_place_all_beg

# ADDED: Imports for the configuration manager
from settings_and_config.config_manager_marker import _save_marker_tab_settings
from settings_and_config.config_manager_save import save_program_config


class MarkerSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for marker settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing MarkerSettingsTab. This should be a walk in the park! 🚶‍♀️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func

        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._set_default_variables()
        self._create_widgets()

    def _set_default_variables(self):
        """Initializes Tkinter variables for the widgets."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting default variables for MarkerSettingsTab. ⚙️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.read_markers_all_data = tk.StringVar(self, value="N/A")
        # Set default values to match the experiment tab
        default_freqs = [111.0, 222.0, 333.0, 444.0, 555.0, 666.0]
        self.marker_freq_vars = [tk.DoubleVar(self, value=f) for f in default_freqs]
        
    def _create_widgets(self):
        """Creates the GUI widgets for the tab."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for MarkerSettingsTab. The puzzle pieces are coming together! 🧩",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        # Main container frame with padding
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill="both", expand=True)
        main_container.grid_columnconfigure(0, weight=1)
        
        # --- Marker Input Frame (top row) ---
        marker_input_frame = ttk.Frame(main_container)
        marker_input_frame.grid(row=0, column=0, pady=(0, 5), sticky="ew")
        for i in range(6):
            marker_input_frame.grid_columnconfigure(i, weight=1)
            ttk.Label(marker_input_frame, text=f"M{i+1} Freq (MHz):").grid(row=0, column=i, padx=2, pady=2)
            ttk.Entry(marker_input_frame, textvariable=self.marker_freq_vars[i], width=8).grid(row=1, column=i, padx=2, pady=2)

        # --- Action Button ---
        ttk.Button(main_container, text="YakBeg - MARKER/PLACE/ALL", command=self._on_marker_place_all_beg, style='Blue.TButton').grid(row=1, column=0, pady=5, sticky="ew")

        # --- Results Table ---
        results_frame = ttk.Frame(main_container)
        results_frame.grid(row=2, column=0, pady=(5, 0), sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        self.marker_result_table = ttk.Treeview(results_frame, columns=('Marker', 'Frequency', 'Amplitude'), show='headings', height=6)
        self.marker_result_table.heading('Marker', text='Marker')
        self.marker_result_table.heading('Frequency', text='Frequency (MHz)')
        self.marker_result_table.heading('Amplitude', text='Amplitude (dBm)')
        
        self.marker_result_table.column('Marker', width=80, stretch=tk.YES, anchor='center')
        self.marker_result_table.column('Frequency', width=120, stretch=tk.YES, anchor='center')
        self.marker_result_table.column('Amplitude', width=120, stretch=tk.YES, anchor='center')
        
        self.marker_result_table.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.marker_result_table.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.marker_result_table.configure(yscrollcommand=vsb.set)
        
        debug_log(f"Widgets for Marker Settings Tab created. The controls are ready to go! 🗺️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _on_marker_place_all_beg(self):
        """
        Handles the YakBeg - MARKER/PLACE/ALL command.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering function: {current_function}. Arrr, let's get these markers placed! 🧭",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            marker_freqs = [v.get() for v in self.marker_freq_vars]
            
            result_string = handle_marker_place_all_beg(
                app_instance=self.app_instance, 
                marker_freqs_MHz=marker_freqs,
                console_print_func=self.console_print_func
            )
            
            self.marker_result_table.delete(*self.marker_result_table.get_children())

            if result_string and result_string != "FAILED":
                y_values = result_string.split(';')

                if len(y_values) == 6:
                    for i in range(6):
                        marker_label = f"M{i+1}"
                        input_freq_MHz = self.marker_freq_vars[i].get()
                        
                        try:
                            amplitude_dBm = float(y_values[i])
                            self.marker_result_table.insert('', 'end', values=(marker_label, f"{input_freq_MHz:.3f}", f"{amplitude_dBm:.2f}"))
                        except (ValueError, IndexError):
                            self.console_print_func(f"❌ Error parsing result for {marker_label}.")
                            self.marker_result_table.insert('', 'end', values=(marker_label, f"{input_freq_MHz:.3f}", 'FAILED'))
                    self.console_print_func("✅ Marker operation successful. Results displayed in table.")
                    self._save_settings_handler()
                else:
                    self.console_print_func(f"❌ Invalid response format. Expected 6 values, got {len(y_values)}.")
                    debug_log(f"Invalid response format from instrument. Expected 6 values, got {len(y_values)}. What a pain!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
                    self.marker_result_table.insert('', 'end', values=('M1-6', 'FAILED', 'FAILED'))
            else:
                self.console_print_func("❌ Marker operation failed.")
                self.marker_result_table.insert('', 'end', values=('M1-6', 'FAILED', 'FAILED'))
                
        except Exception as e:
            self.console_print_func(f"❌ Error in {current_function}: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)

    def _save_settings_handler(self):
        """Handles saving the instrument marker settings to the config file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"⚙️ 💾 Entering {current_function}. Time to save the instrument marker settings! 📍",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            # Call the specific save function from the modular config manager
            _save_marker_tab_settings(
                config=self.app_instance.program_config,
                showtime_tab=self,
                console_print_func=self.console_print_func
            )
            # Call the main config save function to write the changes to the file
            save_program_config(
                app_instance=self.app_instance,
                config=self.app_instance.program_config,
                config_file_path=self.app_instance.config_file_path,
                console_print_func=self.console_print_func
            )
            debug_log("⚙️ ✅ Instrument marker settings saved successfully. Mission accomplished!",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
        except Exception as e:
            debug_log(f"❌ Error saving instrument marker settings: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            self.console_print_func(f"❌ Error saving instrument marker settings: {e}")