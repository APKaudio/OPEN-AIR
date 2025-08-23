# tabs/Instrument/tab_instrument_child_settings_frequency.py
#
# This file defines the FrequencySettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's frequency settings.
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
# Version 20250821.222800.1
# FIXED: The _save_settings_handler was corrected to import and use the CONFIG_FILE_PATH
#        from config_manager.py, resolving the AttributeError.

current_version = "20250821.222800.1"
current_version_hash = 20250821 * 222800 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg
from ref.ref_scanner_setting_lists import PRESET_FREQUENCY_SPAN_MHZ
from settings_and_config.config_manager_instruments import _save_instrument_settings
from settings_and_config.config_manager_save import load_program_config, save_program_config
from ref.ref_file_paths import CONFIG_FILE_PATH # ADDED IMPORT
from ref.ref_program_default_values import DEFAULT_CONFIG


class FrequencySettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for frequency settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Initializing FrequencySettingsTab. This should be a walk in the park! 🚶‍♀️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.is_tracing = False
        self.span_buttons = {}

        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._set_default_variables()
        self._create_widgets()

    def _set_default_variables(self):
        """Initializes Tkinter variables for the widgets."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Setting default variables for FrequencySettingsTab. ⚙️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        # Tkinter variables for frequency settings, now in MHz
        self.freq_start_var = tk.DoubleVar(value=100.0)
        self.freq_stop_var = tk.DoubleVar(value=200.0)
        self.freq_center_var = tk.DoubleVar(value=150.0)
        self.freq_span_var = tk.DoubleVar(value=100.0)

        # New shared variable for the common result display
        self.freq_common_result_var = tk.StringVar(value="Result: N/A")

        # NEW: Add traces to round the variable values
        self.freq_start_var.trace_add('write', self._round_variables)
        self.freq_stop_var.trace_add('write', self._round_variables)
        self.freq_center_var.trace_add('write', self._round_variables)
        self.freq_span_var.trace_add('write', self._round_variables)
        # New trace for span button styling
        self.freq_span_var.trace_add('write', self._on_span_variable_change)


    def _round_variables(self, *args):
        """
        Callback to round the values of the DoubleVar to 3 decimal places.
        It also truncates values with more than 6 decimal places.
        """
        if self.is_tracing:
            return
        self.is_tracing = True

        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Rounding variables to 3 decimal places. A meticulous process, for sure! 🔬",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            current_start = self.freq_start_var.get()
            current_stop = self.freq_stop_var.get()
            current_center = self.freq_center_var.get()
            current_span = self.freq_span_var.get()

            # Helper function to truncate float at 6 decimal places
            def truncate_float(f):
                s = f"{f:.7f}" # Get a string representation with enough precision
                if '.' in s:
                    parts = s.split('.')
                    if len(parts[1]) > 6:
                        return float(f"{parts[0]}.{parts[1][:6]}")
                return f

            self.freq_start_var.set(round(truncate_float(current_start), 3))
            self.freq_stop_var.set(round(truncate_float(current_stop), 3))
            self.freq_center_var.set(round(truncate_float(current_center), 3))
            self.freq_span_var.set(round(truncate_float(current_span), 3))

        except Exception as e:
            console_log(message=f"❌ Error while rounding variables: {e}")
            debug_log(message=f"Rounding failed! The numbers be acting up! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
        finally:
            self.is_tracing = False

    def _create_widgets(self):
        """Creates the GUI widgets for the tab."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Creating widgets for FrequencySettingsTab. The puzzle pieces are coming together! 🧩",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # --- FREQUENCY/START-STOP Frame ---
        freq_ss_frame = ttk.Frame(self, padding=10)
        freq_ss_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        freq_ss_frame.grid_columnconfigure(0, weight=1)

        # Container for Start and Stop frames
        main_start_stop_frame = ttk.Frame(freq_ss_frame)
        main_start_stop_frame.grid(row=0, column=0, sticky="ew")
        main_start_stop_frame.grid_columnconfigure(0, weight=1)
        main_start_stop_frame.grid_columnconfigure(1, weight=1)

        # Start Frequency Frame
        start_frame = ttk.Frame(main_start_stop_frame, padding=5)
        start_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        start_frame.grid_columnconfigure(0, weight=1)
        # UPDATED: Added Label for "START"
        ttk.Label(start_frame, text="Start:").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        start_entry = ttk.Entry(start_frame, textvariable=self.freq_start_var)
        start_entry.grid(row=1, column=0, sticky="ew")
        start_entry.bind("<Return>", lambda e: self._on_freq_start_stop_beg())
        start_entry.bind("<FocusOut>", lambda e: self._on_freq_start_stop_beg())
        start_scale = ttk.Scale(start_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_start_var, style='InteractionBars.TScale')
        start_scale.grid(row=2, column=0, sticky="ew")
        start_scale.bind("<ButtonRelease-1>", lambda e: self._on_freq_start_stop_beg())

        # Stop Frequency Frame
        stop_frame = ttk.Frame(main_start_stop_frame, padding=5)
        stop_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        stop_frame.grid_columnconfigure(0, weight=1)
        # UPDATED: Added Label for "STOP"
        ttk.Label(stop_frame, text="Stop:").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        stop_entry = ttk.Entry(stop_frame, textvariable=self.freq_stop_var)
        stop_entry.grid(row=1, column=0, sticky="ew")
        stop_entry.bind("<Return>", lambda e: self._on_freq_start_stop_beg())
        stop_entry.bind("<FocusOut>", lambda e: self._on_freq_start_stop_beg())
        stop_scale = ttk.Scale(stop_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_stop_var, style='InteractionBars.TScale')
        stop_scale.grid(row=2, column=0, sticky="ew")
        stop_scale.bind("<ButtonRelease-1>", lambda e: self._on_freq_start_stop_beg())

        # --- FREQUENCY/CENTER-SPAN Frame ---
        freq_cs_frame = ttk.Frame(self, padding=10)
        freq_cs_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        freq_cs_frame.grid_columnconfigure(0, weight=1)
        freq_cs_frame.grid_columnconfigure(1, weight=1)

        # Center Frequency Slider & Entry
        ttk.Label(freq_cs_frame, text="Center Frequency:", justify=tk.RIGHT).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        center_scale = ttk.Scale(freq_cs_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_center_var, style='InteractionBars.TScale')
        center_scale.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        center_scale.bind("<ButtonRelease-1>", lambda e: self._on_freq_center_span_beg())
        center_entry = ttk.Entry(freq_cs_frame, textvariable=self.freq_center_var)
        center_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        center_entry.bind("<Return>", lambda e: self._on_freq_center_span_beg())
        center_entry.bind("<FocusOut>", lambda e: self._on_freq_center_span_beg())


        # Span Slider & Entry
        ttk.Label(freq_cs_frame, text="Span:", justify=tk.RIGHT).grid(row=2, column=0, padx=5, pady=2, sticky="e")
        span_scale = ttk.Scale(freq_cs_frame, from_=0, to=500, orient=tk.HORIZONTAL, variable=self.freq_span_var, style='InteractionBars.TScale')
        span_scale.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        span_scale.bind("<ButtonRelease-1>", lambda e: self._on_freq_center_span_beg())
        span_entry = ttk.Entry(freq_cs_frame, textvariable=self.freq_span_var)
        span_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        span_entry.bind("<Return>", lambda e: self._on_freq_center_span_beg())
        span_entry.bind("<FocusOut>", lambda e: self._on_freq_center_span_beg())


        # Span Preset Buttons Frame
        span_buttons_frame = ttk.Frame(freq_cs_frame, padding=5)
        span_buttons_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self._create_span_preset_buttons(parent_frame=span_buttons_frame)


        # --- NEW COMMON RESULT FRAME ---
        common_result_frame = ttk.Frame(self, padding=10)
        common_result_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        common_result_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(common_result_frame,
                  textvariable=self.freq_common_result_var,
                  justify=tk.LEFT
                  ).grid(row=0, column=0, padx=5, pady=2, sticky="ew")


    def _create_span_preset_buttons(self, parent_frame):
        # Creates buttons for predefined frequency spans and links them to the span variable.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(message=f"Entering {current_function} with argument: parent_frame: {parent_frame}",
                  file=current_file,
                  version=current_version,
                  function=current_function)

        try:
            for i, (label, preset) in enumerate(PRESET_FREQUENCY_SPAN_MHZ.items()):
                # Use a format string with two decimal places for better display and rely on grid for sizing.
                button_text = f"{label}\n{preset['span_mhz']:.2f} MHz"
                button = ttk.Button(parent_frame,
                                    text=button_text,
                                    command=lambda p=preset: self._on_span_preset_button_click(preset=p))
                button.grid(row=0, column=i, sticky="ew", padx=2, pady=5)
                self.span_buttons[label] = button

            parent_frame.grid_rowconfigure(0, weight=1)
            for i in range(len(PRESET_FREQUENCY_SPAN_MHZ)):
                parent_frame.grid_columnconfigure(i, weight=1)

            console_log(message="✅ Span preset buttons created successfully.", function=current_function)
        except Exception as e:
            console_log(message=f"❌ Error in {current_function}: {e}")
            debug_log(message=f"Arrr, the code be capsized! The error be: {e}",
                      file=current_file,
                      version=current_version,
                      function=current_function)


    def _on_span_preset_button_click(self, preset):
        # Handles the click event for a span preset button.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(message=f"Entering {current_function} with argument: preset: {preset}",
                  file=current_file,
                  version=current_version,
                  function=current_function)
        try:
            self.is_tracing = True
            self.freq_span_var.set(preset['span_mhz'])
            self.freq_center_var.set(preset['center_mhz']) # Also set center frequency
            self.is_tracing = False
            self._update_span_button_styles()
            self._on_freq_center_span_beg() # Trigger YakBeg after button click
            console_log(message=f"✅ Span set to {preset['span_mhz']} MHz).", function=current_function)
        except Exception as e:
            console_log(message=f"❌ Error in {current_function}: {e}")
            debug_log(message=f"Arrr, the code be capsized! The error be: {e}",
                      file=current_file,
                      version=current_version,
                      function=current_function)

    def _on_span_variable_change(self, *args):
        # A callback function for the span variable's trace.
        # It updates button styles when the variable changes.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function} with no arguments.",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        if not self.is_tracing:
            self._update_span_button_styles()
            console_log(message="✅ Span variable changed, button styles updated.", function=current_function)

    def _update_span_button_styles(self):
        # A brief, one-sentence description of the function's purpose.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(message=f"Entering {current_function} with no arguments.",
                  file=current_file,
                  version=current_version,
                  function=current_function)
        try:
            current_span_mhz = self.freq_span_var.get()
            for label, preset in PRESET_FREQUENCY_SPAN_MHZ.items():
                button = self.span_buttons.get(label)
                if button:
                    if np.isclose(current_span_mhz, preset['span_mhz']):
                        button.configure(style='Orange.TButton')
                    else:
                        button.configure(style='Blue.TButton')
            console_log(message="✅ Span button styles updated.", function=current_function)
        except Exception as e:
            console_log(message=f"❌ Error in {current_function}: {e}")
            debug_log(message=f"Arrr, the code be capsized! The error be: {e}",
                      file=current_file,
                      version=current_version,
                      function=current_function)


    def _on_freq_start_stop_beg(self):
        """
        Handles the YakBeg for FREQUENCY/START-STOP.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering function: {current_function}. Arrr, a treasure map for frequencies! 🗺️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            start_freq_mhz = self.freq_start_var.get()
            stop_freq_mhz = self.freq_stop_var.get()
            
            # UPDATED: Validation logic for Start/Stop frequencies
            if start_freq_mhz >= stop_freq_mhz:
                new_stop_mhz = start_freq_mhz + 10.0
                console_log(message=f"⚠️ Start frequency ({start_freq_mhz:.3f} MHz) is greater than or equal to stop frequency ({stop_freq_mhz:.3f} MHz). Automatically setting stop to {new_stop_mhz:.3f} MHz.")
                debug_log(message=f"The start frequency ({start_freq_mhz} MHz) is greater than or equal to the stop frequency ({stop_freq_mhz} MHz). The captain has corrected the course! 📈",
                          file=os.path.basename(__file__),
                          version=current_version,
                          function=current_function)
                self.freq_stop_var.set(value=new_stop_mhz)
                # Re-read the adjusted value for the YakBeg command
                stop_freq_mhz = self.freq_stop_var.get()
            elif stop_freq_mhz < start_freq_mhz:
                new_start_mhz = stop_freq_mhz - 10.0
                console_log(message=f"⚠️ Stop frequency ({stop_freq_mhz:.3f} MHz) is less than start frequency ({start_freq_mhz:.3f} MHz). Automatically setting start to {new_start_mhz:.3f} MHz.")
                debug_log(message=f"The stop frequency ({stop_freq_mhz} MHz) is less than the start frequency ({start_freq_mhz} MHz). The captain has corrected the course! 📉",
                          file=os.path.basename(__file__),
                          version=current_version,
                          function=current_function)
                self.freq_start_var.set(value=new_start_mhz)
                # Re-read the adjusted value for the YakBeg command
                start_freq_mhz = self.freq_start_var.get()


            # Get values in MHz and convert to Hz, ensuring no decimal points
            start_freq_hz = int(start_freq_mhz * 1e6)
            stop_freq_hz = int(stop_freq_mhz * 1e6)

            # Expect 4 values to be returned from the handler
            start_resp_hz, stop_resp_hz, span_resp_hz, center_resp_hz = handle_freq_start_stop_beg(
                app_instance=self.app_instance,
                start_freq=start_freq_hz,
                stop_freq=stop_freq_hz,
                console_print_func=self.console_print_func
            )

            if start_resp_hz is not None and stop_resp_hz is not None:
                # Convert response back to MHz for display
                start_resp_mhz = start_resp_hz / 1e6
                stop_resp_mhz = stop_resp_hz / 1e6
                span_resp_mhz = span_resp_hz / 1e6
                center_resp_mhz = center_resp_hz / 1e6
                
                # Update all variables
                self.freq_start_var.set(value=start_resp_mhz)
                self.freq_stop_var.set(value=stop_resp_mhz)
                self.freq_center_var.set(value=center_resp_mhz)
                self.freq_span_var.set(value=span_resp_mhz)
                
                # UPDATED: Format the result string to match the requested layout
                result_message = (
                    f"Center: {center_resp_mhz:.3f} MHz\n"
                    f"Span: {span_resp_mhz:.3f} MHz\n\n\n"
                    f"Start: {start_resp_mhz:.3f} MHz\n"
                    f"Stop: {stop_resp_mhz:.3f} MHz"
                )
                self.freq_common_result_var.set(value=result_message)
                self._save_settings_handler()
            else:
                self.freq_common_result_var.set(value="Result: FAILED")

        except Exception as e:
            console_log(message=f"❌ Error in {current_function}: {e}")
            debug_log(message=f"Arrr, the code be capsized! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)

    def _on_freq_center_span_beg(self):
        """
        Handles the YakBeg for FREQUENCY/CENTER-SPAN.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering function: {current_function}. Plotting a course to the center! 🧭",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            # Get values in MHz and convert to Hz, ensuring no decimal points
            center_freq_mhz = self.freq_center_var.get()
            span_freq_mhz = self.freq_span_var.get()

            center_freq_hz = int(center_freq_mhz * 1e6)
            span_freq_hz = int(span_freq_mhz * 1e6)

            # Expect 4 values to be returned from the handler
            center_resp_hz, span_resp_hz, start_resp_hz, stop_resp_hz = handle_freq_center_span_beg(
                app_instance=self.app_instance,
                center_freq=center_freq_hz,
                span_freq=span_freq_hz,
                console_print_func=self.console_print_func
            )

            if center_resp_hz is not None and span_resp_hz is not None:
                # Convert response back to MHz for display
                center_resp_mhz = center_resp_hz / 1e6
                span_resp_mhz = span_resp_hz / 1e6
                start_resp_mhz = start_resp_hz / 1e6
                stop_resp_mhz = stop_resp_hz / 1e6
                
                # Update all variables
                self.freq_center_var.set(value=center_resp_mhz)
                self.freq_span_var.set(value=span_resp_mhz)
                self.freq_start_var.set(value=start_resp_mhz)
                self.freq_stop_var.set(value=stop_resp_mhz)
                
                # UPDATED: Format the result string to match the requested layout
                result_message = (
                    f"Center: {center_resp_mhz:.3f} MHz\n"
                    f"Span: {span_resp_mhz:.3f} MHz\n\n\n"
                    f"Start: {start_resp_mhz:.3f} MHz\n"
                    f"Stop: {stop_resp_mhz:.3f} MHz"
                )
                self.freq_common_result_var.set(value=result_message)
                self._save_settings_handler()
            else:
                self.freq_common_result_var.set(value="Result: FAILED")

        except Exception as e:
            console_log(message=f"❌ Error in {current_function}: {e}")
            debug_log(message=f"Arrr, the code be capsized! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)

    def _save_settings_handler(self):
        """
        Handles saving the instrument frequency settings to the config file.
        This handler now directly loads and saves the configuration to resolve
        the AttributeError.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"⚙️ 💾 Entering {current_function}. Time to save the instrument frequency configuration! 🚀",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        try:
            # Load the configuration file
            config = load_program_config(config_file_path=CONFIG_FILE_PATH, default_config=DEFAULT_CONFIG)

            # Call the specific save function from the modular config manager
            _save_instrument_settings(
                config=config,
                app_instance=self.app_instance,
                console_print_func=self.console_print_func
            )
            # Call the main config save function to write the changes to the file
            save_program_config(
                app_instance=self.app_instance,
                config=config,
                config_file_path=CONFIG_FILE_PATH,
                console_print_func=self.console_print_func
            )
            debug_log("⚙️ ✅ Instrument frequency settings saved successfully. Mission accomplished!",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
        except Exception as e:
            debug_log(f"❌ Error saving instrument frequency settings: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            self.console_print_func(f"❌ Error saving instrument frequency settings: {e}")