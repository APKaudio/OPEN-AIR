# settings_and_config/vars_instrument.py
#
# This module defines and initializes Tkinter variables for instrument and
# instrument-settings configurations.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.220500.1
# NEW: Created a new file to house instrument variables.

import tkinter as tk
import inspect
import os
from display.debug_logic import debug_log
from ref.ref_program_default_values import DEFAULT_CONFIG
from ref.ref_frequency_bands import MHZ_TO_HZ

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = (20250821 * 220500 * 1)
current_file = f"{os.path.basename(__file__)}"

def setup_instrument_vars(app_instance):
    """
    Initializes all the Tkinter variables for the Instrument tab.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to set up instrument variables. 🎸",
                file=current_file,
                version=current_version,
                function=current_function)

    # --- Instrument Variables ---
    app_instance.connected_instrument_manufacturer = tk.StringVar(app_instance, value="N/A")
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="N/A")
    app_instance.connected_instrument_serial = tk.StringVar(app_instance, value="N/A")
    app_instance.connected_instrument_version = tk.StringVar(app_instance, value="N/A")
    app_instance.instrument_visa_resource_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Instrument']['visa_resource'])
    app_instance.center_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['center_freq_mhz']))
    app_instance.span_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['span_freq_mhz']))
    app_instance.start_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['start_freq_mhz']))
    app_instance.stop_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['stop_freq_mhz']))
    app_instance.rbw_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['rbw_mhz']))
    app_instance.vbw_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['vbw_mhz']))
    app_instance.vbw_auto_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['vbw_auto_on'] == 'True')
    app_instance.initiate_continuous_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['initiate_continuous_on'] == 'True')
    app_instance.ref_level_dbm_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['ref_level_dbm']))
    app_instance.preamp_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['preamp_on'] == 'True')
    app_instance.power_attenuation_db_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['power_attenuation_db']))
    app_instance.high_sensitivity_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['high_sensitivity_on'] == 'True')

    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)